# Ch.43 GPU 调度与 Kubernetes

> **本章目标**：读者学完后能为企业 Agent 平台设计 GPU 资源池与 Kubernetes 调度策略，并识别常见调度失败模式。
> **前置阅读**：[Ch.4 平台参考架构总览](../part01-overview/ch04.md) / [Ch.6 本地推理引擎](../part02-model-inference/ch06-local-inference.md)
> **估计阅读**：L1 15 min / L1+L2 45 min / 全章 90 min
> **按角色推荐阅读层**：CTO ⇒ L1+L2 ｜ 架构师 ⇒ L1+L2 ｜ 工程师 ⇒ L1+L2+L3

---

## L1 概念  〔约 30% 篇幅〕

### 43.1 GPU 调度层在企业 Agent 平台中的位置

当多事业部共用 GPU 集群时，算力争抢往往先于模型能力成为生产瓶颈。典型现象是：在线推理 Pod 排队等待 GPU，而训练或批处理 Job 仍占用大量卡资源；监控面板显示 GPU 平均利用率处于中等水平，但首 token 延迟（TTFT）已超出 SLO。此类问题的根因通常不在模型算法，而在于**算力未按业务优先级与 SLA 进行调度**。企业 Agent 平台的生产故障，在算力层往往首先表现为调度异常，而非推理质量下降。

企业 Agent 平台从试点走向规模化后，多事业部的算力诉求往往彼此冲突。以四个典型事业部为例：

- **零售**：促销高峰需支撑高并发推理，P99 首 token 需控制在毫秒至秒级，不能接受长时间排队；
- **制造**：设备诊断 Agent 需 7×24 占用 GPU 做视觉推理，要求节点亲和与故障域隔离；
- **金融**：月末批分析需长时间占用队列，但数据不出域，且不能影响日间在线查询；
- **物流**：存在可预测的短时弹性峰值，其余时段 GPU 应释放给其他队列。

多套业务、多种 SLA、单一 GPU 采购预算——若缺少统一的 **GPU 调度层**，最终往往退化为非正式的算力协调：运维人员手工 cordon 节点、驱逐 Pod，既不可审计，也不可复现。

GPU 调度层在 Part VIII 中位于最底端，回答一个精确问题：**哪张物理卡、在哪个节点、以什么隔离粒度、在什么时限内，跑哪个工作负载**。它向上为 Ch.44 模型部署提供「可预测的算力契约」——模型服务声明需要 1 张 A100-80G，调度层应保证在约定时间内绑定到满足 `nodepool=gpu-inference` 的节点，而非依赖「集群里总共有若干张卡、各团队自行协调」。它向侧面为 Ch.46 GitOps 交付提供可被声明式管理的节点池——Terraform 创建节点池，K8s 标签表达调度策略，ArgoCD 同步 DaemonSet 与 Queue 配置。

调度层**不负责**的事项须明确，以免与相邻章节重复：

- 不负责模型权重如何加载、Canary 如何切换——属于 Ch.44；
- 不负责请求走哪个模型、租户配额多少 Token——属于 Ch.45；
- 不负责 vLLM 的 KV Cache 如何优化——属于 Part II Ch.7。

![图 43-1：GPU 调度层位于 Agent 平台算力底座，向上支撑模型服务与业务 Agent](../assets/images/ch43-01.png)

图 43-1 展示 Part VIII 的「算力从哪来」。读者应看到：GPU 调度不是 vLLM 启动参数里的 `--gpu-memory-utilization`，而是平台基础设施；没有这一层，Ch.44 的 InferenceService 只是在 YAML 里写 `nvidia.com/gpu: 1`，却无法保证高峰时不被训练 Job 挤占。

| 概念 | 定义 | 与相邻概念的区别 |
|---|---|---|
| GPU 调度 | 在集群内按优先级、配额和拓扑，把 GPU 分配给 Pod/Job | 不同于 Ch.44 的模型版本管理与 Canary 流量 |
| Kubernetes（K8s） | 容器编排平台，提供 Pod、节点、命名空间等抽象 | 不同于 Slurm 的 HPC 批作业语义与 `sbatch` 文化 |
| 队列调度器 | 在 K8s 之上管理 AI 作业排队、优先级与 Gang Scheduling | 不同于默认 kube-scheduler 的「来一个 Pod 调度一个」 |
| GPU 共享 | 多工作负载复用同一张物理卡（MIG、时间片等） | 不同于 HPA 增加 Pod 副本（那是水平扩展） |

### 43.2 Agent 平台 GPU 负载分类：推理、微调、批处理与弹性扩缩

Part II Ch.6 解决「用什么引擎跑模型」——vLLM 还是 SGLang；调度层解决「跑多少、跑多久、能不能被插队、失败后谁让路」。**不先分类负载，就无法设计节点池**。架构师在设计 GPU 资源池时，若将 SLA 差异显著的负载混在同一调度域，常见后果包括：在线推理 OOM、微调 Job 饿死、FinOps 无法按业务线归因——问题往往不在卡数不足，而在**调度域划分不当**。

#### 在线推理

Agent Runtime、DataAgent 对话、客服流式回复属于在线推理。特征是：**延迟敏感、可流式、占用时长不确定但单次会话较短、不可被随意抢占**。促销或业务高峰期间，并发可从平日水平骤升数倍；若推理 Pod 与微调 Job 混池，用户会感到响应「卡住」——实质是 Pod 在等 GPU，而非模型在推理。

在线推理应绑定 `gpu-inference` 专用节点池，并配合 Ch.44 的 `minReplicas` 预热，避免 HPA 冷启动叠加 GPU 节点扩容延迟。

#### 微调与对齐

Part II Ch.9 的 LoRA 微调属于间歇性高占用：例如每季度用 8 卡跑 36–48 小时，业务通常可接受非实时排队。这类负载**怕的不是等待，怕的是 Gang 半启动**——8 个 Pod 只起了 6 个，训练 silently 错误。应进入 Volcano 管理的 `gpu-train` 队列，优先级低于在线推理，并设置 `minMember` 与队列上限。

#### 离线批推理

Embedding 重建、RAG 索引刷新、Ch.39 评测集批跑，属于高吞吐、延迟不敏感、可断点续跑。若 nightly 批 Job 与在线推理混部，可能在业务高峰仍占用带宽和 GPU DMA。应进 `gpu-batch` 队列，并限制并发 Job 数（例如同时最多 2 个批 Job）。

#### 弹性扩缩

促销、月末关账、大促复盘带来**可预测但不可精确预估**的尖峰。Kubernetes HPA 扩 Pod、Cluster Autoscaler 扩节点的链路，对 CPU 服务往往够用；对 GPU 节点，从 Pending 到新节点可调度常需 **8–25 分钟**（镜像预热、驱动初始化、模型拉取）。规模化部署中，常见做法是在可预测尖峰前提前预热 `gpu-burst` 缓冲池，而非完全依赖 Autoscaler 的滞后响应——Autoscaler 往往在尖峰**结束后**才回收节点，成本与体验均非最优。

| 负载类型 | 典型场景 | 延迟要求 | 调度优先级 | 推荐节点池 |
|---|---|---|---|---|
| 在线推理 | 客服 Agent、DataAgent 对话 | 毫秒–秒级 | 高 | `gpu-inference` |
| 微调训练 | LoRA 领域适配 | 小时–天级 | 中 | `gpu-train` |
| 离线批推理 | Embedding 重建、评测批跑 | 分钟–小时级 | 中低 | `gpu-batch` |
| 弹性尖峰 | 促销夜、月末分析 | 突发 | 可抢占缓冲 | `gpu-burst` |

![图 43-2：四类 GPU 负载的延迟、时长与优先级差异决定节点池划分](../assets/images/ch43-02.png)

图 43-2 的核心读法是：**先问负载属于哪个象限，再问进哪个池**；反过来「统一 GPU 池、各团队共用」是在用运维复杂度换取采购时的决策便利，规模化后几乎必然出现 OOM 或排队失控。

### 常见误区

**误区 1：有 Kubernetes 就等于有 GPU 调度能力**

Kubernetes 默认调度器理解 `cpu` 和 `memory`，通过 Device Plugin 也能看见 `nvidia.com/gpu`，但它**不理解** AI 作业的三类特殊需求：Gang Scheduling（N 卡必须同时就绪）、队列优先级（微调可以等但不能永远饿死）、拓扑感知（NVLink 多卡推理希望 Pod 在同一 NUMA 域）。某次 70B 四卡张量并行上线时，曾出现 4 个 Pod 里 3 个 Running、1 个 Pending 的「半启动」——vLLM 进程 hang 住，网关超时，而监控显示「GPU 还有空闲」，因为那 1 张卡散落在另一节点上，无法满足 TP=4。

**误区 2：GPU 共享等于免费翻倍**

FinOps 视角下，推理平均利用率偏低时，启用 MIG 或 Time-Slicing 看似可提升卡利用率。试点中常见失败模式是：P99 延迟显著上升，用户感知「AI 变慢」，GPU 利用率图表却「达标」。根因是**延迟敏感负载与批处理共享时间片**；共享提高的是平均值，恶化的往往是尾延迟。MIG 适合同规格、同 SLA 的多租户推理；Time-Slicing 适合 dev/test；在线推理默认独占整卡仍是多数规模化企业的书面策略。

**误区 3：Slurm 与 Kubernetes 必须二选一**

制造或仿真团队长期使用 Slurm 管理 HPC 集群，工程师熟悉 `sbatch --gres=gpu:4`；AI 平台建在 K8s，两边若各自独立采购 GPU，预算与利用率均难统一。共存模型的关键是**统一台账**：CMDB 记录物理 GPU 总量，Slurm 分区与 K8s 节点池分别占配，季度内不允许单方面超配；Slurm 管重训练与科学计算，K8s 管推理与 Agent Runtime，只有容器化成熟且需与 GitOps 同生命周期的 Job 才迁移。

---

## L2 架构  〔约 40% 篇幅〕

### 43.3 Kubernetes GPU 调度基础：Device Plugin、资源请求、节点亲和与拓扑感知

可以把 Kubernetes 调度 GPU 的过程理解为「让调度器看见卡 → 让调度器懂规则 → 让调度器放对位置」三步。许多团队只做了第一步，就在生产高峰遇到莫名 Pending。

#### Device Plugin：让 K8s「看见」GPU

NVIDIA Device Plugin（或云厂商等价物）以 DaemonSet 跑在每个 GPU 节点，向 kubelet 注册 `nvidia.com/gpu` 资源。没有它，Pod 里写再多 `limits.gpu` 也不会被调度——调度器认为节点没有 GPU。运维人员在排查某次驱动升级后的 Pending 问题时发现，全集群 `nvidia.com/gpu` 容量归零，根因是 Plugin 版本与驱动不匹配；规范做法要求先在 `gpu-staging` 池滚动验证，再动生产推理池。

Pod 声明示例：

```yaml
# 示例：推理 Pod 的 GPU 资源声明
resources:
  limits:
    nvidia.com/gpu: "1"
  requests:
    nvidia.com/gpu: "1"
```

`requests` 与 `limits` 对 GPU 通常一致——不像 CPU 可以 burst，GPU 独占时两者应相同，避免调度器 overcommit。

#### Affinity 与 Taints：让 Pod「放对」节点池

仅有 Device Plugin，批训练 Pod 仍可能落到推理节点——调度器只数卡，不懂业务。平台团队通常用 **污点（Taint）+ 容忍（Toleration）** 隔离节点池：推理节点打 `workload=online-infer:NoSchedule`，只有带对应 toleration 的推理 Pod 能进入；批处理节点打 `workload=batch:NoSchedule`。

此外：

- **nodeAffinity**：限制 `nodepool=gpu-inference`、`gpu.model=a100-80g`；
- **podAntiAffinity**：同一 InferenceService 的副本尽量不共节点，避免单节点宕机灭多副本；
- **topologySpreadConstraints**：跨可用区均匀分布，避免 AZ 故障灭半数算力。

| 标签键 | 示例值 | 含义 |
|---|---|---|
| `nodepool` | `gpu-inference` | 节点池归属 |
| `gpu.model` | `a100-80g` | 物理卡型号 |
| `gpu.topology` | `nvlink-2` | 多卡 NVLink 拓扑 |
| `workload` | `online-infer` | 允许的工作负载类型 |

![图 43-3：Pod 从资源声明到物理 GPU 绑定的五步调度链路](../assets/images/ch43-03.png)

图 43-3 的第 ③ 步只是「数卡」；第 ④ 步才是平台纪律。读者在设计集群时应问：**如果去掉 Affinity，批 Job 会不会溜进推理池？** 若会，则调度设计尚未完成。

### 43.4 队列调度器对比：Volcano、Kueue 与默认 Scheduler 的适用边界

默认 kube-scheduler 适合「一个 Pod 一颗糖」的无状态服务。AI 负载常是「一把糖必须同时发到 N 个小朋友手里，少一个都别开始吃」——这就是 Gang Scheduling。

#### 典型场景：四卡 TP 推理半启动

`llm-general-70b` 需要 TP=4。没有 Volcano PodGroup 时，scheduler 可能先绑定 3 个 Pod，第 4 个 Pending——前 3 个占着卡空转，第 4 个永远等不到连续 4 卡。Volcano 的 `PodGroup.minMember: 4` 保证：**要么 4 个一起绑定，要么 4 个一起等**。

#### Kueue：跨事业部的「GPU 预算科」

合规要求某事业部「最多占用集群 30% GPU 时间」；另一事业部促销需要临时提额。Kueue 的 `ClusterQueue` 像财务预算科目，`LocalQueue` 像各部门报销窗口——超出预算的 Job 排队，而不是抢占在线推理 Pod（抢占应靠 PriorityClass 显式设计，不应靠运气）。

| 方案 | 优势 | 代价 | 适用场景 | 本书建议 |
|---|---|---|---|---|
| 默认 kube-scheduler | 零额外组件、与 K8s 原生集成 | 无队列、无 Gang、无 AI 优先级 | 单卡推理 Pod | 在线推理 + Affinity ⭐ |
| Volcano | Gang、队列、批作业原生 | CRD 与运维学习成本 | 微调、批推理、多卡并行 | `gpu-train` / `gpu-batch` ⭐ |
| Kueue | 轻量、多租户配额 | Gang 弱于 Volcano | 跨事业部 GPU 预算 | 配额治理 ⭐ |

![图 43-4：三类调度器按工作负载特征分工，而非互相替代](../assets/images/ch43-04.png)

图 43-4 对比三类调度器的职责边界：默认 scheduler 管单 Pod 即时绑定，Volcano 管 Gang 与批队列，Kueue 管跨租户 GPU 预算。三者不是互斥关系。本书推荐的目标架构是：**推理 Pod 仍由默认 scheduler 绑定到推理池；训练/批 Job 进 Volcano Queue；所有 Job 类负载受 Kueue 配额约束**。

### 43.5 HPC 集群路径：Slurm 与 Kubernetes 的共存、迁移与分工

HPC 用户往往更熟悉 `sbatch` 而非 YAML。强行迁移往往得到双输——HPC 用户效率下降，K8s 团队承担额外支持成本。

典型的共存实践如下：

- **Slurm 保留**：CFD、长时预训练、科学计算；独立 GPU 分区；
- **K8s 主导**：推理、Agent、KServe、GitOps（Ch.46）；独立 GPU 节点池；
- **迁移判据**：Job 已容器化、需与 InferenceService 同版本节奏、需 ArgoCD 管理——才进 K8s + Volcano。

统一台账可避免「Slurm 有空闲卡、K8s 推理在排队」的资源割裂——平台周会 review 两域利用率，FinOps 按事业部分摊。

### 43.6 分布式计算框架：Ray Cluster 在 Agent 推理与数据处理中的角色

DataAgent 月末批分析常触发典型需求：对大量 parquet 分区并行跑 Python 统计，单机内存放不下。Ray 把任务拆成数百个 Task，在 K8s 提供的 Worker Pod 上跑——**对外是一个 K8s Job，对内是 Ray 的 Task 调度**。

Ray 在企业 Agent 平台中的典型用法包括：

1. **DataAgent 批分析**：Ray Data + Python，配合 Kueue 配额；
2. **RAG Embedding 离线**：Ray 并行调 Triton Embedding API；
3. **与 KServe 协作的多副本编排**（可选）：复杂 pre/post 链。

混淆 Volcano 与 Ray 是常见架构错误：Volcano 决定「4 个 GPU Pod 能否同时启动」；Ray 决定「Pod 启动后内部 200 个 Task 怎么分配 CPU/GPU」。排查 Pending 看 Volcano；排查 Task 慢看 Ray Dashboard。

![图 43-5：K8s 供给节点与 Pod 边界，Ray 在集群内调度 Task](../assets/images/ch43-05.png)

图 43-5 把 K8s 与 Ray 的分工画成双层：上层节点池与 Volcano 队列决定 Pod 何时获得 GPU，下层 Ray Head 在 Pod 内调度 Task/Actor。Pending 查 Volcano，Task 慢查 Ray Dashboard——混查两层是常见排障误区。

### 43.7 GPU 共享与切分：MIG、Time-Slicing、vGPU 与多租户算力隔离

GPU 空闲不等于浪费——在线推理留 20% KV Cache 余量是为长上下文预留。但 **28% 平均利用率** 仍会让 FinOps 追问：能否共享？

| 方案 | 隔离强度 | 适用场景 | 主要风险 |
|---|---|---|---|
| MIG | 高（硬件切分） | 同 SLA 多推理服务 | 规格固定，切分后不可动态合并 |
| Time-Slicing | 低（时间片） | dev/test、低优先级批 | 尾延迟抖动 |
| vGPU | 中 | 虚拟桌面式多租户 | 许可与厂商锁定 |
| 独占整卡 | 最高 | 延迟敏感在线推理 | 利用率数字「不好看」 |

本书建议的书面策略：**在线推理默认独占**；dev 环境 Time-Slicing；非核心批处理在独立 A100 上用 MIG 7g，**不得与在线推理混节点**。

### 43.8 失败模式：OOM、抢占、Gang Scheduling 失败、配额耗尽与节点漂移

| 组件 | 职责 | 输入 | 输出 | 失败模式 |
|---|---|---|---|---|
| Device Plugin | 注册 GPU | 物理 GPU 状态 | 可分配量 | 驱动升级失联 |
| kube-scheduler | 单 Pod 调度 | Pod spec | Binding | 碎片化 Pending |
| Volcano | Gang + 队列 | PodGroup | 批量 Binding | minMember 永久等待 |
| Kueue | 租户配额 | ClusterQueue | 准入/排队 | 配额饿死 |
| Cluster Autoscaler | 节点扩缩 | Pending Pod | 新节点 | GPU 扩容滞后 |

接口契约（Volcano PodGroup）：

```yaml
apiVersion: scheduling.volcano.sh/v1beta1
kind: PodGroup
metadata:
  name: llm-70b-tp4
spec:
  minMember: 4
  queue: gpu-inference
  priorityClassName: online-infer-high
```

| 失败模式 | 触发条件 | 影响 | 检测方式 | 恢复策略 |
|---|---|---|---|---|
| GPU OOM | KV Cache + 权重超出显存 | Pod 重启、503 | DCGM、OOMKilled | 降 batch、量化（Ch.7）、限 max_model_len |
| Gang 永久 Pending | 空闲 GPU < minMember | 服务永不 Ready | PodGroup Unschedulable | 扩容、降 minMember、调整 TP |
| 抢占误伤 | 批 Job 抢占推理 Pod | 对话中断 | SLO 告警、Event | PriorityClass 禁止抢占在线 |
| 配额耗尽 | Kueue 达上限 | Job 无限排队 | Workload Pending | 提配额、清僵尸 Job |
| 节点漂移 | 驱动/CUDA 不一致 | 部分节点不可用 | 标签对账 | 节点池标准化滚动升级 |

![图 43-6：五类调度失败的可检测信号与恢复动作应写入 Runbook](../assets/images/ch43-06.png)

图 43-6 归纳 OOM、Gang Pending、误抢占、配额耗尽、节点漂移五类失败的检测信号与恢复动作——On-call 应能按图对号入座写入 Runbook，而非默认逐卡重启。

**取舍 1：专用节点池 vs 统一 GPU 池**

| 方案 | 优势 | 代价 | 适用场景 | 本书建议 |
|---|---|---|---|---|
| 专用节点池 | SLO 可预测、故障域清晰 | 利用率可能偏低 | SLA 差异大的多事业部 | 规模化企业推荐 ⭐ |
| 统一 GPU 池 | 采购决策简单 | 争抢、OOM | 单团队 MVP | 仅试点 |

**取舍 2：Volcano vs Kueue 作为主队列**

| 方案 | 优势 | 代价 | 适用场景 | 本书建议 |
|---|---|---|---|---|
| Volcano 为主 | Gang、AI 批作业 | 组件重 | 多卡训练/推理 | 训练/批队列 ⭐ |
| Kueue 为主 | 配额清晰 | Gang 弱 | 多租户 Job | 配额 ⭐ |
| 两者并存 | 各取所长 | 运维成本 | 规模化 | 推荐 ⭐ |

---

## L3 工程实现  〔约 30% 篇幅〕

### 43.9 工程落地：调度策略配置、资源配额、监控指标与扩缩容联动

以下配置均为生产工程示例，部署前需按实际集群参数调整。推荐的落地顺序是：**先定节点池标签与污点 → 再定推理 Pod 亲和 → 再挂 Volcano/Kueue 队列 → 最后接告警与扩缩联动**。跳过前两步直接上队列，会出现「队列里 Job 永远 Pending，但难以判断是 Affinity 写错还是真没卡」。

#### 步骤 1：定义节点池与污点

推理节点必须「拒绝」批处理 Pod 误入。污点相当于节点上的「此路不通，除非你有通行证」：

```yaml
# 示例：推理专用节点污点
apiVersion: v1
kind: Node
metadata:
  name: gpu-infer-node-01
  labels:
    nodepool: gpu-inference
    gpu.model: a100-80g
    workload: online-infer
spec:
  taints:
    - key: workload
      value: online-infer
      effect: NoSchedule
```

`gpu-batch` 池使用 `workload=batch:NoSchedule`，与推理池物理隔离。FinOps 按 `nodepool` 标签分摊 GPU 小时，避免 OOM 时查不到是哪条业务线占用的卡。

#### 步骤 2：推理 Pod 容忍污点并声明亲和

Ch.44 的 vLLM InferenceService Pod 必须带 toleration 与 nodeAffinity，否则无法进入推理池：

```yaml
# 示例：vLLM 推理 Pod 调度片段
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - key: nodepool
              operator: In
              values: ["gpu-inference"]
tolerations:
  - key: workload
    operator: Equal
    value: online-infer
    effect: NoSchedule
resources:
  limits:
    nvidia.com/gpu: "1"
```

视觉诊断类 Agent 额外要求 `gpu.model=a100-80g`，避免 40G 卡加载 32B 量化模型时 KV Cache 余量不足——这是 **Affinity 表达业务约束** 的典型用法，而非过度设计。

#### 步骤 3：Kueue 租户配额

金融事业部的 ClusterQueue 限制「并发占用的 GPU 份额」，与 Volcano 队列正交：Volcano 决定 Job 启动顺序，Kueue 决定 Job 能否进入集群：

```yaml
# 示例：金融事业部 GPU 配额
apiVersion: kueue.x-k8s.io/v1beta1
kind: ClusterQueue
metadata:
  name: finance-gpu
spec:
  resourceGroups:
    - coveredResources: ["nvidia.com/gpu"]
      flavors:
        - name: default
          resources:
            - name: "nvidia.com/gpu"
              nominalQuota: 12    # 示意：并发 GPU 份额上限
```

零售促销可申请临时提额，但必须走变更单并设过期时间——否则「临时 48 小时」常变成永久配额，挤压其他事业部队列。

#### 步骤 4：监控指标、告警与扩缩容联动

| 指标 | 来源 | 告警阈值（示意） | 联动动作 |
|---|---|---|---|
| `DCGM_FI_DEV_GPU_UTIL` | DCGM Exporter | 连续 15min < 10% | FinOps 审查是否过度独占 |
| `kube_pod_status_phase{phase="Pending"}` | Prometheus | Pending > 5min | 查 Gang/配额/节点池 |
| `volcano_queue_allocated` | Volcano Metrics | 队列满 | 扩容或调优先级 |
| GPU 节点 NotReady 比例 | Node Exporter | > 10% | 节点池滚动修复 |

扩缩容联动需特别注意：**HPA 扩 Pod 副本 ≠ 一定有卡**。Pod 数从 4 变 8，若集群只剩 2 张空闲 GPU，新增 4 个 Pod 会 Pending——Ch.44 的 `minReplicas` 与 Ch.43 的节点池 `max_size` 必须联合容量规划。Cluster Autoscaler 对 GPU 节点冷启动慢（8–25 分钟），可预测尖峰前 SRE 可手动把 `gpu-burst` 从 0 预热到若干节点，并在活动开始后延迟缩回，避免「尖峰刚过就缩节点、二次尖峰再来」的抖动。

验证命令（示例）：

```bash
kubectl describe node gpu-infer-node-01 | grep -A5 Taints
kubectl get podgroup -n model-serving
kubectl get clusterqueue finance-gpu -o yaml
```

### 43.10 生产化检查清单与真实踩坑记录

**踩坑 1：Device Plugin 升级导致全集群 GPU 不可见**

- 现象：某次 NVIDIA 驱动升级后，所有推理 Pod Pending，`kubectl describe node` 显示 `nvidia.com/gpu: 0`。
- 根因：Device Plugin DaemonSet 版本与节点驱动不匹配，Plugin 启动失败但节点仍 Ready。
- 修复：节点池滚动升级——cordon → 驱逐 Pod → 升级驱动与 Plugin → `nvidia-smi` 与 Plugin 日志验证 → uncordon；**必须**先在 `gpu-staging` 池完整走一遍，再动生产推理池。
- 教训：GPU 集群的「节点 Ready」不等于「GPU 可调度」；告警应覆盖 Plugin Pod 重启次数与 `gpu_capacity` 指标。

**踩坑 2：Volcano PodGroup minMember 大于集群可用 GPU**

- 现象：70B 四卡推理服务上线后永久 Unschedulable，3 个 Pod Running、1 个 Pending，网关部分 503。
- 根因：生产池仅 3 张连续空闲卡，`minMember=4` 的 Gang 永远无法满足。
- 修复：短期启用三卡 TP + 量化（Part II Ch.7）；长期扩容 `gpu-inference`；告警规则「PodGroup Pending > 10min」直连 On-call。
- 教训：Gang 配置必须与容量规划联审；「模型能跑」在单机验证通过，不等于集群里能同时凑齐 N 卡。

**踩坑 3：Time-Slicing 与在线推理混部导致 P99 延迟恶化 3 倍**

- 现象：某生产环境促销高峰期间，客服 Agent 首 token P99 从 600ms 升至 1.8s，GPU 利用率 KPI 却「达标」。
- 根因：为节省成本在推理节点启用 GPU Time-Slicing，Embedding 批 Job 与在线推理共享时间片，尾延迟被批处理拉爆。
- 修复：在线推理改回独占整卡；批处理迁 `gpu-batch`；FinOps KPI 改为**分池利用率**，禁止用集群平均利用率考核推理 SLO。
- 教训：利用率是成本指标，不是体验指标；延迟敏感负载与批处理共享物理卡，省下的成本往往不足以覆盖一次生产事故的复盘与修复。

**生产化 checklist**

- [ ] 权限：RBAC 限制 Queue/PriorityClass 变更；仅平台 SRE 可改 Kueue ClusterQueue
- [ ] 审计：Volcano/Kueue 调度事件写入 SIEM；GPU 分配记录关联 tenant / 事业部 ID
- [ ] 成本：分节点池、分队列上报 GPU 小时账单；FinOps 月度复盘与配额对齐
- [ ] 性能：在线推理独占策略书面化；禁止 Time-Slicing 混入 `gpu-inference`
- [ ] 稳定性：PodGroup Pending、GPU NotReady、OOMKilled 三类告警与 Runbook
- [ ] 可观测性：DCGM + kube-state-metrics + Volcano/Kueue exporter 接入 Ch.38 Trace
- [ ] 灾难恢复：节点池多可用区；关键模型在两个 nodepool 可调度

---

## 本章小结

### 关键结论

1. GPU 调度层是算力底座，与 Ch.44/Ch.45 正交；事故常先表现为 Pending 与尾延迟，而非模型变差。
2. 四类负载分池：推理独占、训练/批走 Volcano、配额走 Kueue；GPU Autoscaler 慢，尖峰需预热。
3. Slurm 与 K8s 可共存，统一台账比分仓采购更重要。
4. Gang 半启动、OOM、误抢占、配额耗尽需 Runbook 与可检测信号。
5. Affinity/Taint 是「池纪律」；仅有 Device Plugin 不够。

### 上线检查清单

- [ ] 能上线吗？Plugin 健康、PriorityClass 防抢占、标签一致
- [ ] 能扩展吗？节点池与 Queue 配额可调
- [ ] 能治理吗？分租户 GPU 账单、调度审计

### 延伸阅读

- 官方文档：[Kubernetes Device Plugins](https://kubernetes.io/docs/concepts/extend-kubernetes/compute-storage-net/device-plugins/)、[Volcano](https://volcano.sh/en/docs/)、[Kueue](https://kueue.sigs.k8s.io/docs/)
- 相关章节：Part II [Ch.6](../part02-model-inference/ch06-local-inference.md)、Part VII [Ch.42](../part07-observability-eval/ch42-slo.md)、Part VIII [Ch.44](ch44.md)

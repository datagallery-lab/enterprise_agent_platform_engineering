# Ch.46 GitOps、IaC 与边缘推理

> **本章目标**：读者学完后能用 GitOps + IaC 交付完整 Agent 平台栈，并设计边缘推理的混合部署方案。
> **前置阅读**：[Ch.43 GPU 调度](ch43-gpu-kubernetes.md)–[Ch.45 LLM 网关](ch45-llm.md) / [Ch.4 平台参考架构总览](../part01-overview/ch04.md)
> **估计阅读**：L1 15 min / L1+L2 45 min / 全章 90 min
> **按角色推荐阅读层**：CTO ⇒ L1+L2 ｜ 架构师 ⇒ L1+L2 ｜ 工程师 ⇒ L1+L2+L3

---

## L1 概念  〔约 30% 篇幅〕

### 46.1 从手工部署到声明式交付：Agent 平台基础设施演进路径

Ch.43–45 分别交付算力、模型服务、网关；Ch.46 回答：**这些组件如何作为整体、可版本化、可晋升（Promotion）地交付到 dev/staging/prod，以及门店/工厂边缘如何纳入同一治理模型**。没有 GitOps，Ch.44 的 Canary 百分比、Ch.45 的 tenant 白名单、Ch.43 的节点池标签会在三个环境各自漂移——staging 测通过，prod 行为不一致，是最常见的「环境谎言」。

企业 Agent 平台通常经历三阶段演进：第一阶段，工程师 SSH 到 GPU 机器启动 vLLM；第二阶段，Kubernetes + Helm 手工 `kubectl apply`；第三阶段，Git 仓库声明期望状态，Argo CD（ArgoCD）自动同步到集群。某次生产故障中，运维人员在 prod 集群手工 `kubectl edit` 了 LiteLLM 的 ConfigMap 以排查延迟，排查结束后未改回，导致模型过载与大面积 502——更糟的是，**没有任何 PR、没有 ArgoCD Sync 记录、没有 Terraform state 变更**，复盘无法回答「是谁在何时改了什么」。手工部署的风险不仅在于慢，更在于 **不可审计、不可回滚、不可复现**。

![图 46-1：GitOps 把部署从「操作机器」变成「合并 PR」](../assets/images/ch46-01.png)

图 46-1 的第三阶段，「改生产」的唯一合法路径是 merge 到受保护分支 + prod Manual Sync——不是 kubectl 权限大小的问题，是 **组织记忆** 是否外化为 Git 历史的问题。

### 46.2 GitOps 核心机制：声明式配置、Git 为单一事实源、自动同步与漂移检测

GitOps 四原则：

1. **声明式**：集群状态由 YAML/HCL 描述，而非脚本 imperative 命令；
2. **Git 为 SSOT（Single Source of Truth，单一事实源）**：改生产 = 合并 PR；
3. **自动同步**：ArgoCD/Flux reconcile 期望 vs 实际；
4. **漂移检测**：手工 kubectl edit 会被标记 OutOfSync 并可选自动修复。

Reconcile 循环是 GitOps 的心跳：ArgoCD 每 3 分钟（默认）对比 Git commit 与集群对象，diff 非空则 Sync 或告警。prod 对 `llm-gateway-prod` Application 关闭 automated sync，但 **仍持续 diff**——OutOfSync 本身即是有人绕过 Git 的信号。

| 概念 | 定义 | 与相邻概念的区别 |
|---|---|---|
| GitOps | 用 Git 驱动部署与变更 | 不同于 CI 只负责构建镜像 |
| IaC（Infrastructure as Code，基础设施即代码） | 用代码描述基础设施 | 包含 Terraform、Helm 等 |
| Promotion | 配置从 dev→staging→prod 晋升 | 不同于镜像 tag 晋升 |
| 漂移 | 集群实际 ≠ Git 声明 | 不同于 Canary 流量比例 |

Git 仓库结构（示意，与 Ch.44/45 组件名一致）：

```text
agent-platform-gitops/
├── terraform/           # 云资源：VPC、GPU 节点池、OSS
├── helm/
│   ├── llm-gateway/     # Ch.45 LiteLLM
│   ├── model-serving/   # Ch.44 KServe InferenceService
│   └── observability/   # Ch.38
├── kustomize/
│   ├── overlays/dev
│   ├── overlays/staging
│   └── overlays/prod
└── argocd/apps/         # Application 定义
```

`helm/model-serving` 的 `values-prod.yaml` 里写 `llm-general-32b` 的 `canaryTrafficPercent` 与 OSS URI；`helm/llm-gateway` 的 `values-prod.yaml` 写四 tenant 配额与 backend 列表——**同一 PR 可原子变更「模型 + 路由」**，避免 Ch.44 已 Canary 20% 而 Ch.45 仍指向旧 Service 的窗口期。

### 常见误区

**误区 1：GitOps 等于「把 YAML 放进 Git」**

没有自动 reconcile、没有 PR 门禁、没有密钥分离，只是把 YAML 当备份。真正 GitOps 需要 ArgoCD + 分支策略 + Promotion 流程 + External Secrets。某次上线中，YAML 已提交 Git 但仍手工 kubectl apply，Git 与集群长期 OutOfSync，ArgoCD 上线后第一次 sync 误删了手工创建的 Ingress——说明 **必须先 baseline 对齐，再开启 self-heal**。

**误区 2：Terraform 和 Helm 二选一**

Terraform 擅长云资源（GPU 节点池、网络、IAM）；Helm 擅长 K8s 应用打包。两者并用：Terraform 产出 `gpu-inference` 节点池与模型 OSS 桶，Helm 部署 KServe 与 LiteLLM。用 Terraform 硬写 Deployment 模板可维护性不如 Helm；用 Helm 创建 VPC 则状态与模块复用差——**按管理对象分层，而非按工具宗教分层**。

**误区 3：边缘推理可以脱离 GitOps 独立运维**

数百家门店各手工升级 llama.cpp，版本碎片化 inevitable——不同区域模型量化版本不一致，同一导购话术回答质量不一，总部无法复现投诉。边缘也应是 GitOps 的一个 `overlay`，只是同步策略不同（见 46.6）：中心 Git 发布 manifest，门店 OTA Agent reconcile，与云端 ArgoCD 同哲学。

**误区 4：Promotion 等于镜像 tag 从 staging 推到 prod**

Agent 平台 Promotion 主要是 **Helm values 与 Terraform 变量** 的 tag 晋升——`llm-general-32b` 的 OSS URI、`canaryTrafficPercent`、LiteLLM tenant 配额同步变化。只晋升网关镜像 digest 而不晋升 model-serving values，会出现「新网关旧模型 URI」的隐性漂移；PR 模板应要求列出影响的 Application 列表。

---

## L2 架构  〔约 40% 篇幅〕

### 46.3 IaC 工具链：Terraform 资源编排、Helm Chart 打包与 ArgoCD 持续交付

Part VIII 的交付栈是四层协作：**Terraform 管云、Helm 管应用、Kustomize 管环境差异、ArgoCD 管同步**。每层都有明确 SSOT 边界，避免「一个 mega-repo 脚本打天下」。

| 工具 | 职责 | 管理对象 | 典型用法 |
|---|---|---|---|
| Terraform | 云资源 CRUD | VPC、节点池、OSS、IAM | GPU 节点池、模型桶 |
| Helm | K8s 应用模板 | Deployment、Service、CRD 值 | LiteLLM、KServe |
| Kustomize | 环境差异 patch | overlay 覆盖 | dev/staging/prod Replicas |
| ArgoCD | Git → Cluster 同步 | Application、AppProject | 分环境 Application |

Terraform state 记录 OSS 桶 ARN 与节点池 ID，Helm values 通过 External Secrets 引用 IAM Role——**云与应用的分工清晰**，On-call 看到 InferenceService 拉取 OSS 403，先查 Terraform IAM module 而非重启 Pod。

![图 46-2：Terraform 管云，Helm 管应用，ArgoCD 管 Git 到集群的 reconcile](../assets/images/ch46-02.png)

图 46-2 描述四层交付协作：Terraform 声明云资源，Helm 打包 K8s 应用，Kustomize 表达环境差异，ArgoCD 把 Git commit reconcile 到集群——PR merge 是变更进入 prod 的合法触发源。

**取舍 1：ArgoCD vs Flux**

| 方案 | 优势 | 代价 | 适用场景 | 本书建议 |
|---|---|---|---|---|
| ArgoCD | UI 直观、AppProject 成熟 | 资源占用 | 多团队、需可视化 | 规模化企业推荐 ⭐ |
| Flux | 轻量、GitOps Toolkit 原生 | UI 弱 | 纯 CLI 团队 | 可选 |

多事业部、平台 SRE 与各业务运维需看 prod diff 与 Sync History——ArgoCD UI 降低「配置变更」沟通成本。Flux 适合已深度 GitOps 且无需 UI 的团队。

**取舍 2：单仓库 vs 多仓库 GitOps**

| 方案 | 优势 | 代价 | 适用场景 | 本书建议 |
|---|---|---|---|---|
| 单仓库 monorepo | 原子变更、Promotion 简单 | 权限粗 | 平台团队集中 | 早期推荐 ⭐ |
| 多仓库 | 团队自治 | 跨库版本对齐难 | 大规模多团队 | 长期演进 |

Ch.44 Canary 与 Ch.45 路由在同一 PR 原子合并，是 monorepo 的核心收益。长期可按 `terraform/` 与 `helm/` 拆库，但 Promotion tag 必须跨库对齐——如 `prod-v1.2.0` 同时 pin 模型与网关 chart version。

### 46.4 平台交付分层：网络、存储、GPU 节点池、模型服务、网关与应用栈

交付顺序应自底向上，与 Ch.43–45 一致——上层 Application 依赖下层资源 ID 与 Secret，跳层 PR 会在 ArgoCD 报 PreSync hook 失败或更糟的「静默错误配置」。

| 层 | 组件 | 交付方式 | 依赖 |
|---|---|---|---|
| L0 网络 | VPC、子网、安全组 | Terraform | 无 |
| L1 算力 | GPU 节点池、Device Plugin | Terraform + DaemonSet | L0 |
| L2 存储 | OSS 模型桶、PVC | Terraform | L0 |
| L3 模型服务 | KServe InferenceService | Helm | L1、L2 |
| L4 网关 | LiteLLM | Helm | L3 |
| L5 平台应用 | Agent Runtime、DataAgent | Helm/Kustomize | L4 |
| L6 观测 | OTel、Langfuse | Helm | L5 |

任何一层跳过 PR 直接改集群，都会破坏上层依赖假设。典型反例：手工扩大 GPU 节点池 max_size 未改 Terraform，Cluster Autoscaler 与 FinOps 标签漂移；或手工改 LiteLLM backend 未改 Helm，ArgoCD 下次 sync **覆盖回旧配置**，On-call 以为是「幽灵故障」。

L3 与 L4 的 Helm release 顺序由 ArgoCD Application 依赖或 sync wave 控制：先 `model-serving-prod`，Ready 后再 `llm-gateway-prod`——避免网关指向尚未创建的 InferenceService。

### 46.5 环境管理：开发、预发、生产的配置差异、密钥管理与 Promotion 流程

三环境差异不是「副本数少一半」这么简单——模型权重、外部 API 策略、sync 门禁都不同，必须在 `values-*.yaml` 与 Kustomize overlay 里显式列出，而不是工程师口头约定。

| 维度 | dev | staging | prod |
|---|---|---|---|
| GPU 节点 | 1–2 卡共享 | 与 prod 同规格小集群 | 全量节点池 |
| 模型 | 7B 量化 | 与 prod 同权重 | 32B+ 生产权重 |
| 副本数 | 1 | 2 | ≥4 |
| 外部 API | 允许 | 允许（限额） | finance 禁止 |
| 同步策略 | 自动 | 自动 | **手动审批** |

密钥管理：Git 中 **永不存明文 Key**；使用 External Secrets Operator（ESO）从 Vault/KMS 注入。LiteLLM `master_key`、云端 API Key、OSS 凭证均走 Secret 引用——PR 里只有 `secretRef: vault/path/openai-key`，never 明文。finance 租户的云端 Key 在 Vault 路径级就不存在，与 Ch.45 白名单双重保险。

Promotion 流程：dev 自动 sync → staging 自动 sync + 集成测试（含 Ch.39 离线 gate 触发）→ prod 需 Platform Owner Approve + ArgoCD Manual Sync。配置 diff 必须可审：ArgoCD `app diff` 与 PR diff 一致。staging 通过后打 tag `prod-v1.2.0`，prod Application `targetRevision` 指向 tag 而非 floating `main`——**prod 不可追 moving head**。

![图 46-3：生产 Promotion 必须有人工门禁，不能依赖与 dev 相同的自动 sync](../assets/images/ch46-03.png)

图 46-3 强调 prod 与 dev/staging 的 sync 策略差异：前两环境可自动 sync，prod 必须人工审批 + Manual Sync。业务高峰前的 Promotion 窗口：提前 72 小时把 `llm-general-32b` 的 `minReplicas` 在 staging 压测后随 tag 晋升；prod Manual Sync 安排在业务低峰时段，而非高峰前数小时——避免配置变更与流量尖峰叠加。

### 46.6 边缘推理场景：门店终端、工厂边缘节点、离线/弱网与混合云拓扑

某零售企业的平台团队需为数百门店提供离线导购助手；制造工厂内网隔离，质检 Agent 需毫秒级响应；物流 handheld 在移动网络下仍需运单查询。全走云端 Ch.45 网关 + Ch.44 32B 不可行——弱网 RTT 与断连会把体验打碎。**边缘推理是部署位置的延伸**，不是另一套架构：控制平面仍在中心 GitOps，边缘是特殊 `overlay` + OTA reconcile。

边缘场景特征：

| 场景 | 约束 | 模型规模 | 同步策略 |
|---|---|---|---|
| 门店导购 | 弱网、隐私 | 3B–7B 量化 | 夜间批量 OTA |
| 工厂质检 | 内网、低延迟 | 7B 视觉语言 | 工单触发更新 |
| 物流手持 | 移动网络 | 3B 文本 | 按区域 CDN 下发 |

门店 llama.cpp 跑 7B Q4，处理「尺码、库存、退换货政策」类高频问答；复杂投诉或跨 SKU 推理 **回传** 中心 Ch.45 网关走 `llm-general-32b`——回传路径需断路器，弱网时宁可本地降级答「请稍后联系人工」，也不要无限 hang 中心链路。

![图 46-4：边缘节点是 GitOps 的特殊 overlay，不是脱离治理的孤岛](../assets/images/ch46-04.png)

图 46-4 展示中心 GitOps 与三类边缘节点（门店、工厂、物流）的混合拓扑：边缘跑 llama.cpp/ONNX/MLC 小模型，控制面仍由中心 manifest OTA 同步，不是脱离治理的孤岛。工厂质检 ONNX 模型由中心训练 pipeline 导出，manifest 与云端 KServe 模型同版本号 schema——便于投诉时对齐「边缘 7B 视觉 vs 云端 32B 复核」是否同一次发布 train。

#### 边缘与云端的请求分流决策（示意）

| 请求类型 | 边缘处理 | 回传中心条件 |
|---|---|---|
| 门店 FAQ、尺码库存 | llama.cpp 7B | 置信度低 / 用户要求人工 |
| 工厂视觉缺陷初判 | ONNX 小模型 | 边界样本 / 需 32B 复核 |
| 物流 handheld 单号查询 | MLC 3B | 复杂理赔 / 多轮对话 |
| 全集团 DataAgent NL2SQL | 不回传边缘 | 始终经 Ch.45→`llm-code-7b` |

回传路径必须带 `edge_store_id` 与 `edge_model_version` Header，中心网关计入 Observability 时区分「边缘 origin」与「纯云端」——FinOps 分摊时零售门店算力成本与中心 GPU 分开科目。

### 46.7 边缘推理引擎对比：ONNX Runtime、llama.cpp、MLC 与云端模型的协同

| 引擎 | 优势 | 代价 | 适用 | 与云端协同 |
|---|---|---|---|---|
| llama.cpp | CPU/GPU 轻量、量化成熟 | 大模型性能有限 | 门店 7B 以下 | 复杂问题回传网关 |
| ONNX Runtime | 跨框架、推理优化 | 转换链路 | 视觉质检小模型 | 中心训练→ONNX 下发 |
| MLC LLM | 移动端、NPU 加速 | 生态较新 | 手持设备 | 与云端模型分工 |
| 云端 KServe | 最强模型 | 网络依赖 | 非边缘场景 | 边缘 fallback 上游 |

混合策略：边缘处理 80% 高频简单请求；超时或低置信度 **回传** Ch.45 网关走 32B 云端——需在网络层配置断路器，避免弱网拖垮中心。物流 handheld 用 MLC 在 NPU 上跑 3B，回传仅传结构化 JSON 而非整段对话，节省带宽。

### 46.8 失败模式：配置漂移、同步冲突、回滚失败、边缘 OTA 中断与版本碎片化

| 组件 | 职责 | 输入 | 输出 | 失败模式 |
|---|---|---|---|---|
| Terraform | 云资源 desired state | HCL | 资源 ID | state 锁冲突 |
| ArgoCD | K8s sync | Git commit | Sync 状态 | OutOfSync 未处理 |
| External Secrets | 密钥注入 | Vault | K8s Secret | 轮换窗口失败 |
| Edge OTA Agent | 边缘模型更新 | 制品 manifest | 本地模型版本 | 断网半更新 |

| 失败模式 | 触发条件 | 影响 | 检测方式 | 恢复策略 |
|---|---|---|---|---|
| 配置漂移 | 手工 kubectl edit | Git 与集群不一致 | ArgoCD OutOfSync | 自动 self-heal 或 PR 修复 |
| Helm 值冲突 | 两 Chart 争同一 CRD | 部署失败 | CI helm template | Chart 依赖版本锁定 |
| Git 回滚失败 | revert 合并不完整 | prod 混合版本 | ArgoCD History | 固定 tag 重新 sync |
| 边缘 OTA 中断 | 弱网下载断点 | 边缘模型损坏 | checksum 校验 | 原子切换：下载完再 rename |
| 版本碎片化 | 门店各自升级 | 体验不一致 | 边缘版本上报 | 强制最低版本 + 批量 OTA |

漂移是 GitOps 的「免疫反应」：OutOfSync 不是噪音，是有人绕过 PR 的信号。prod 是否开启 self-heal 有争议——规模化企业 prod 默认 **不自动 heal**，先告警、人工确认再 sync，避免误 heal 掩盖正在进行的合法紧急操作（紧急操作仍应事后补 PR）。

#### Ch.43–45 组件在 Git 中的命名约定

| Git 路径 | 对应章节 | 关键 values 字段 |
|---|---|---|
| `terraform/node-pools/gpu-inference.tf` | Ch.43 | min/max_size, labels |
| `helm/model-serving/values-prod.yaml` | Ch.44 | storageUri, canaryTrafficPercent |
| `helm/llm-gateway/values-prod.yaml` | Ch.45 | model_list, tenantPolicy |
| `argocd/apps/prod/*.yaml` | Ch.46 | targetRevision tag |

命名不一致（如网关写 `general-32b` 而 KServe 名 `llm-general-32b`）会在 Promotion 时产生「能 sync、不能调用」的隐性故障——PR 模板要求 cross-check 服务名与 Ch.45 契约。

---

## L3 工程实现  〔约 30% 篇幅〕

### 46.9 工程落地：Terraform + Helm + ArgoCD 的完整交付流水线示例

完整流水线：**Terraform plan/apply 节点池与 OSS** → **Helm CI template 校验** → **ArgoCD Application 指向 tag** → **staging 集成测试** → **prod Manual Sync**。工程师本地禁止 `kubectl apply -f` 直 prod——dev 集群可例外，但须同名 overlay 回写 Git。

**Terraform GPU 节点池（片段）**

与 Ch.43 `gpu-inference` 标签、污点一致，供 Ch.44 InferenceService nodeAffinity 引用。

```hcl
# 示例：GPU 推理节点池（生产工程示例）
resource "cloud_kubernetes_node_pool" "gpu_inference" {
  cluster_id   = cloud_k8s_cluster.agent_platform.id
  name         = "gpu-inference"
  min_size     = 4
  max_size     = 20
  instance_type = "gpu.a100.80g.8xlarge"   # 示意，按云厂商调整

  labels = {
    nodepool  = "gpu-inference"
    workload  = "online-infer"
  }

  taint {
    key    = "workload"
    value  = "online-infer"
    effect = "NoSchedule"
  }
}
```

Terraform Cloud 或 OSS backend 存 state；`terraform plan` 在 PR 评论 bot 展示 diff，merge 后 CI apply staging，prod apply 需双人 approve。

**ArgoCD Application（片段）**

```yaml
# 示例：生产 LiteLLM 网关 Application
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: llm-gateway-prod
  namespace: argocd
spec:
  project: agent-platform-prod
  source:
    repoURL: https://git.example.com/agent-platform-gitops.git
    targetRevision: prod-v1.2.0          # 固定 tag，不用 floating branch
    path: helm/llm-gateway
    helm:
      valueFiles:
        - values-prod.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: llm-gateway
  syncPolicy:
    automated: null                       # prod 禁止自动 sync
    syncOptions:
      - CreateNamespace=true
```

`model-serving-prod` Application 结构类似，`values-prod.yaml` 含 `llm-general-32b` 的 `canaryTrafficPercent` 与 OSS URI——两 Application 同 tag 晋升。

**Kustomize prod overlay（片段）**

```yaml
# 示例：prod 环境提高网关副本
apiVersion: apps/v1
kind: Deployment
metadata:
  name: litellm
spec:
  replicas: 4
```

业务高峰窗口 overlay patch `replicas: 8` 与 HPA max，随单独 PR merge 后晋升 tag，而非 kubectl scale。

**边缘 llama.cpp systemd 单元（示意）**

```ini
# 示例：门店边缘推理服务
[Service]
ExecStart=/opt/llama-cpp/server -m /var/models/qwen2.5-7b-q4_k_m.gguf --port 8080
Restart=on-failure
Environment=UPSTREAM_GATEWAY=https://llm-gateway.prod.example.com
```

边缘 OTA：中心 Git 发布 `manifest.json`（model_version、sha256、url）；门店 OTA Agent 夜间下载到 `.staging`，校验通过后 atomic rename 到 `/var/models/active`——与 ArgoCD reconcile 同哲学：**先对齐期望状态，再切换流量**。

**验证命令**

```bash
terraform plan -out=tfplan          # 云资源变更预览
helm template llm-gateway ./helm/llm-gateway -f values-prod.yaml | kubectl apply --dry-run=client -f -
argocd app diff llm-gateway-prod    # 同步前 diff
```

CI 门禁：`helm template` 失败则 PR 不可 merge；`argocd app diff` 非空则 prod sync 需二次确认。staging 在 merge 后自动 sync，跑 smoke：经网关 ping 四 tenant、`llm-code-7b` NL2SQL 样例、finance 拒绝云端探测。

#### model-serving Helm 与 KServe 值文件（片段）

Ch.44 InferenceService 由 GitOps 管理，而非裸 kubectl：

```yaml
# 示例：helm/model-serving/values-prod.yaml 片段
inferenceServices:
  llm-general-32b:
    storageUri: oss://agent-platform-models/llm/qwen2.5-32b-awq/v20260301/
    minReplicas: 4
    maxReplicas: 8
    canaryTrafficPercent: 0
    nodepool: gpu-inference
  llm-code-7b:
    storageUri: oss://agent-platform-models/llm/qwen2.5-coder-7b/v20260301/
    minReplicas: 2
    maxReplicas: 4
  embed-bge-m3:
    runtime: triton
    storageUri: oss://agent-platform-models/embed/bge-m3/v20260301/
```

Promotion 时若只改 `llm-general-32b.storageUri`，同一 PR 应更新 Ch.39 离线评测记录链接，ArgoCD sync 后按 Ch.44 Runbook 调 Canary。

#### 边缘 overlay 目录结构（示意）

```text
kustomize/overlays/edge-retail-store/
├── kustomization.yaml
├── llama-cpp-config.yaml
└── ota-manifest-ref.yaml   # 指向中心 manifest tag
```

边缘不跑 ArgoCD Server，但 OTA Agent 拉取的 manifest tag 与云端 `prod-v*` 同源——版本碎片化时查中心 inventory 即可定位门店落后几个 tag。

### 46.10 生产化检查清单与真实踩坑记录

**踩坑 1：ArgoCD prod 开启 automated sync 导致未审批变更直接上线**

- 现象：工程师 merge 到 main，prod 网关配置 5 分钟内变更，业务高峰期间误关 fallback。
- 根因：Application 复制 dev 的 `automated: {}` 到 prod；main 与 prod tag 混用。
- 修复：prod 必须 `automated: null` + Manual Sync；Branch 保护 + 必需 Reviewer；prod 只追 tag。

**踩坑 2：Terraform state 未锁，两人同时 apply 搞乱节点池**

- 现象：GPU 节点池 max_size 被覆盖，Cluster Autoscaler 行为异常；Ch.44 HPA 扩 Pod 无节点。
- 根因：本地 state 文件，无 remote backend；两人 apply 不同 HCL。
- 修复：Terraform Cloud 或 OSS backend + 锁；禁止本地 apply prod；state 变更审计。

**踩坑 3：边缘 OTA 断点续传未校验 sha256，门店模型文件损坏**

- 现象：部分门店导购 Agent 输出异常，文件大小少 200MB。
- 根因：弱网中断后仍加载不完整文件；OTA Agent 未 atomic rename。
- 修复：下载到 `.staging`，sha256 校验通过后才 `mv` 到 active；启动前探针加载 tokenizer smoke test；中心 inventory 上报版本，低于 `min_version` 强制 OTA。

**生产化 checklist**

- [ ] 权限：ArgoCD AppProject RBAC；prod sync 仅 Platform Owner
- [ ] 审计：Git PR、ArgoCD Sync、Terraform apply 三联审计
- [ ] 成本：Terraform 标签分环境；GPU 节点池 autoscaling 上下限
- [ ] 性能：Helm CI `template` 校验；prod Promotion 前 staging 压测
- [ ] 稳定性：ArgoCD sync 失败告警；Terraform drift detection
- [ ] 可观测性：边缘版本 inventory 上报中心
- [ ] 灾难恢复：Git tag 固定 prod；一键 `argocd app sync --revision <tag>`

#### 三联审计字段对齐

| 系统 | 必记字段 | 用途 |
|---|---|---|
| Git PR | author, paths, tag | 谁改了什么配置 |
| ArgoCD Sync | revision, initiator, diff | 何时进集群 |
| Terraform apply | workspace, run_id, resource | 云资源变更 |

三系统 `tenant`/`environment` 标签命名与 Ch.45 一致，便于从 finance 合规审计反查「哪次 PR 放开过云端 backend」——应查不到，若查到即流程破损。

---

## 本章小结

### 关键结论

1. GitOps 把 Agent 平台交付从手工操作变成 PR 驱动的声明式 reconcile；Git 是 SSOT，ArgoCD 是执行器。
2. Terraform 管云、Helm 管应用、Kustomize 管环境差异、ArgoCD 管同步——四层分工，不可互相替代。
3. prod Promotion 必须有人工门禁；密钥永不进 Git，走 External Secrets。
4. 边缘推理是 GitOps 的特殊 overlay，需 OTA、checksum 与版本 inventory，不能成为治理盲区。
5. 失败模式集中在漂移、sync 策略误配、state 锁缺失与 OTA 半更新——应 CI 阻断 + Runbook 覆盖。

### 上线检查清单

- [ ] 能上线吗？prod 无 automated sync；Terraform remote state + 锁
- [ ] 能扩展吗？Helm values 分环境；节点池 Terraform 可扩缩
- [ ] 能治理吗？PR 审计、ArgoCD History 可回滚、边缘版本可上报

### 延伸阅读

- 官方文档：[ArgoCD 文档](https://argo-cd.readthedocs.io/)、[Terraform 文档](https://developer.hashicorp.com/terraform/docs)、[llama.cpp Server](https://github.com/ggerganov/llama.cpp/blob/master/tools/server/README.md)
- 对标产品：Flux CD、Pulumi、Rancher Fleet
- 相关章节：Part VIII [Ch.43–45](ch43-gpu-kubernetes.md)、Part IX [Ch.47 对话 UI](../part09-frontend-multimodal/ch47-ui.md)

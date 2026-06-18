# Ch.45 LLM 网关与多租户

> **本章目标**：读者学完后能设计并实现 LLM 统一网关，完成多租户路由、限流、配额与降级链路。
> **前置阅读**：[Ch.6 本地推理引擎](../part02-model-inference/ch06.md) / [Ch.44 模型部署](ch44.md) / [Ch.41 成本治理与缓存](../part07-observability-eval/ch41-cost-governance-cache.md)
> **估计阅读**：L1 15 min / L1+L2 45 min / 全章 90 min
> **按角色推荐阅读层**：CTO ⇒ L1+L2 ｜ 架构师 ⇒ L1+L2 ｜ 工程师 ⇒ L1+L2+L3

---

## L1 概念  〔约 30% 篇幅〕

### 45.1 LLM 网关在企业 Agent 平台控制平面中的位置

缺少统一入口时，多 Agent 团队各自维护 API Key、重试逻辑、模型列表和限流规则，规模化后几乎必然出现：密钥泄漏、成本失控、故障无法统一定界、合规审计无法回答「谁调用了哪个模型、走了哪条 backend」。FinOps 在月度账单中若发现云端 API 费用异常，而平台监控显示推理 QPS 平稳，常见根因是部分 Agent 绕过平台直连外部 API，或重试风暴放大 Token 消耗。

**LLM 网关（LLM Gateway）** 是 Agent 平台控制平面的统一入口：所有 Runtime、DataAgent、Console 只对接网关；网关负责路由到 Ch.44 模型服务或外部 SaaS，并叠加限流、配额、缓存、Trace 传播与降级。Ch.41 讲 Token 成本核算策略，Ch.42 讲 SLO 与熔断——**网关是这些策略的执行点**，不是替代者。Ch.43 保证 GPU 到位，Ch.44 保证模型服务 Ready，Ch.45 保证「这条请求以哪个 tenant 身份、走哪条 backend、失败时退到哪」——Runtime 只需学会一种 OpenAI 兼容调用方式。

企业 Agent 平台通常有四个事业部、十余个 Agent 应用、若干模型服务（Ch.44 的 `llm-general-32b`、`llm-code-7b` 等），以及部分云端 API 备用。网关将上述异构 backend 收敛为单一调用面。

![图 45-1：网关是模型调用的唯一入口，也是治理策略的执行面](../images/ch/ch45-01.png)

图 45-1 与 Ch.44 的边界：Ch.44 管模型副本与版本、Canary 与 Revision；Ch.45 管「哪条请求去哪个模型、以什么配额、失败时去哪」。读者不应在网关里做模型权重加载，也不应在 InferenceService 里做 tenant 配额——职责混淆会导致双份限流或双份盲区。

### 45.2 网关核心能力：统一 API、模型路由、缓存、限流、配额与成本归因

网关能力可以按「对 Agent 透明」与「对 FinOps/合规可见」两类理解。对 Agent 透明的是 OpenAI 兼容 API、流式 SSE、统一错误体；对 FinOps 可见的是 tenant 标签、Token 计量、backend 选择审计。

| 能力 | 作用 | 与 Ch.41/Ch.42 关系 |
|---|---|---|
| 统一 API | OpenAI 兼容，屏蔽后端差异 | 降低 Agent 集成成本 |
| 模型路由 | 按任务/租户/合规选 backend | 执行成本路由策略 |
| Prompt Cache | 相同前缀复用 KV（若后端支持） | 与 Ch.41 semantic cache 互补 |
| 限流 | RPM/TPM/并发连接 | 执行 Ch.42 限流 SLO |
| 配额 | 租户日/月 Token 上限 | FinOps 硬门禁 |
| 成本归因 | 请求级 model + tenant 标签 | 账单分摊 |
| Trace 传播 | 注入 trace_id 到 Ch.38 | 可观测性关联 |

网关租户划分（与 Ch.46 GitOps `values-prod.yaml`、Ch.50 安全策略一致）：

| 租户 ID | 事业部 | 默认模型 | 日 Token 配额（示意） |
|---|---|---|---|
| `retail` | 零售 | `llm-general-32b` | 50M |
| `mfg` | 制造 | `llm-code-7b` + 本地 32B | 20M |
| `finance` | 金融 | 仅本地 `llm-general-32b` | 10M |
| `logistics` | 物流 | `llm-general-32b` + 云端备用 | 30M |

零售 tenant 允许在业务高峰通过路由规则切云端备用以吸收尖峰；finance tenant 的 allowed_models 白名单只有 `llm-general-32b`，任何 `gpt-4o` 请求在网关层直接 403，而非到云端才拒绝。制造 DataAgent 的 NL2SQL 默认走 `llm-code-7b`，复杂规划仍回 `llm-general-32b`——路由由 `X-Task-Type` 与规则表决定，Agent 代码不必硬编码两套 URL。

| 概念 | 定义 | 与相邻概念的区别 |
|---|---|---|
| LLM 网关 | 统一 LLM API 入口与治理执行点 | 不同于 API Gateway 全站入口 |
| 租户 | 资源与配额隔离单元 | 不同于 K8s Namespace 本身 |
| 路由规则 | 决定 backend 的匹配逻辑 | 不同于模型服务发布（Ch.44） |
| 降级 | 主 backend 失败时的备用路径 | 不同于模型 Canary（Ch.44） |

Ch.44 的 Canary 是「同一服务名的新旧 Revision 切流」；网关降级是「主 backend 不可用时的 fallback_chain」——二者都可能改变用户看到的回答质量，但触发条件与回滚方式不同，On-call 必须分册记录。

#### 四事业部在网关层的典型流量模式

把抽象能力映射到典型业务流量，有助于设计路由与配额：

- **零售（`retail`）**：日间客服 Agent 占 TPM 主体；业务高峰配额触达 80% 预警时，路由允许切 `gpt-4o-fallback` 吸收部分溢出，但 FinOps 通常要求限时回切本地 32B。
- **制造（`mfg`）**：DataAgent NL2SQL 尖峰走 `llm-code-7b`；设备知识库问答回 `llm-general-32b`；两模型独立限流，避免 SQL 尖峰饿死对话。
- **金融（`finance`）**：全天仅本地 32B，日配额 10M 硬门禁；任何 403 以外异常都不得 fallback 到云端——降级只能是「排队」或「缓存 FAQ」，不能换模型到外部 API。
- **物流（`logistics`）**：Embedding 重建 Job 不经网关（直连 Ch.44 Triton）；运单问答经网关，弱网时 fallback 本地 3B 边缘（Ch.46）而非无限重试中心 32B。

### 常见误区

**误区 1：网关等于反向代理**

反向代理（如 Nginx）转发流量，不理解 `model` 字段、Token 用量、流式 SSE 分块、Retry-After 语义。LLM 网关必须解析 JSON body、统计 completion tokens、在 429 时返回可机器读的 `retryable`——需要 **LLM 语义层**。某次试点中，通用 Ingress 做路径路由，无法按 tenant 做 TPM 限流，也无法在 backend 503 时自动 fallback 到 `llm-code-7b`。

**误区 2：限流只在网关做一层就够**

Agent Runtime 侧仍可能循环重试放大流量：收到 429 后指数退避写错，变成固定 100ms 重试，QPS 反而翻倍。网关限流需配合 Ch.42 熔断与 Runtime 重试预算（每 session 最多 N 次、总 backoff 上限），否则 429 会被重试风暴抵消。弱网 handheld Agent 场景中，网关 429 + Runtime 无限重试 = 中心网关被打满。

**误区 3：多租户等于多个 API Key**

Key 只是认证手段；租户隔离还需要配额、路由白名单、日志分区、缓存命名空间隔离——否则 Key 泄漏即租户边界失效。finance 与 retail 各一把 Key 不够，还必须保证 finance Key 在注册表里 `allowed_models` 不可见云端 backend，且 Langfuse 项目按 tenant 分区，避免审计串扰。

**误区 4：网关可以替代 Ch.44 做模型版本管理**

有人在 LiteLLM 里维护两套 `api_base` 表示 v1/v2 模型，却不用 KServe Revision——Canary 与回滚逻辑分裂在两层，故障时无法判断流量落在哪条 Revision。网关只做路由与治理，**版本与流量百分比属于 Ch.44 InferenceService**；网关 `model_name` 保持稳定，后端 Revision 由 KServe 的 `canaryTrafficPercent` 切换。

---

## L2 架构  〔约 40% 篇幅〕

### 45.3 多租户模型：租户隔离、API Key 管理、命名空间与资源配额

网关多租户至少四层隔离——缺任何一层都会在规模化后暴露：

1. **认证层**：API Key / OAuth / mTLS，映射到 `tenant_id`；
2. **授权层**：租户可调用的 `model` 白名单；
3. **配额层**：RPM（Requests Per Minute，每分钟请求数）、TPM（Tokens Per Minute，每分钟 Token 数）、日预算；
4. **观测层**：日志、Trace、账单按 `tenant_id` 分区。

K8s Namespace 可与租户对齐（`tenant-retail`），但 Namespace 管容器隔离、NetworkPolicy 与 ResourceQuota 的 CPU/内存/GPU——**管不了 Token 配额**。Token 是业务语义资源，必须在网关或专用策略服务（如 LiteLLM DB + 自定义 middleware）实现。`finance` Namespace 里的 Pod 仍可能若持有错误 Key 访问 retail 配额——Namespace 不能替代网关授权。

![图 45-2：租户隔离是认证、授权、配额、观测四层叠加，而非单一 API Key](../images/ch/ch45-02.png)

图 45-2 中金融租户「仅本地模型」在授权层生效：即使有人持有有效 API Key，请求 `gpt-4o` 也会在网关返回 `403 MODEL_NOT_ALLOWED_FOR_TENANT`，不会泄漏到 Ch.50 才拦截。观测层的 tenant 标签由网关注入，不信任客户端 Header——见踩坑 2。

### 45.4 路由策略：按任务类型、按成本、按延迟、按合规域与降级链路

路由不是「if-else 选 URL」，而是带优先级的决策链：合规约束硬截断，业务偏好软选择，失败路径显式 fallback。输入字段应在 Ch.45 与 Runtime 之间文档化，避免各 Agent 自定义 Header 名。

路由决策输入：

```text
tenant_id, model（请求声明）, task_type（Header/metadata）,
latency_slo, compliance_zone, fallback_chain
```

路由规则（示意，与 Ch.44 服务名一致）：

| 优先级 | 条件 | 目标 backend |
|---|---|---|
| 1 | `compliance_zone=finance` | 仅 `llm-general-32b` 本地 |
| 2 | `task_type=code/sql` | `llm-code-7b` |
| 3 | `model=gpt-4o` 且 tenant 允许云端 | 外部 API |
| 4 | 默认 | `llm-general-32b` |
| fallback | 主 backend 5xx/超时 | 备用本地小模型或缓存响应 |

优先级 1 不可被客户端 `model` 字段覆盖——金融合规是硬规则。优先级 2 服务制造 DataAgent：同一 tenant `mfg` 下，NL2SQL 走 SGLang 代码模型，设备问答走 32B。优先级 4 的 fallback 必须指向 **与主 backend 不同 Revision 或不同模型**——见踩坑 1。物流 tenant 在 `llm-general-32b` 超时 30s 后可降级到更小本地模型或返回缓存的运单 FAQ，但降级质量需在 Console 明示「简答模式」。

![图 45-3：路由是带优先级的决策链，降级是显式配置的 fallback_chain](../images/ch/ch45-03.png)

图 45-3 展示路由决策链顺序：租户认证→合规硬截断→task_type→成本/延迟→backend 选择→显式 fallback；finance「拒绝云端」必须在合规层生效，不能留到模型层才拦截。

**取舍 1：LiteLLM 代理模式 vs 自研网关**

| 方案 | 优势 | 代价 | 适用场景 | 本书建议 |
|---|---|---|---|---|
| LiteLLM | 100+ 后端、OpenAI 兼容、社区活跃 | 深度企业特性需扩展 | 快速统一 API | MVP 推荐 ⭐ |
| Portkey | 可观测、路由、缓存成熟 | SaaS/许可 | 偏 SaaS 治理 | 对标参考 |
| Higress/Kong AI | 与 API 网关生态集成 | LLM 语义需插件 | 已有 Kong/Higress | 混合架构 |
| 自研 | 完全定制 | 工程量大 | 超大厂 | 长期选项 |

MVP 阶段选 LiteLLM，因 Ch.44 已统一 OpenAI 兼容 backend，LiteLLM 的 `model_list` 可快速映射 KServe Service。finance 合规路由、tenant 白名单在 LiteLLM 之上加一层 middleware 或 DB 策略，而非从零写 HTTP 代理。

**取舍 2：网关层缓存 vs 模型层 Prompt Cache**

| 方案 | 优势 | 代价 | 适用场景 | 本书建议 |
|---|---|---|---|---|
| 网关 semantic cache（Ch.41） | 跨 backend、可租户隔离 | 一致性难 | 重复问答多 | 与 LiteLLM cache 配合 ⭐ |
| 后端 prefix cache | 延迟最低 | 绑定单引擎 | vLLM 长系统 prompt | Part II Ch.7 |

零售客服重复「退换货政策」问答适合网关 semantic cache；制造 DataAgent 长 system prompt 重复利用 vLLM prefix cache 更省延迟。两层 cache 并存时，cache key 必须含 `tenant_id`，且 finance 租户应禁用跨 session 缓存或加密隔离——见踩坑 3。

### 45.5 网关产品对比：LiteLLM、Portkey、Higress AI Gateway 与 Kong AI

| 产品 | 为什么用 | 不适合什么 | 替代 |
|---|---|---|---|
| LiteLLM | 开源、多 backend、易部署 | 复杂 RBAC 需二次开发 | Portkey、自研 |
| Portkey | 路由、缓存、观测一体 | 强私有化定制 | LiteLLM + Langfuse |
| Higress AI | 云原生、Wasm 插件 | 团队无 K8s 网关经验 | Kong、Envoy |
| Kong AI | 企业 API 网关存量 | LLM 原生特性需配置 | Higress |

产品选型应服务于架构取舍，不是品牌选择。推荐路径：**LiteLLM 作 LLM 语义层**，必要时前挂 Higress 作 TLS/WAF（Ch.46 Helm 分 Chart 部署），Observability 接 Langfuse（Ch.38）。Kong AI 适合已全站 Kong 的企业，但 LLM 流式与 Token 计量插件需逐项验证，不能假设「上了 Kong 就等于上了 LLM 网关」。

#### LiteLLM + Higress 组合拓扑（简述）

请求路径：`Internet/内网 Agent` → Higress（TLS 终止、WAF、IP allowlist）→ LiteLLM Pod（LLM 语义、tenant、配额）→ KServe Service（Ch.44）。Higress **不理解** TPM 配额，LiteLLM **不替代** WAF——两层各做擅长的事。金融 tenant 的 IP allowlist 在 Higress；模型白名单在 LiteLLM DB——缺一不可。Observability 在 LiteLLM 出口注入 traceparent，Higress access log 只记录 L4/L7 元数据，不记录 prompt 正文（Ch.50 日志合规）。

### 45.6 网关接口契约：请求/响应格式、错误码、Trace 传播与审计字段

Runtime、Console 与网关之间的契约是 Part VIII 对上的「最后一道 API」——字段稳定比功能丰富更重要。以下契约与 Ch.44 OpenAI 子集衔接，并扩展治理字段。

```text
POST /v1/chat/completions
Headers:
  Authorization: Bearer <api_key>
  X-Tenant-Id: retail              # 或由 Key 映射，见踩坑 2
  X-Task-Type: nl2sql               # 可选，供路由
  traceparent: 00-<trace_id>-...   # W3C Trace Context

Request:
{
  "model": "llm-general-32b",
  "messages": [...],
  "stream": true,
  "metadata": { "agent_id": "data_agent", "session_id": "s_001" }
}

Response: （OpenAI 兼容 + 扩展 Header）
  X-Route-Backend: kserve-llm-general-32b
  X-Token-Usage-Billed: 1523

Errors:
  401 AUTH_INVALID
  403 MODEL_NOT_ALLOWED_FOR_TENANT
  429 QUOTA_EXCEEDED | RATE_LIMITED  （Retry-After 秒）
  502 BACKEND_UNAVAILABLE
  503 DEGRADED_TO_FALLBACK
Body: { "error": { "code", "message", "retryable" } }
```

`X-Route-Backend` 用于 On-call 定界：用户报「回答变慢」时，先看是网关开销还是 KServe TTFT。`503 DEGRADED_TO_FALLBACK` 表示已降级，Runtime 可决定是否向用户提示。`retryable` 帮助 Runtime 区分「不应重试的 403」与「可退避的 429/502」——403 重试只会放大审计噪音。

### 45.7 与平台其他子系统的协作：Runtime、Observability、Policy 与 Cost 治理

| 组件 | 职责 | 输入 | 输出 | 失败模式 |
|---|---|---|---|---|
| 认证器 | Key → tenant | API Key | tenant_id, scopes | Key 泄漏 |
| 路由器 | 选 backend | 请求 + 规则 | upstream URL | 规则冲突循环 |
| 限流器 | RPM/TPM | tenant + model | allow/deny | Redis 单点 |
| 配额器 | 日预算 | tenant 用量 | allow/deny | 计数漂移 |
| Trace 注入 | 关联 Ch.38 | traceparent | 后端 Header | Trace 断链 |
| 降级器 | fallback | backend 健康 | 备用 backend | 降级模型质量不足 |

Trace 应从 Runtime 经网关延续到 Ch.44 KServe Pod，Langfuse span 含 `tenant_id`、`model`、`X-Route-Backend`。Policy（Ch.50）在网关执行「finance 禁止云端」类规则，细粒度 IAM 仍在平台身份层——网关只做 LLM 调用路径的策略 enforcement。

![图 45-4：Trace 不断链，tenant 标签只在网关注入](../images/ch/ch45-04.png)

图 45-4 强调 Trace **不断链**与 tenant 标签**只在网关注入**：KServe Pod 不应信任来自客户端的 `X-Tenant-Id`，否则 finance 合规在模型层被绕过。Observability 侧应能按 `tenant_id + model + backend` 三维下钻，与 Ch.41 账单维度一致。

### 45.8 失败模式：上游超时、路由死循环、配额误配、缓存污染与租户串扰

| 失败模式 | 触发条件 | 影响 | 检测方式 | 恢复策略 |
|---|---|---|---|---|
| 上游超时 | vLLM 过载 | 用户长时间等待 | gateway_latency P99 | 超时切断 + fallback |
| 路由死循环 | fallback 指回自身 | 502 风暴 | 路由 DAG 校验 | 静态分析 fallback 链 |
| 配额误配 | finance 日限额过大 | 成本失控 | FinOps 日报 | 配额变更 CR + 双人复核 |
| 缓存污染 | 跨 tenant cache key 冲突 | A 租户看到 B 的回答片段 | 缓存 key 审计 | key 含 tenant_id+model |
| 租户串扰 | Header 伪造 tenant | 越权 | mTLS + Key 绑定 | 忽略客户端 tenant Header |

上游超时常与 Ch.43/Ch.44 容量相关：网关 timeout 设 120s 而 vLLM 队列已满，用户只会看到 spinner——应在网关侧更短 timeout + fallback，并把排队指标告警接到 Ch.42 SLO。配额误配在业务高峰尤其危险：retail 日配额未临时调高，合法流量被 429，业务方改用个人 Key 绕过网关，FinOps 失控。

#### 与 Ch.44 Canary 的联调注意

Ch.44 对 `llm-general-32b` 做 5% Canary 时，Ch.45 的 `model_list` 仍指向同一 KServe Service 名——KServe 在 Service 层分割流量，网关无需改 URL。但若工程师在 LiteLLM 新增 `llm-general-32b-canary` 作为独立 model_name 并配 fallback 回主模型，会与 KServe 内置 Canary **双重切流**，指标无法解读。规范要求：**网关 model_name 与 InferenceService 名 1:1**，Canary 只在 Ch.44 调 `canaryTrafficPercent`，网关只看聚合 `/ready` 与错误率。

#### Redis 限流单点与多副本网关

LiteLLM 多副本 + Redis 限流时，Redis 故障会导致「限流失效或全拒」——应 Redis Sentinel 或集群，且限流失败策略明确为 fail-closed（宁拒勿放）还是 fail-open（宁放勿拒）。finance 通常选 fail-closed；retail 业务高峰窗口可临时 fail-open 并强依赖 Ch.41 成本告警，但需变更单。

---

## L3 工程实现  〔约 30% 篇幅〕

### 45.9 工程落地：LiteLLM 网关配置、路由规则与多租户隔离示例

工程落地顺序：**staging 单 tenant 打通 KServe backend** → **四 tenant Key 与白名单入库** → **fallback 与限流** → **prod 切流（Ch.46 Manual Sync）**。禁止 Agent 直连 KServe 的验收标准：网络层除网关 ServiceAccount 外，InferenceService 无 ClusterIP 对外路由。

**LiteLLM `config.yaml` 示例**

`api_base` 指向 Ch.44 KServe 集群内 Service；`model_name` 与 Runtime `served-model-name`、Ch.44 契约一致。

```yaml
# 示例：LiteLLM 网关配置（生产工程示例）
model_list:
  - model_name: llm-general-32b
    litellm_params:
      model: openai/llm-general-32b
      api_base: http://llm-general-32b.model-serving.svc:8000/v1
      api_key: os.environ/INTERNAL_API_KEY
  - model_name: llm-code-7b
    litellm_params:
      model: openai/llm-code-7b
      api_base: http://llm-code-7b.model-serving.svc:8000/v1
  - model_name: gpt-4o-fallback
    litellm_params:
      model: gpt-4o
      api_key: os.environ/OPENAI_API_KEY

router_settings:
  routing_strategy: simple-shuffle   # 生产建议自定义 callback
  fallbacks:
    - llm-general-32b: [llm-code-7b]

litellm_settings:
  drop_params: true
  set_verbose: false

general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
  database_url: os.environ/DATABASE_URL   # 用量与 Key 管理
```

`fallbacks` 生产环境必须人工审查 DAG 无环；`simple-shuffle` 在多副本 KServe 间负载均衡，不能替代 tenant 路由——tenant 路由应在 DB 策略或 custom callback 实现。

**租户 Key 与模型白名单（示意 SQL 逻辑）**

```sql
-- 伪代码：租户模型授权表
-- tenant_id | allowed_models              | daily_token_quota
-- finance   | {llm-general-32b}           | 10000000
-- retail    | {llm-general-32b,gpt-4o-*}  | 50000000
```

Key 创建时绑定 `tenant_id`；请求处理路径只读 DB 映射，不读 `X-Tenant-Id` Header。

**限流配置示例**

```yaml
# 示例：LiteLLM 路由级 RPM 限制
router_settings:
  model_group_alias:
    retail-fast: llm-general-32b
  rpm: 600          # 全局示意
  tenant_rpm:
    retail: 300
    finance: 100
```

业务高峰前 retail `tenant_rpm` 需走变更单临时上调，并在 Ch.41 成本面板标注「高峰窗口」。

**部署与验证**

```bash
# 启动（示例）
litellm --config /etc/litellm/config.yaml --port 4000

# 验证路由
curl http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer $RETAIL_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"llm-general-32b","messages":[{"role":"user","content":"ping"}]}'
```

验收：finance Key 请求 `gpt-4o` 返回 403；`mfg` Key 带 `X-Task-Type: nl2sql` 时 `X-Route-Backend` 指向 code 服务；Trace 在 Langfuse 可串联三段 span。

#### Helm 部署与 Ch.46 GitOps 衔接

生产网关不手工 `litellm --config` 起进程，而由 `helm/llm-gateway` Chart 挂载 ConfigMap + External Secret：

```yaml
# 示例：Helm values-prod 片段（伪代码结构）
replicaCount: 4
config:
  model_list: []   # 由 chart 模板渲染，backend 来自 model-serving release
externalSecrets:
  openaiKey: vault/agent-platform/openai
  masterKey: vault/agent-platform/litellm-master
tenantPolicy:
  finance:
    allowed_models: [llm-general-32b]
    deny_cloud: true
  retail:
    allowed_models: [llm-general-32b, gpt-4o-fallback]
```

ArgoCD Application `llm-gateway-prod` 的 `targetRevision` 与 `model-serving-prod` 同 tag 晋升——避免网关先 sync、模型未 Ready 的窗口。staging 可允许 `replicaCount: 1` 节省成本，但 tenant 白名单必须与 prod 同逻辑，否则「staging 测通过、prod 403 策略不同」。

#### 切流 Runbook：从直连 KServe 到经网关

1. 冻结新 Agent 直连 KServe 的 NetworkPolicy（Ch.50 配合）；
2. Runtime 配置改 `OPENAI_BASE_URL=https://llm-gateway.internal/v1`；
3. 按 tenant 分批切流：finance → mfg → logistics → retail（零售最后，因 QPS 最高）；
4. 每批观察 24h：网关 P99 开销、backend 错误率、FinOps tenant 账单是否闭合；
5. 回滚：Runtime 指回 KServe 仅作紧急路径，须 4h 内补 Git revert。

### 45.10 生产化检查清单与真实踩坑记录

**踩坑 1：fallback 链配置错误导致无限重试**

- 现象：backend 故障时网关 QPS 翻倍，下游更快崩溃。
- 根因：`llm-general-32b` fallback 到 `llm-general-32b-canary`，Canary 仍指向同一 KServe Service；降级未换 Revision。
- 修复：fallback 必须指向 **不同 Revision 或不同模型**；限制每请求最多 1 次 fallback；记录 `X-Route-Backend` 审计；CI 静态检查 fallback DAG。

**踩坑 2：finance 租户通过伪造 Header 访问云端**

- 现象：合规扫描发现 finance Agent 请求出现在 OpenAI 账单。
- 根因：网关信任客户端 `X-Tenant-Id`，未从 API Key 映射；攻击者用 retail Key body 里伪造 finance。
- 修复：tenant 仅来自 Key 注册表；合规路由在服务端强制；云端 backend 对 finance Key 不可见；Ch.50 定期跑「应拒绝」探测用例。

**踩坑 3：semantic cache 未含 tenant_id 导致回答串扰**

- 现象：零售客服 Agent 返回含金融术语的缓存片段。
- 根因：cache key = hash(prompt)，未含 tenant；finance 与 retail 共享 gateway cache Redis。
- 修复：cache key = hash(tenant_id + model + prompt)；finance 租户禁用跨会话 cache 或加密隔离；缓存 TTL 与 Ch.41 semantic cache 策略对齐。

**生产化 checklist**

- [ ] 权限：Key 轮换策略；master_key 仅 SRE 可访问
- [ ] 审计：每次请求记录 tenant、model、backend、token、trace_id
- [ ] 成本：配额硬门禁 + 80% 预警；分 tenant 日报
- [ ] 性能：P99 网关开销 < 50ms（不含模型推理）
- [ ] 稳定性：fallback DAG 无环；429 带 Retry-After
- [ ] 可观测性：Langfuse/OTel 与 Ch.38 关联
- [ ] 灾难恢复：网关多副本；backend 列表 ConfigMap 热更新

#### 网关侧 Prometheus 指标（示意）

| 指标名 | 含义 | 告警建议 |
|---|---|---|
| `gateway_requests_total{tenant,model,backend}` | 请求计数 | 按 tenant 突增 |
| `gateway_latency_seconds{phase="pre_backend"}` | 网关自身开销 | P99 > 50ms |
| `gateway_quota_denied_total{tenant}` | 配额拒绝 | finance 非零即查 |
| `gateway_fallback_total{from,to}` | 降级次数 | 1h 内 > 100 |
| `gateway_backend_errors_total{backend}` | 上游 5xx | 与 Ch.44 Ready 联查 |

指标标签必须与 Ch.41 成本报表、Ch.38 Trace 的 `tenant_id` 命名一致，避免 FinOps 与 SRE 各用一套 tenant 拼写。

---

## 本章小结

### 关键结论

1. LLM 网关是 Agent 平台控制平面的统一入口，执行路由、限流、配额、Trace 与降级，与 Ch.44 模型服务解耦。
2. 多租户隔离需认证、授权、配额、观测四层叠加；tenant 必须来自 Key 映射，不能信任客户端 Header。
3. 路由是带优先级的决策链，fallback 必须无环且指向真正不同的 backend。
4. LiteLLM 适合作为 MVP 的 LLM 语义网关；企业特性（RBAC、合规路由）需二次加固。
5. 缓存 key 必须含 tenant_id；限流需与 Runtime 重试预算协同（Ch.42）。

### 上线检查清单

- [ ] 能上线吗？所有 Agent 已切网关、无直连 KServe
- [ ] 能扩展吗？backend 列表可热更新、规则可版本化
- [ ] 能治理吗？分 tenant 账单、审计、配额、合规路由可验证

### 延伸阅读

- 官方文档：[LiteLLM 文档](https://docs.litellm.ai/)、[Higress AI Gateway](https://higress.io/)、[Kong AI Plugin](https://docs.konghq.com/)
- 对标产品：Portkey、Helicone、Cloudflare AI Gateway
- 相关章节：Part VII [Ch.41–42](../part07-observability-eval/ch41-cost-governance-cache.md)、Part VIII [Ch.44 模型部署](ch44.md)、Part X [Ch.50 安全](../part10-security-org/ch50.md)

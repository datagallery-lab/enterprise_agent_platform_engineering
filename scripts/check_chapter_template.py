"""Check that chapter drafts conform to their expected heading conventions.

Usage:
    python scripts/check_chapter_template.py
Exit code 0 if all chapters pass, 1 otherwise.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

REQUIRED_HEADINGS = [
    re.compile(r"^##\s+L1\s+概念"),
    re.compile(r"^##\s+L2\s+架构"),
    re.compile(r"^##\s+L3\s+"),
    re.compile(r"^##\s+本章小结"),
]

ARTICLE_HEADINGS_BY_PATH = {
    Path("part04-vector-knowledge/ch16.md"): [
        re.compile(r"^##\s+嵌入模型的企业应用场景$"),
        re.compile(r"^##\s+向量表示与相似度计算$"),
        re.compile(r"^##\s+文本嵌入模型选型$"),
        re.compile(r"^##\s+多模态嵌入与视觉检索$"),
        re.compile(r"^##\s+企业级嵌入模型评估框架$"),
    ],
    Path("part04-vector-knowledge/ch17.md"): [
        re.compile(r"^##\s+领域语义适配需求$"),
        re.compile(r"^##\s+对比学习与样本构造$"),
        re.compile(r"^##\s+嵌入模型微调路线$"),
        re.compile(r"^##\s+重排模型架构位置$"),
        re.compile(r"^##\s+标注评测与版本治理$"),
    ],
    Path("part04-vector-knowledge/ch18.md"): [
        re.compile(r"^##\s+向量库平台定位$"),
        re.compile(r"^##\s+ANN 索引算法谱系$"),
        re.compile(r"^##\s+主流向量库技术选型$"),
        re.compile(r"^##\s+元数据过滤与多租户权限$"),
        re.compile(r"^##\s+索引生命周期治理$"),
        re.compile(r"^##\s+工程实践：嵌入模型微调 \+ 向量库 benchmark$"),
    ],
    Path("part04-vector-knowledge/ch19-ocr.md"): [
        re.compile(r"^##\s+企业文档解析挑战$"),
        re.compile(r"^##\s+文档结构与版面语义$"),
        re.compile(r"^##\s+文档解析工具链选型$"),
        re.compile(r"^##\s+多模态 OCR 与 VLM 解析$"),
        re.compile(r"^##\s+解析流水线与质量门禁$"),
    ],
    Path("part04-vector-knowledge/ch20-rag.md"): [
        re.compile(r"^##\s+RAG 工程体系$"),
        re.compile(r"^##\s+Chunk 策略与上下文组装$"),
        re.compile(r"^##\s+混合检索与排序融合$"),
        re.compile(r"^##\s+查询理解与多跳检索$"),
        re.compile(r"^##\s+可信回答与证据溯源$"),
    ],
    Path("part04-vector-knowledge/ch21.md"): [
        re.compile(r"^##\s+企业知识工程定位$"),
        re.compile(r"^##\s+本体建模与业务语义层$"),
        re.compile(r"^##\s+信息抽取与实体链接$"),
        re.compile(r"^##\s+图数据库与 GraphRAG 架构$"),
        re.compile(r"^##\s+知识资产治理$"),
    ],
    Path("part09-frontend-multimodal/ch47-ui.md"): [
        re.compile(r"^##\s+企业 Agent UI 组成$"),
        re.compile(r"^##\s+流式交互协议$"),
        re.compile(r"^##\s+消息模型与增量渲染$"),
        re.compile(r"^##\s+Agent 前端框架选型$"),
        re.compile(r"^##\s+可靠交互与前端可观测$"),
        re.compile(r"^##\s+本章小结$"),
    ],
    Path("part09-frontend-multimodal/ch48-generative-ui.md"): [
        re.compile(r"^##\s+任务化交互界面$"),
        re.compile(r"^##\s+工具调用渲染模式$"),
        re.compile(r"^##\s+Artifacts 与可编辑产物$"),
        re.compile(r"^##\s+业务控件与数据可视化$"),
        re.compile(r"^##\s+UI 安全与审批流程$"),
        re.compile(r"^##\s+工程实验：Generative UI DataAgent 工作台$"),
        re.compile(r"^##\s+本章小结$"),
    ],
    Path("part09-frontend-multimodal/ch49-agent.md"): [
        re.compile(r"^##\s+多模态输入产品边界$"),
        re.compile(r"^##\s+文件上传与异步解析$"),
        re.compile(r"^##\s+语音 Agent 架构$"),
        re.compile(r"^##\s+实时语音交互控制$"),
        re.compile(r"^##\s+多模态权限与审计留痕$"),
        re.compile(r"^##\s+工程实验：语音与文件输入扩展$"),
        re.compile(r"^##\s+本章小结$"),
    ],
    Path("part10-security-org/ch50.md"): [
        re.compile(r"^##\s+企业 Agent 攻击面$"),
        re.compile(r"^##\s+Prompt Injection 与间接注入$"),
        re.compile(r"^##\s+工具越权与数据泄漏$"),
        re.compile(r"^##\s+AI Red Teaming 方法体系$"),
        re.compile(r"^##\s+安全基线与事件响应$"),
        re.compile(r"^##\s+工程实验：Prompt Injection 攻防$"),
        re.compile(r"^##\s+本章小结$"),
    ],
    Path("part10-security-org/ch51-guardrails.md"): [
        re.compile(r"^##\s+Guardrails 分层架构$"),
        re.compile(r"^##\s+内容安全分类器$"),
        re.compile(r"^##\s+可编程策略引擎$"),
        re.compile(r"^##\s+脱敏过滤与输出校验$"),
        re.compile(r"^##\s+策略误杀漏杀治理$"),
        re.compile(r"^##\s+工程实验：可配置 Guardrails 网关$"),
        re.compile(r"^##\s+本章小结$"),
    ],
    Path("part10-security-org/ch52.md"): [
        re.compile(r"^##\s+合规工程化框架$"),
        re.compile(r"^##\s+NIST AI RMF 风险管理$"),
        re.compile(r"^##\s+EU AI Act 风险分级$"),
        re.compile(r"^##\s+中国生成式 AI 合规要求$"),
        re.compile(r"^##\s+内容溯源与 C2PA$"),
        re.compile(r"^##\s+工程实验：合规控制矩阵生成器$"),
        re.compile(r"^##\s+本章小结$"),
    ],
    Path("part10-security-org/ch53.md"): [
        re.compile(r"^##\s+AI 平台团队职责边界$"),
        re.compile(r"^##\s+PoC 到平台化运营路径$"),
        re.compile(r"^##\s+ROI、SLO 与价值度量$"),
        re.compile(r"^##\s+人才结构与能力模型$"),
        re.compile(r"^##\s+三年平台演进路线图$"),
        re.compile(r"^##\s+工程实验：平台成熟度评估表$"),
        re.compile(r"^##\s+本章小结$"),
    ],
}


def check_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    errors: list[str] = []
    rel = path.relative_to(DOCS)
    required = ARTICLE_HEADINGS_BY_PATH.get(rel, REQUIRED_HEADINGS)
    for pat in required:
        if not any(pat.search(line) for line in lines):
            errors.append(f"missing section matching {pat.pattern}")
    return errors


def main() -> int:
    bad = 0
    for path in sorted(DOCS.glob("part*/ch*.md")):
        errs = check_file(path)
        if errs:
            bad += 1
            rel = path.relative_to(ROOT)
            print(f"✗ {rel}")
            for e in errs:
                print(f"   - {e}")
    total = len(list(DOCS.glob("part*/ch*.md")))
    if bad:
        print(f"\n{bad}/{total} chapter(s) failed template check.")
        return 1
    print(f"\n✓ all {total} chapters satisfy heading checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

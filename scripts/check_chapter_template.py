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

LEGACY_TEMPLATE_HEADINGS = [
    re.compile(r"^##\s+L1\s+概念"),
    re.compile(r"^##\s+L2\s+架构"),
    re.compile(r"^##\s+L3\s+"),
    re.compile(r"^#{2,4}\s+\d+(?:\.\d+)*\s+业务场景[:：]为什么企业需要这个能力"),
    re.compile(r"^#{2,4}\s+\d+(?:\.\d+)*\s+核心概念与边界"),
    re.compile(r"^#{2,4}\s+\d+(?:\.\d+)*\s+常见误区"),
    re.compile(r"^#{2,4}\s+\d+(?:\.\d+)*\s+在平台中的位置"),
    re.compile(r"^#{2,4}\s+\d+(?:\.\d+)*\s+组件划分与接口契约"),
    re.compile(r"^#{2,4}\s+\d+(?:\.\d+)*\s+状态机\s*/\s*时序\s*/\s*失败模式"),
    re.compile(r"^#{2,4}\s+\d+(?:\.\d+)*\s+mini-platform 中的实现路径", re.IGNORECASE),
    re.compile(r"^#{2,4}\s+\d+(?:\.\d+)*\s+可运行代码与配置"),
    re.compile(r"^#{2,4}\s+\d+(?:\.\d+)*\s+生产化\s*checklist", re.IGNORECASE),
    re.compile(r"^#{2,4}\s+\d+(?:\.\d+)*\s+上线检查清单"),
    re.compile(r"^#{2,4}\s+\d+(?:\.\d+)*\s+踩坑记录"),
    re.compile(r"^#{2,4}\s+\d+(?:\.\d+)*\s+.+发布校验"),
    re.compile(r"^#{2,4}\s+\d+(?:\.\d+)*\s+.+异常定位"),
    re.compile(r"^#{2,4}\s+\d+(?:\.\d+)*\s+.+接入门禁"),
    re.compile(r"^#{2,4}\s+\d+(?:\.\d+)*\s+.+故障定界"),
    re.compile(r"^#{2,4}\s+\d+(?:\.\d+)*\s+mini-platform\s+关联", re.IGNORECASE),
    re.compile(r"^#{2,4}\s+\d+(?:\.\d+)*\s+项目演练[：:]"),
]

UNPROFESSIONAL_HEADING_PATTERNS = [
    re.compile(r"(什么|为什么|如何|怎么|哪些|到底|是否|能否|吗|？)"),
    re.compile(r"(要确认什么|要检查什么|要满足什么|要回答什么|要复盘什么|长什么样|解决什么)"),
    re.compile(r"(不要|不能|不应|不是|而不是|不该用)"),
]

ARTICLE_CLOSING_HEADING = re.compile(
    r"^##\s+(?:本章小结|第[一二三四五六七八九十百0-9]+章收束.*)$"
)
ARTICLE_H2_HEADING = re.compile(r"^##\s+")
ARTICLE_H3_HEADING = re.compile(r"^###\s+")
ARTICLE_REFERENCE_HEADING = re.compile(r"^##\s+参考文献$")
CHAPTER_HEADING = re.compile(r"^#\s+第(?P<number>\d+)章\b")
NUMBERED_HEADING_PREFIX = re.compile(r"^(#{2,3})\s+\d+(?:\.\d+)*\s+")
SPECIAL_H2_HEADINGS = {
    "摘要",
    "关键词",
    "学习目标",
    "本章摘要",
    "场景引入",
    "开篇场景",
    "本章小结",
    "参考文献",
    "延伸阅读",
    "下一章预告",
    "术语表",
}
SPECIAL_H3_HEADINGS = {
    "案例背景",
    "回溯过程",
    "事故概述",
    "时间线",
    "根因分析",
    "修复措施",
    "事故复盘模板",
    "关键指标改进效果",
}
REQUIRED_FRONT_MATTER_HEADINGS = [
    "本章摘要",
    "关键词",
    "学习目标",
    "场景引入",
]

ARTICLE_HEADINGS_BY_PATH = {
    Path("part04-vector-knowledge/ch/ch16.md"): [
        re.compile(r"^##\s+嵌入模型的企业应用场景$"),
        re.compile(r"^##\s+向量表示与相似度计算$"),
        re.compile(r"^##\s+文本嵌入模型选型$"),
        re.compile(r"^##\s+多模态嵌入与视觉检索$"),
        re.compile(r"^##\s+企业级嵌入模型评估框架$"),
    ],
    Path("part04-vector-knowledge/ch/ch17.md"): [
        re.compile(r"^##\s+领域语义适配需求$"),
        re.compile(r"^##\s+对比学习与样本构造$"),
        re.compile(r"^##\s+嵌入模型微调路线$"),
        re.compile(r"^##\s+重排模型架构位置$"),
        re.compile(r"^##\s+标注评测与版本治理$"),
    ],
    Path("part04-vector-knowledge/ch/ch18.md"): [
        re.compile(r"^##\s+向量库平台定位$"),
        re.compile(r"^##\s+ANN 索引算法谱系$"),
        re.compile(r"^##\s+主流向量库技术选型$"),
        re.compile(r"^##\s+元数据过滤与多租户权限$"),
        re.compile(r"^##\s+索引生命周期治理$"),
        re.compile(r"^##\s+工程实践：嵌入模型微调 \+ 向量库 benchmark$"),
    ],
    Path("part04-vector-knowledge/ch/ch19-ocr.md"): [
        re.compile(r"^##\s+企业文档解析挑战$"),
        re.compile(r"^##\s+文档结构与版面语义$"),
        re.compile(r"^##\s+文档解析工具链选型$"),
        re.compile(r"^##\s+多模态 OCR 与 VLM 解析$"),
        re.compile(r"^##\s+解析流水线与质量门禁$"),
    ],
    Path("part04-vector-knowledge/ch/ch20-rag.md"): [
        re.compile(r"^##\s+RAG 工程体系$"),
        re.compile(r"^##\s+Chunk 策略与上下文组装$"),
        re.compile(r"^##\s+混合检索与排序融合$"),
        re.compile(r"^##\s+查询理解与多跳检索$"),
        re.compile(r"^##\s+可信回答与证据溯源$"),
    ],
    Path("part04-vector-knowledge/ch/ch21.md"): [
        re.compile(r"^##\s+企业知识工程定位$"),
        re.compile(r"^##\s+本体建模与业务语义层$"),
        re.compile(r"^##\s+信息抽取与实体链接$"),
        re.compile(r"^##\s+图数据库与 GraphRAG 架构$"),
        re.compile(r"^##\s+知识资产治理$"),
    ],
    Path("part09-frontend-multimodal/ch/ch47-ui.md"): [
        re.compile(r"^##\s+企业 Agent UI 组成$"),
        re.compile(r"^##\s+流式交互协议$"),
        re.compile(r"^##\s+消息模型与增量渲染$"),
        re.compile(r"^##\s+Agent 前端框架选型$"),
        re.compile(r"^##\s+可靠交互与前端可观测$"),
        re.compile(r"^##\s+本章小结$"),
    ],
    Path("part09-frontend-multimodal/ch/ch48-generative-ui.md"): [
        re.compile(r"^##\s+任务化交互界面$"),
        re.compile(r"^##\s+工具调用渲染模式$"),
        re.compile(r"^##\s+Artifacts 与可编辑产物$"),
        re.compile(r"^##\s+业务控件与数据可视化$"),
        re.compile(r"^##\s+UI 安全与审批流程$"),
        re.compile(r"^##\s+本章小结$"),
    ],
    Path("part09-frontend-multimodal/ch/ch49-agent.md"): [
        re.compile(r"^##\s+多模态输入产品边界$"),
        re.compile(r"^##\s+文件上传与异步解析$"),
        re.compile(r"^##\s+语音 Agent 架构$"),
        re.compile(r"^##\s+实时语音交互控制$"),
        re.compile(r"^##\s+多模态权限与审计留痕$"),
        re.compile(r"^##\s+本章小结$"),
    ],
    Path("part10-security-org/ch/ch50.md"): [
        re.compile(r"^##\s+企业 Agent 攻击面$"),
        re.compile(r"^##\s+Prompt Injection 与间接注入$"),
        re.compile(r"^##\s+工具越权与数据泄漏$"),
        re.compile(r"^##\s+AI Red Teaming 方法体系$"),
        re.compile(r"^##\s+安全基线与事件响应$"),
        re.compile(r"^##\s+Prompt Injection 攻防评估$"),
        re.compile(r"^##\s+本章小结$"),
    ],
    Path("part10-security-org/ch/ch51-guardrails.md"): [
        re.compile(r"^##\s+Guardrails 分层架构$"),
        re.compile(r"^##\s+内容安全分类器$"),
        re.compile(r"^##\s+可编程策略引擎$"),
        re.compile(r"^##\s+脱敏过滤与输出校验$"),
        re.compile(r"^##\s+策略误杀漏杀治理$"),
        re.compile(r"^##\s+可配置 Guardrails 网关评估$"),
        re.compile(r"^##\s+本章小结$"),
    ],
    Path("part10-security-org/ch/ch52.md"): [
        re.compile(r"^##\s+合规工程化框架$"),
        re.compile(r"^##\s+NIST AI RMF 风险管理$"),
        re.compile(r"^##\s+EU AI Act 风险分级$"),
        re.compile(r"^##\s+中国生成式 AI 合规要求$"),
        re.compile(r"^##\s+内容溯源与 C2PA$"),
        re.compile(r"^##\s+合规控制矩阵的生成与校验$"),
        re.compile(r"^##\s+本章小结$"),
    ],
    Path("part10-security-org/ch/ch53.md"): [
        re.compile(r"^##\s+AI 平台团队的职责边界$"),
        re.compile(r"^##\s+从试点到平台化运营$"),
        re.compile(r"^##\s+ROI、SLO 与价值度量$"),
        re.compile(r"^##\s+人才结构与能力模型$"),
        re.compile(r"^##\s+三年平台演进路径$"),
        re.compile(r"^##\s+平台成熟度评估设计$"),
        re.compile(r"^##\s+本章小结$"),
    ],
}


def content_lines(lines: list[str]) -> list[str]:
    result: list[str] = []
    in_fence = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if not in_fence:
            result.append(line)
    return result


def normalize_heading_line(line: str) -> str:
    """Remove chapter-number prefixes from H2/H3 headings for content matching."""
    return NUMBERED_HEADING_PREFIX.sub(r"\1 ", line)


def missing_patterns(lines: list[str], patterns: list[re.Pattern[str]]) -> list[str]:
    errors: list[str] = []
    normalized_lines = [normalize_heading_line(line) for line in lines]
    for pat in patterns:
        if not any(pat.search(line) for line in normalized_lines):
            errors.append(f"missing section matching {pat.pattern}")
    return errors


def legacy_template_errors(lines: list[str]) -> list[str]:
    errors: list[str] = []
    for line in lines:
        for pat in LEGACY_TEMPLATE_HEADINGS:
            if pat.search(line):
                errors.append(f"legacy template heading is not allowed: {line}")
    return errors


def heading_tone_errors(lines: list[str]) -> list[str]:
    """Reject chatty or prompt-like section headings in Chinese chapters."""
    errors: list[str] = []
    for line in lines:
        if not re.match(r"^#{2,4}\s+", line):
            continue
        normalized = normalize_heading_line(line)
        title = re.sub(r"^#{2,4}\s+", "", normalized).strip()
        if title in SPECIAL_H2_HEADINGS or title in SPECIAL_H3_HEADINGS:
            continue
        for pat in UNPROFESSIONAL_HEADING_PATTERNS:
            if pat.search(title):
                errors.append(
                    "heading should be a formal noun phrase, not a question/chatty phrase: "
                    + line
                )
                break
    return errors


def front_matter_errors(lines: list[str]) -> list[str]:
    """Require the published-book style chapter lead before the numbered body."""
    errors: list[str] = []
    first_numbered_h2 = next(
        (
            i
            for i, line in enumerate(lines)
            if re.match(r"^##\s+\d+\.\d+\b", line)
        ),
        None,
    )
    if first_numbered_h2 is None:
        return ["missing first numbered H2 body section"]

    front_lines = lines[:first_numbered_h2]
    seen: list[str] = []
    for line in front_lines:
        if not line.startswith("## "):
            continue
        heading = line[3:].strip()
        if heading in REQUIRED_FRONT_MATTER_HEADINGS:
            seen.append(heading)

    if seen != REQUIRED_FRONT_MATTER_HEADINGS:
        errors.append(
            "front matter must be ordered as: "
            + " -> ".join(REQUIRED_FRONT_MATTER_HEADINGS)
        )

    for line in front_lines:
        if line.startswith(">"):
            errors.append(f"legacy blockquote front matter is not allowed: {line}")
            break
    return errors


def chapter_numbering_errors(lines: list[str]) -> list[str]:
    chapter_number: int | None = None
    errors: list[str] = []
    for line in lines:
        chapter_match = CHAPTER_HEADING.search(line)
        if chapter_match:
            chapter_number = int(chapter_match.group("number"))
            continue
        if chapter_number is None:
            continue

        if line.startswith("## "):
            title = line[3:].strip()
            normalized_title = normalize_heading_line(line)[3:].strip()
            if normalized_title in SPECIAL_H2_HEADINGS:
                continue
            if not re.match(rf"^{chapter_number}\.\d+\b", title):
                errors.append(
                    f"H2 heading must use chapter-prefixed numbering: {line}"
                )
        elif line.startswith("### "):
            title = line[4:].strip()
            normalized_title = normalize_heading_line(line)[4:].strip()
            if normalized_title in SPECIAL_H3_HEADINGS:
                continue
            if not re.match(rf"^{chapter_number}\.\d+\.\d+\b", title):
                errors.append(
                    f"H3 heading must use chapter-prefixed numbering: {line}"
                )
    if chapter_number is None:
        errors.append("missing chapter heading matching # 第N章 ...")
    return errors


def check_article_structure(lines: list[str]) -> list[str]:
    closing_index = next(
        (
            i
            for i, line in enumerate(lines)
            if ARTICLE_CLOSING_HEADING.search(normalize_heading_line(line))
        ),
        None,
    )
    if closing_index is None:
        return [f"missing article closing section matching {ARTICLE_CLOSING_HEADING.pattern}"]

    body_lines = lines[:closing_index]
    body_h2_count = sum(
        1
        for line in body_lines
        if ARTICLE_H2_HEADING.search(line)
        and not ARTICLE_REFERENCE_HEADING.search(normalize_heading_line(line))
        and not ARTICLE_CLOSING_HEADING.search(normalize_heading_line(line))
    )
    body_h3_count = sum(1 for line in body_lines if ARTICLE_H3_HEADING.search(line))
    if body_h2_count >= 3 or body_h3_count >= 3:
        return []
    return ["missing article body structure with at least 3 H2 or H3 sections"]


def check_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    lines = content_lines(text.splitlines())
    rel = path.relative_to(DOCS)
    errors = legacy_template_errors(lines)
    errors.extend(heading_tone_errors(lines))
    errors.extend(front_matter_errors(lines))
    errors.extend(chapter_numbering_errors(lines))
    if rel in ARTICLE_HEADINGS_BY_PATH:
        errors.extend(missing_patterns(lines, ARTICLE_HEADINGS_BY_PATH[rel]))
    else:
        errors.extend(check_article_structure(lines))
    return errors


def main() -> int:
    bad = 0
    chapter_paths = sorted(
        path
        for path in DOCS.rglob("ch*.md")
        if "/en/" not in path.as_posix()
    )
    for path in chapter_paths:
        errs = check_file(path)
        if errs:
            bad += 1
            rel = path.relative_to(ROOT)
            print(f"✗ {rel}")
            for e in errs:
                print(f"   - {e}")
    total = len(chapter_paths)
    if bad:
        print(f"\n{bad}/{total} chapter(s) failed template check.")
        return 1
    print(f"\n✓ all {total} chapters satisfy heading checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

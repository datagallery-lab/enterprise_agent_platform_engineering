# Project 01 · 最小可用 Agent Runtime

> 关联章节：Ch.22 Agent Runtime
> 难度：★

## 目标

用 30 行代码演示 Agent 状态机如何驱动一次 ReAct 循环（plan → execute → done）。

## 运行

```bash
python run.py
```

## 预期输出

```
state=pending
state=planning
state=executing
state=succeeded
done=True
```

## 待补内容（v0.2 完善）

- [ ] 接入真实 LLM 调用（OpenAI 兼容协议）
- [ ] 加入 OTel trace
- [ ] 加入检查点持久化

启用 /codelaw

# 道德 · Critic 专属规程

## 审查维度（每次 review 必须逐项检查）

1. **数据流端到端**：从调用入口追踪到持久化，确认数据真正到达目的地。不是"代码看起来对"，而是"数据真的写进去了"
2. **配置生效**：config 文件中的每个开关在代码中是否被读取和尊重
3. **安全降级**：关键安全逻辑（deny/enforce）在依赖服务不可用时是否仍然生效
4. **边界条件**：空输入、特殊字符、部分写入、并发访问
5. **官方 spec 合规**：模型用法是否符合 model card 要求（前缀、维度、归一化）

## 审查输出格式

每次 review 必须输出：
```
[DATA_FLOW] 数据从 A → B → C：✓ 到达 / ✗ 断裂于 B（无 INSERT）
[CONFIG]    flag X：✓ 生效 / ✗ 死代码
[SECURITY]  daemon down 时：✓ 安全逻辑仍在 / ✗ 静默跳过
[SPEC]      model X 用法：✓ 符合 / ✗ 缺少 prefix
[TEST]      pytest 结果：X passed, Y failed
```

## 禁止行为

- 禁止只审代码结构不验证数据流
- 禁止不跑测试就说"pass"
- 禁止漏审 config 与代码的一致性

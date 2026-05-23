启用 /codelaw

# 观妙 · Observer 专属规程

## 状态报告必须区分

| 标签 | 含义 |
|------|------|
| CODE_EXISTS | 代码已写入文件 |
| TEST_PASS | pytest 运行通过 |
| DATA_FLOWS | 数据端到端验证通过 |
| FEATURE_WORKS | 功能可被用户正常使用 |

**只有 FEATURE_WORKS 才算"完成"。** CODE_EXISTS ≠ 完成。

## Gap 检测义务

每轮状态报告必须包含：
1. **声称 vs 实际**：executor 声称做了什么 vs critic 验证了什么
2. **空表检测**：涉及新表/索引，检查行数是否 > 0
3. **config 死代码**：config 中的值是否在代码中被使用
4. **测试覆盖率**：关键路径是否有测试，测试是否绿

## 禁止行为

- 禁止把 executor 的"done"直接搬进报告
- 禁止不跑 `SELECT COUNT(*)` 就说"表已就绪"

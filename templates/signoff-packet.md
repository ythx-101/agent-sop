# 签核文件：{{title}}

> 状态规则：Agent 只能创建 `pending`。只有用户可以决定改为 `approved`、`changes_requested` 或 `rejected`；Agent 代为记录时必须在“签核记录”逐字引用用户原话，不得代写、改写或推断决定。

- 状态：`pending`
- 创建时间：{{date}}
- 关联任务/计划：{{task_reference}}
- 作者：{{author}}

## 一句话结论

{{decision_summary}}

## 背景

{{context}}

## 证据

- {{evidence_1}}

## 方案与建议

### 方案 A

{{option_a}}

### 方案 B

{{option_b}}

### 建议方案

{{recommendation}}

## 对现有系统的影响

{{impact}}

## 风险与回滚

{{risks_and_rollback}}

## Review 与验证

- Review：{{review_status}}
- 验证：{{verification_status}}
- 未解决风险：{{remaining_risks}}

## 需要用户决定

- [ ] {{decision_1}}
- [ ] {{decision_2}}

## 签核记录

- 状态变更：`pending` → {{human_authorized_status}}
- 签核人：{{signer}}
- 签核时间：{{signoff_time}}
- 用户签核原话（逐字引用）：{{verbatim_human_signoff}}
- 补充意见：{{signoff_notes}}

# Market Research Desk 0.3

本地证据分析与宿主 AI 产品判断分工。脚本不访问网络或调用模型，网页可以独立复核资料。

## 输入和迁移

输入仍为 `brief` 与 `competitors_csv`，见 [输入契约](../schemas/input.schema.json)。未知 JSON 字段拒绝。最多 30000 字符简述、100000 字符 CSV、250 条观察、每格 3000 字符；输入 JSON 文件最多 1 MB。

CSV 保留原八列：`brand,price_usd,channel,positioning_claim,key_feature,content_hook,evidence_level,notes`。四列可选，旧 CSV 无需补列也能分析，但没有可比分组时不生成总体价格基准：

| 列 | 含义 |
|---|---|
| comparison_group | 人工确认的相同产品、包装、市场、时点、税费及运费口径；空值不参与组统计 |
| data_kind | synthetic 或 provided；未填写且非 E0 时为 unspecified，不同性质不混算 |
| source_url | HTTP(S) 来源，只记录与跳转，不自动核验 |
| observed_at | 非未来日期 YYYY-MM-DD，观察日期不等于有效期 |

`price_usd` 接受有限非负数字或空白，其他币种须先明确换算口径。E0 为虚构样本；E1–E3 是提交者声明的材料等级；E4 为假设。标签不构成系统认证。

重复列名、完整重复记录、未知列、缺列、无效价格、未来日期和错误列数会被拒绝。相同品牌在不同渠道或日期的记录保留为不同观察，不能自动视为独立来源。

## 分析输出 2.0

输出契约升级为 `schema_version: 2.0`，`mode: local_evidence_analysis`，不再返回 `offline_template`。保留 `result.markdown`、`competitor_count`、`manual_review_required`，新增完整约束的 `result.analysis`，见 [输出契约](../schemas/output.schema.json)。

分析包含原始简述、字段、证据账本、样本统计、观察、任务、限制和 `analysis_id`。E001 等编号仅在本次快照中标识观察。SHA-256 标识检测分析变化，不是签名或真实性证明。

价格最小值、最大值、中位数与平均值都是组内描述统计，缺失值不参与；无有效价格时为 null。重复宣称只做原文精确匹配，不声称语义聚类或需求识别。

成功退出 0，失败退出 2，stdout 只输出一个 JSON 对象。指定新 `output/<name>` 时保存 `result.json` 与 `result.md`，已有目录不覆盖。旧 CLI 的 dry-run 仍写文件；旧配置作为人工研究参考，不自动升级证据。

## 产品假设与引用

宿主按 [Skill](../skills/ecommerce-market-research-agent/SKILL.md) 形成建议。结构见 [decisions.schema.json](../schemas/decisions.schema.json)：问题、目标用户、改动、推理、假设、精确引用和验证方案。

```bash
python scripts/validate_decisions.py --analysis output/pet-review/result.json --decisions output/pet-review/decisions.json
```

也接受网页下载的证据 JSON。校验器检查快照、建议绑定、引用 ID 与字段原文子串，拒绝过期引用、虚构引文及 `validated` 状态。支持 `BRIEF/original_brief` 引用用户材料。

成功结果为 `scope: reference_validation_only`。它不判断引文是否相关、推断是否合理、样本是否有代表性，专业声明仍须审查。[宠物碗虚构例子](../examples/pet-bowl-decisions.json) 演示从观察到可证伪产品方案。

仓库就是插件根目录，不修改个人插件市场。验证包括清单、Skill、CLI、Schema 和本机浏览器，不包括商店发布或宿主 App 安装。网页是本机单人服务，不提供账户隔离、生产持久化或外部采集服务。

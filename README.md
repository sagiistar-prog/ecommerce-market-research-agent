# Market Research Desk

把产品问题和竞品观察整理成可核对的样本结论，再决定下一步验证什么。适合手头已有资料、需要评估新品方向的产品与品类人员。

当前版本 0.5：本地分析器负责数据检查、价格分组和证据追溯；Skill 引导宿主 AI 根据具体品类形成产品假设。研究者可记录成对任务测试计划，导入观察并核对指标与护栏。网页可独立离线使用，无需模型密钥。**不自动抓取网站，不把虚构样例当作市场事实。**

[产品取舍](docs/product-case.md) | [本轮验收](docs/paired-task-tests.md) | [插件与数据格式](docs/plugin.md) | [维护记录](CHANGELOG.md)

新增 [测试计划与结果复核](docs/paired-task-tests.md)：选择 Plan a test 后，在 Tests 记录主指标、阈值、样本量和护栏，下载计划，随后导入观察 CSV。结果只说明提交数据是否达到所设条件，不等于统计显著或商业价值已经成立。全部示例明确为虚构练习。

## 下载后使用

需要 Python 3.10 或更高版本。在仓库根目录运行：

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS / Linux: source .venv/bin/activate
python -m pip install -r requirements-plugin.txt
python scripts/app_server.py --port 8765
```

打开终端显示的本地地址。端口被占用时会选择后续空闲端口。

1. 写明品类、目标市场、用户假设和研究问题，支持中英文标签。纯文本会保留，并提示待补字段。
2. 粘贴或导入竞品 CSV；也可以加载明确标注为虚构的示例。
3. 查看样本结论与下一步任务，点击 E001 等编号核对原始记录。
4. 在 Hypotheses 导入宿主 AI 生成的 `decisions.json`，展开引用核对原始字段。首次体验可先 Load sample，再 Try sample hypotheses。
5. 逐条选择 Plan a test、Defer 或 Reject，填写理由并 Record choice；默认保持 Not reviewed，可以撤销上一次记录。
6. Download review 保存包含证据、假设和取舍的 JSON；Download review notes 导出阅读版。重开页面后，分析相同的简述与 CSV，再导入保存的 review JSON 恢复。修改输入后旧结果停止导出。
7. 对已计划的假设，在 Tests 记录成对任务计划，导入观察 CSV，下载结果。恢复测试时先恢复匹配的评审，再导入计划或结果 JSON；已有结果会重新计算。

输入只在本机请求中处理，网页服务不保存输入或请求正文，也不访问资料中的 URL。服务用于本机单人使用，不是已部署的多租户系统。

## AI 插件流程

仓库根目录包含 `.codex-plugin/plugin.json`。宿主负责模型推理，本地脚本提供可执行的证据约束。

```bash
python scripts/plugin_run.py --input examples/pet-bowl-input.json --output-dir output/pet-review
python scripts/validate_decisions.py --analysis output/pet-review/result.json --decisions examples/pet-bowl-decisions.json
```

第一步生成 `result.json` 与 `result.md`，同名目录不会覆盖。第二步校验示例建议的引用。实际使用时，宿主 AI 应针对用户的输入写出自己的 `decisions.json`，包含用户问题、产品改动、依据、假设、验证方法、主指标、护栏指标和判定条件，再运行校验器。

`analysis_id` 绑定完整分析快照。输入更新、引用不存在、引文与原文不符都会导致失败。通过只代表引用完整，不代表建议正确或产生商业效果。

## 产品取舍

- 不同品类使用各自输入，不预设灯具人群、桌面改造或赠礼卖点。
- 空价格保持为空，保留小数，正确读取 `1e2`。缺失数据不会被统计为零。
- 只对明确声明的 `comparison_group` 计算样本价格；不同包装、条件和数据性质分开。
- 来源 URL、采集日期、等级和原文一起保留。提供者的等级标签不等于核验结果。
- 样本渠道数量不被解释为市场份额，重复竞品宣称不被解释为真实需求。
- 缺失证据转成有完成条件的研究任务，具体品类判断由宿主 AI 和研究者完成。

Content Growth 场景中，先选择一条有出处的竞品承诺，再提出适合自身产品的可证伪表达和测试方案，不自动输出可直接发布的营销结论。

## Safe Demo 与验证

The Safe Demo does not scrape, fetch or verify live market data. All committed examples are fictional portfolio fixtures.

旧命令继续可用。`--dry-run` 标识离线演示，仍会写入指定报告：

```bash
python scripts/generate_market_report.py --input examples/sample_product_brief.md --competitors examples/sample_competitor_table.csv --output examples/generated_market_report.md --rules configs/research_rules.yaml --sources configs/source_policy.yaml --preferences configs/user_preferences.yaml --dry-run
python -m unittest discover -s tests -v
powershell -ExecutionPolicy Bypass -File scripts/portfolio_audit.ps1
```

旧配置保留为研究参考，不会自动提高输入证据等级。网页、插件与旧命令共用 [分析核心](scripts/evidence_analysis.py)。

本地与 CI 验证覆盖数据边界、跨品类、引用完整性和 HTTP 接口。真实用户任务完成率、研究时间改善和业务收益尚未测量，试用计划见 [产品案例](docs/product-case.md)。

开源依赖与贡献边界见 [docs/open-source.md](docs/open-source.md)。未宣称已发布插件商店或完成宿主 App 安装验收。

网页不自动保存，关闭前请下载评审文件。评审选择表示下一步安排，不表示假设已获验证。浏览器技术验收运行 `npm ci`、`npx playwright install chromium`、`npm run test:review`，测试工具仅用于开发检查，普通使用不需要 Node.js。

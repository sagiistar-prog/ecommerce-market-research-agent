# 0.3 证据分析与产品判断验收

日期：2026-09-18。范围为本地程序、插件契约、独立宿主练习和浏览器交互；不代表生产部署、行业领先或用户收益验证。

## 本次修复的用户问题

旧生成器无论品类是什么，都推荐桌面灯具人群、赠礼与灯光改造。空价格被当成零，科学计数法被正则截断，也没有可核对的观察引用。报告形式完整，却不能支撑跨品类判断。

新核心只计算输入可支持的样本结论，保留原文与出处，把缺口变成研究任务。具体产品判断由宿主 AI 形成，使用固定分析快照和原文字段校验引用。网页按结论、下一步和证据分区，支持导入、撤销、原文跳转与结构化导出。

## 已执行验证

| 检查 | 结果与边界 |
|---|---|
| Python 回归 | 33 项通过，含儿童安全座椅、宠物碗、食品包装等品类输入及数据、引用、HTTP 边界 |
| 旧 Safe Demo | 原命令成功写出新版报告，继续无网络运行 |
| 插件 JSON | 宠物碗输入成功生成 result.json/result.md，输出通过 2.0 契约 |
| 建议引用 | 宠物碗 1 个假设、3 条引用通过；错误引用、编造引文、输入变化和结果篡改均有拒绝测试 |
| 独立宿主试用 | 保温杯任务 2 个假设、11 条引用通过，第一次发现两个使用障碍后完成针对性复测 |
| 桌面与手机 | 1440px、390px Chrome 实际操作通过：示例、分析、证据跳转、CSV 导入、JSON 下载、修改后禁用导出、错误保留输入 |
| 视觉与自动可访问性 | 两个尺寸未发现页面横向溢出或脚本错误；Next actions 视图的 axe 指定 WCAG 规则无命中；不是完整认证 |
| 打包 | plugin-creator 与 skill-creator 校验通过，JavaScript 语法检查通过 |

机器记录：[浏览器](evaluation/browser-review.json)、[独立 Skill 试用](evaluation/skill-forward-test.json)。实际判断示例：[保温杯复核](evaluation/commuter-mug-review.md)。截图：[桌面](screenshots/review-desktop.png)、[手机](screenshots/review-mobile.png)、[研究任务](screenshots/review-tasks.png)。

Impeccable 的机械检测器缺少 HTML 解析依赖，退回正则模式，因此不把检测输出当成质量认证。沿用现有本机字体栈保障离线使用；蓝灰界面、原生 details、44px 控件和按需说明经浏览器检查。DESIGN.md 更新当前交互，未把检测器建议误写成用户需求。

## 复现

```bash
python -m pip install -r requirements-plugin.txt
python -m unittest discover -s tests -v
python scripts/plugin_run.py --input examples/pet-bowl-input.json --output-dir output/pet-check
python scripts/validate_decisions.py --analysis output/pet-check/result.json --decisions examples/pet-bowl-decisions.json
python scripts/plugin_run.py --input examples/commuter-mug-input.json --output-dir output/mug-check
python scripts/validate_decisions.py --analysis output/mug-check/result.json --decisions examples/commuter-mug-decisions.json
powershell -ExecutionPolicy Bypass -File scripts/portfolio_audit.ps1
```

每次使用新的输出目录。已有结果不会覆盖。完整浏览器场景和视口记录在上述 JSON 中；启动网页后可以按场景手工复核。

## 不能从这些检查推断的事情

引用能解析不等于推理正确。宿主示例是一项行为验收，不能外推模型准确率。来源 URL 与等级不自动核验，价格统计不能直接用于定价，重复宣称也不能证明市场饱和。自然语言的语义提取由宿主执行，Python 仅识别标签；网页输入纯文本时会保留原文并提示补标签。

目前没有真实参与者、生产数据接入或商业结果。后续应让目标研究人员带着合规材料完成真实决策任务，测量复核时间、无来源结论、实际采纳的假设与被否决原因。

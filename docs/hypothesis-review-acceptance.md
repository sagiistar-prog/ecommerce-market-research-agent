# 假设评审验收

日期：2026-09-18。版本0.4。本轮把本地证据分析延伸到研究者的取舍和下一步计划，未接入线上采集或客户效果数据。

## 已实现

网页导入宿主生成的假设包，重新检查引用；逐条查看原始字段、选择待测试/暂缓/拒绝并记录理由；撤销最后一次选择；下载完整JSON或Markdown阅读版；重开页面后基于相同输入恢复。未记录的草稿阻止下载，编辑输入后原有评审控件禁用。

证据快照及假设包双重绑定，改写或重排假设不能继承旧选择。所有假设默认未评审。完成评审仍保留 `validation_status: not_measured`，分母为包内全部假设，不把未评审项藏起来。

## 本地验证

- `python -m unittest discover -s tests -v`：42项全部通过，涵盖原有分析、HTTP边界、引用、重复/缺失编号、空理由、旧快照和Unicode恢复。
- README中的旧Safe Demo命令：退出0，生成报告保持兼容。
- `node --check web/app.js`：通过。
- `npm run test:review`：真实本地HTTP服务及Chrome，在1440和390宽度完成宠物碗与保温杯两个虚构类别的任务，见 [机器记录](evaluation/hypothesis-review-browser.json)。
- 浏览器额外检查无效JSON对象保留旧评审，以及空白理由报错后可重新选择未评审。浏览器异常0、横向溢出0、axe自动违规0。

[桌面截图](screenshots/hypothesis-review-1440.png)与[手机截图](screenshots/hypothesis-review-390.png)来自同次浏览器运行。桌面沿用结果区独立滚动，手机纵向阅读。Impeccable收尾保持蓝灰配色、折叠细节和原生表单，假设标题复用已有18px尺寸。

CI增加固定版本Playwright与axe开发依赖，在Chromium运行同一任务脚本并上传报告、截图和虚构导出文件。Python Safe Demo不依赖这些浏览器工具，也不会抓取外部资料。CI实际结论以对应提交的运行状态为准。

## 复现

先按README安装Python依赖，再执行：

```bash
python -m unittest discover -s tests -v
npm ci
npx playwright install chromium
npm run test:review
powershell -ExecutionPolicy Bypass -File scripts/portfolio_audit.ps1
```

测试默认使用PATH上的Python；可设置 `PYTHON` 为已安装依赖的解释器路径。测试自行启动并关闭本地服务，产物写入忽略的 `output/browser-review-*/`。不需要配置模型密钥。

## 尚未证明

测试使用虚构资料，不是用户访谈或需求验证。精确引文检查不判断语义相关性、样本代表性或假设正确性。没有自动实验执行、实际收益、多人身份审计或持久数据库；刷新前需下载评审文件。插件商店发布与宿主App安装仍未验收。桌面和手机的自动无障碍检查不等于完整WCAG认证。

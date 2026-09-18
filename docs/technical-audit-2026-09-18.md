> 这是 0.2 及以前的设计或验收记录。当前 0.3 行为与验证见 [插件契约](plugin.md) 和 [本轮验收](evidence-review-acceptance.md)。

# 技术验收 2026-09-18

修复本地 HTTP 服务未校验来源与 Host、负数或无限制请求长度的问题。新增真实 HTTP 请求回归测试。CSV数值、字段契约与离线报告测试通过。报告仍是离线规则生成，不是实时抓取的市场研究。

## 复现

`python -m pip install -r requirements-plugin.txt`

`python -m unittest discover -s tests -v`

`python scripts/plugin_run.py --input examples/plugin-input.json`

所有示例为虚构测试资料。没有真实用户参与，本轮仅为技术验收。

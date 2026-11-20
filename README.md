# 名画融合文字图 · 工具引擎

本地排版引擎：把「醒与悟」系列的金句，用本机字体渲染叠加到公版名画上，输出 1536×2048 PNG。零积分、零在线模型调用。

> 截至 2026-11-20：已产出 **102 张**，覆盖 **54 位画家**。

## 仓库结构

```
art_typeset/          # 引擎（16 模块）
  cli.py              # 统一入口 python -m art_typeset <cmd>
  recipe.py           # 配方加载与渲染
  verify.py           # 三项数字测量（对比度/强调占比/包围盒）
  diagnose.py         # 首渲诊断：FAIL 后先诊断再开药
  check.py            # 门禁：逐字/字号/冲突/布局
  preflight.py        # 排产前检查
  derive.py           # 口径派生与一致性审计
  regress.py          # golden 逐像素回归
  methodology.py      # GO·SEE·THINK·DO / PDCA / GSTD 合规复验
  presets/            # 20 份配方 qNN.json（真相源之一）
  golden/             # 快照（默认 .gitignore，可按需纳入）

_qNN_*.py             # 每张图的制作脚手架（历史留痕，引擎不依赖）
local_typeset.py      # 旧版单体脚本（只读，禁止裸调出货）
```

## 核心命令

```bash
PY="C:/Users/admin/.workbuddy-ai/binaries/python/envs/default/Scripts/python.exe"

$PY -m art_typeset check   art_typeset/presets/q34.json     # 门禁
$PY -m art_typeset render  art_typeset/presets/q34.json      # 渲染+验三项数字
$PY -m art_typeset diagnose draft.png base.png --light --recipe=q34.json  # 首渲诊断
$PY -m art_typeset derive  art_typeset/presets/q34.json      # 台账行+交付骨架
$PY -m art_typeset derive  audit                              # 六处口径一致性审计
$PY -m art_typeset check --all                                # 全部配方门禁
$PY -m art_typeset regress                                    # golden 回归
```

## 硬规格（不可退让）

- **1536×2048 PNG**，文件名 = 文字＋画家＋画名＋年份＋风格＋色彩＋`_YYYYMMDD_HHMM`
- 字号下限：标题≥72 / 正文≥28 / 英文≥25 / 款识≥19
- 对比度：标题/正文≥5:1、英文≥4:1、款识≥3.5:1
- 强调占比 8–15%；背景 std ≤25
- 中文逐字保留，句内不删字删词；`check` 内置断言
- 画家/画作全系列不重复

## 方法论

GO·SEE·THINK·DO / PDCA / GSTD，详见 `~/.workbuddy-ai/skills/local-art-typeset/SKILL.md`。

**元规则（2026-11-20 固化）**：FAIL 后先跑 `diagnose` 再开药；连续 2 次同类调参无效强制换维度。

# art_typeset · 排版工具包

> 名画融合文字图系列的**六层流水线**。本地排版零积分通道的第二代外壳。
> 建立：2026-11-10 ｜ 版本 0.3.0（2026-11-11 第三批收口）

## 为什么存在

`local_typeset.py`（1291 行 / 93 参数）继续负责**渲染**，本包负责它周围的一切：
把军规从「MEMORY.md 里 9000 字、每次开工读一遍」搬进**代码门禁**，
把 89 张图的参数从「散落在临时脚本 / 历史会话」搬进**数据资产**。

**`local_typeset.py` 保持只读**，本包通过 subprocess 调用它，输出像素级不变
（Q21 已验证 `max diff 0`）。

## 六层

| 层 | 模块 | 职责 |
|---|---|---|
| 规格 | `spec.py` | 唯一常量源：93 参数默认值、字号/对比度/强调/包围盒门槛、13 条组合冲突表、强调占比口径 |
| 门禁 | `preflight.py` | 出图前拦截：逐字断言、字号下限、敏感词、参数冲突、画布、布局约束 |
| 测量·前 | `measure.py` | 真实墨迹盒（`getbbox`）预测块高/呼吸缝/画布溢出，替代 `1.15` 经验系数 |
| **布局** | `layout.py` | **约束求解**：自动补 `title-gap` / 溢出限宽，修正项写进渲染报告 |
| 测量·后 | `verify.py` | 出图后三项数字（对比度/强调占比/包围盒）＋底色均匀度，不达标不落盘 |
| 配方 | `recipe.py` | JSON 唯一真相源 → argv 唯一编译点 → `render()` 纯函数（内置 Layout 求解） |
| 回归 | `golden.py` / `regress.py` | 快照管理 / **真回归**（重渲后逐像素比对，5 张全 max diff 0） |
| 派生 | `derive.py` | 台账行 / 交付说明骨架 / 进度口径自动生成 |
| 回溯 | `retro.py` | 从历史交付说明抽「档案级配方」，已覆盖第 66–89 张共 24 份 |
| 适配 | `shaping.py` | 文本测量/折行可替换接口（方案 4 的可吸收部分；本机 raqm=False 自动降级） |
| 入口 | `cli.py` | 统一命令行 |

## 目录

```
art_typeset/
  presets/      可复现配方（参数完整，能重渲）  q16…q22.json
  archive/      档案级配方（参数不全，但可查/可派生）  066–089.json + salvage/q066–083.json
  golden/       回归快照 + manifest.json
```

## 命令

必须用带 Pillow/numpy 的 venv 解释器：
`C:\Users\admin\.workbuddy-ai\binaries\python\envs\default\Scripts\python.exe`
（系统 Python 无 PIL，会报 `ModuleNotFoundError`）

```
cd C:\Users\admin\Documents\tietuai

check   presets/q21.json 或 art_typeset/presets/q21.json   # 只跑门禁（两种路径口径都可用）
measure presets/q22.json                                  # 布局预测
layout  presets/q22.json [--apply]                        # 约束求解（可写回）
verify  <final.png> <base.png> [--light]                  # 三项数字（亮底深字加 --light）
render  presets/q22.json <out.png> [base.png] [--light|--dark]
                                                          # 全链路：自动求解+门禁+渲染+测量
                                                          # 极性缺省自动探测，--light/--dark 显式覆盖
regress [Q21]                                             # 真回归：重渲→逐像素比对
golden  freeze <ID> <png> / golden check                  # 快照管理
shaping                                                   # 文本整形能力报告
retro   scan / retro build 24                             # 回溯
derive  presets/q22.json                                  # 台账行+交付骨架
```

### 亮底深字（浅底深墨）与极性

`verify` 的两套对比公式互斥：暗底浅字用「字亮端 p99 ÷ 底中位」，亮底深字用「底中位 ÷ 字暗端 p1」。
`render` 现在**缺省自动探测极性**：渲染完成后按「成图 vs 底图」差分墨像素的亮度中位数判定
（字比底亮 → 暗底浅字，否则亮底深字），并可用 `--light`（亮底深字）/ `--dark`（暗底浅字）显式覆盖。
探测发生在成图落盘之后、测量之前，因此**不会因为极性未定就误删**。

2026-11-11 第 90 张（Q22，亮底深字）实测：不指定极性直接 `render`，自动判为「亮底深字」，
成图与交付图 `max diff 0`、全部达标、不误删；若强制 `--dark`，仍会按旧逻辑测出 0.80:1 并删除不合格成图（预期行为）。

口径：**资产可复现率 = 可复现配方数 / `spec.TOTAL_DELIVERED`**（当前 **90**，每交付一张递增；
禁止在 methodology 或文档里另写死张数）。

## 第二批成果（2026-11-10 下午）

- **7 份配方全部补齐 `source.segments`**（逐字断言），6 份门禁全绿；
  q18 因历史 warp 缺 title-gap 带**书面豁免**（`_legacy_exempt` + `_legacy_reason`），不回溯改已成图。
- **Layout 约束求解落地**：删掉 `en-width` 的破损配方能自动补回并产出 `max diff 0` 的成图；
  抹掉 `title-gap` 能自动补 48（正是第 88 张人工修的值）。
- **真回归 5/5 max diff 0**（`regress.py` 真的重渲再比对，不是只验快照存在）。
- **golden 基线定为落盘交付图**（5 张）；缓存里的 `qXX_final.png` 部分是中间迭代版，不作基线。
- **档案级配方 24 份**（第 66–89 张）。
- **方案 4 结案**：`shaping.py` 落地，整盘换引擎正式排除，见《排版工具_方案4结案_20261110.md》。
- **Q21 v2 修订**：严格口径强调占比 20.09% → **13.43%**，落盘 `..._20261110_1545.png`，配方/golden/交付说明同步。

## 第三批成果（2026-11-11）

- **q18 收口**：历史豁免配方 5/6 → 6/6；三项数字按「交付成图 vs 底图」实测回填（`pdca.see` + `measured_by`/时间/成图 sha256）。豁免判定升级为「书面豁免 + 实测数字 + 测量口径」三件齐备。
- **methodology 审计**：`methodology plan` 9/9、`all` 方案 9/9 + 配方 8/8、`regress` 5/5 max diff 0；新增只读 `methodology facts`（7 项事实实时真值）。
- **CLI render 极性**：缺省自动探测（先落盘后测量），`--light/--dark` 显式覆盖；不达标才删图并返回 1。Q22 亮底深字端到端与交付图 **max diff 0**。
- **已出张数去硬编码**：`spec.TOTAL_DELIVERED = 90`（每交付一张递增），资产可复现率 = presets / TOTAL_DELIVERED。
- **档案回溯**：24 份档案字段回填（14 字段 +172 值；artist/painting/year 全量纠错）；66–83 **18 份内联 CLI 参数抢救**到 `archive/salvage/`，**17/18 用当前引擎重渲 max diff 0**（第 67 张 max diff 16 未过、`verified:false`），补齐 `source.segments` 后可零重渲升级为 presets。
- **新图流水线首次实跑**：第 90 张 Q22 走「配方 → check → render → verify → derive」，`check` 10/0/0、`verify --light` 三项全达标、配方重渲 max diff 0。

> 详细记录：《排版工具重构_第三批实施记录_20261111.md》＋《排版工具重构_第三批_档案回溯_20261111.md》。

## 配方结构

```json
{
  "id": "Q21", "no": 89,
  "title": "…", "body": "…|<a>强调</a>|…", "en": "…", "credit": "原作 …",
  "source": { "page": 71, "segments": ["逐字段1", "逐字段2"],
              "flat_text": "原页全文，可选；提供时才做 in 原页 校验" },
  "meta": { "artist": "…", "painting": "…", "year": "…", "score": 92,
            "layout": "…", "accent": "…", "essay": "…" },
  "params": { "只写与 spec.DEFAULTS 不同的项": "…" }
}
```

`source.segments` 是**唯一真相源**：允许整段跳过，但渲染文案去标签后必须与
各段拼接逐字相等（Q21 血的教训 —— 曾把「不会那么容易」抄成「不容易」带过 5 版）。

## 强调占比口径（禁止临时改切法）

`spec.ACCENT_POLICY = "continuous_band_with_underline_v1"`：
连续 y 区间（**含行间空白**，3px 装饰下划线会落在那里）、
分母为全部差分墨像素、分子用色相差且**禁设绝对亮度阈值**。
详见 `spec.py` 注释与《排版工具重构_第一批实施记录_20261110.md》§4。

## 边界

- **不追求消灭 93 参数**：它们是 88 张验证过的能力资产，CLI 外观原样保留。
- **不批量出图**：用户铁律，一张一张串行。
- **不改艺术字相位**：warp / perspective / 竖排 / 纹理啃噬必须像素级保真。
- 方案 3 的 **Measure→Layout 已内化**（`layout.py` 参与渲染求解，自动补 title-gap / 限宽）；
  **Paint pass 仍由 legacy 执行**（艺术字保真优先），维持现状、不重写 Pillow 绘制。
- 方案 4 的 HarfBuzz 折行外包：本机 `libraqm=False`，暂不可用；仅保留接口位。
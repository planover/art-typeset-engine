# -*- coding: utf-8 -*-
"""art_typeset · 名画融合文字图排版工具包（六层流水线）

配方层    recipe.py    JSON 唯一真相源，render(recipe, base) 纯函数
门禁层    preflight.py 参数冲突 / 逐字断言 / 字号下限 / 敏感词
测量层    verify.py    三项数字 + 底色均匀度，不达标不落盘
回归层    golden.py    历史配方重渲 max diff 0
派生层    derive.py    台账 / 交付说明 / 进度口径 自动生成
规格层    spec.py      93 参数默认值 + 硬门槛 + 冲突表（唯一常量源）

legacy 工具 local_typeset.py 保持只读，本包通过 subprocess 调用它。
"""
from . import spec, preflight, verify, recipe, golden, derive, shaping, measure, retro  # noqa: F401

__version__ = "0.1.0"

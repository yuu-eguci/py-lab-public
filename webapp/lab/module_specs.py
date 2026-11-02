from dataclasses import dataclass, field


@dataclass
class ModuleSpec:
    module: str
    description: str
    # 引数名 -> {"description": "説明"} の形です。
    args: dict[str, dict[str, str]] = field(default_factory=dict)

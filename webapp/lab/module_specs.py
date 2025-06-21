from dataclasses import dataclass, field


@dataclass
class ModuleSpec:
    module: str
    description: str
    args: dict[str, str] = field(default_factory=dict)

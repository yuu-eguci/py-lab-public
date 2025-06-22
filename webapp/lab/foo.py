from .module_specs import ModuleSpec


def get_spec() -> ModuleSpec:
    """
    モジュールの仕様を取得する関数。
    """
    return ModuleSpec(
        module="foo",
        description="Foo module for demonstration purposes",
        args={
            "arg1": {"description": "First argument for foo module"},
            "arg2": {"description": "Second argument for foo module"},
        },
    )


def main(arg1: str, arg2: str):
    """
    メイン関数 - ジェネレーター版
    """
    yield f'Starting foo module with args: {arg1}, {arg2}'
    yield f'Processing...'
    yield f'Result: foo {arg1} {arg2}'
    yield f'Completed foo module execution'


if __name__ == "__main__":
    main()

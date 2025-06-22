import time
from typing import Generator

from .module_specs import ModuleSpec


def get_spec() -> ModuleSpec:
    """
    モジュールの仕様を取得する関数。
    """
    return ModuleSpec(
        module="foo",
        description="Foo module for demonstration purposes",
        args={
            "arg1": {"description": "ひとつめの引数。文字列ならなんでもいいよ。"},
            "arg2": {"description": "ふたつめの引数。文字列ならなんでもいいよ。"},
        },
    )


def main(**args) -> Generator[str, None, None]:
    """
    Main function - generator version
    """
    arg1 = args.get("arg1", "")
    arg2 = args.get("arg2", "")

    yield "Starting foo module..."
    time.sleep(1)

    yield "Checking arguments... This takes 3 seconds."
    time.sleep(3)
    yield f"Done checking. Got '{arg1}' and '{arg2}'!"
    time.sleep(1)

    yield "Starting main task... This takes 5 seconds."
    time.sleep(5)
    yield "Main task finished!"
    time.sleep(1)

    yield "Thanks for using this module!"


if __name__ == "__main__":
    main()

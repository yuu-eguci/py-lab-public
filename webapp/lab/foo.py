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

    # yield "Starting foo module..."
    yield "foo module を開始するよー!"
    time.sleep(1)

    # yield "Checking arguments... This takes 3 seconds."
    yield "引数を検証しまーす。3秒かかりまーす。"
    time.sleep(3)
    # yield f"Done checking. Got '{arg1}' and '{arg2}'!"
    yield f"検証完了。 '{arg1}' と '{arg2}' だね!"
    time.sleep(1)

    # yield "Starting main task... This takes 5 seconds."
    yield "メインの処理を開始するよ! 5秒かかる!"
    time.sleep(5)
    # yield "Main task finished!"
    yield "メインの処理完了! つかれっす!"
    time.sleep(1)

    # yield "Thanks for using this module!"
    yield "foo module をご利用いただきありがとうございましたー。"


if __name__ == "__main__":
    main()

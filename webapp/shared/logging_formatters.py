"""
test: shared.tests.test_logging_formatters
"""
from datetime import datetime, timedelta, timezone
from logging import Formatter, LogRecord


class JSTFormatter(Formatter):

    JST = timezone(timedelta(hours=+9), 'JST')

    def formatTime(self, record: LogRecord, datefmt: str | None = None) -> str:
        """
        `record.created` を基に JST での時刻を表示。
        これを使うと logging が [2023-02-07 00:00:00,000] -> [2023-02-07 09:00:00,000] こうなる。

        Args:
            record (LogRecord): ログレコード。
            datefmt (str | None): 日付フォーマット。 '%Y-%m-%dT%H:%M:%S+09:00' などをどうぞ。

        Returns:
            str: JST での時刻文字列。
        """
        # record.created を datetime オブジェクトに変換して JST に変換
        ct: datetime = datetime.fromtimestamp(record.created, timezone.utc).astimezone(self.JST)

        # フォーマットが指定されているならそれに。
        if datefmt:
            return ct.strftime(datefmt)
        # フォーマットが指定されていないならデフォルトのフォーマットを使う。
        # NOTE: 親クラスのインスタンス変数がきっちり定義されていることを確認。
        assert self.default_time_format is not None
        assert self.default_msec_format is not None
        t = ct.strftime(self.default_time_format)
        return self.default_msec_format % (t, record.msecs)


class UTCFormatter(Formatter):

    def formatTime(self, record: LogRecord, datefmt: str | None = None) -> str:
        """
        `record.created` を基に UTC での時刻を表示。
        これを使うと logging が [2023-02-07 00:00:00,000] -> [2023-02-07 00:00:00,000] こうなる。

        Args:
            record (LogRecord): ログレコード。
            datefmt (str | None): 日付フォーマット。 '%Y-%m-%dT%H:%M:%SZ' などをどうぞ。

        Returns:
            str: UTC での時刻文字列。
        """
        # record.created を datetime オブジェクトに変換。
        ct: datetime = datetime.fromtimestamp(record.created, timezone.utc)

        # フォーマットが指定されているならそれに。
        if datefmt:
            return ct.strftime(datefmt)
        # フォーマットが指定されていないならデフォルトのフォーマットを使う。
        # NOTE: 親クラスのインスタンス変数がきっちり定義されていることを確認。
        assert self.default_time_format is not None
        assert self.default_msec_format is not None
        t = ct.strftime(self.default_time_format)
        return self.default_msec_format % (t, record.msecs)

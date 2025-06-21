"""
shared.tests.test_logging_formatters
"""

import logging
import unittest
from datetime import datetime, timedelta, timezone
from logging import LogRecord

from ..logging_formatters import JSTFormatter, UTCFormatter


class TestJSTFormatter(unittest.TestCase):
    # NOTE: なくても良い。が、あると mypy がクラス変数として cls.record あるいは self.record を認識してくれる。
    record: LogRecord

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # ログレコードを作成。 (created, msecs は自動でセットされる。)
        cls.record = LogRecord(
            name="test", level=logging.DEBUG, pathname="", lineno=0, msg="Sample message.", args=(), exc_info=None)
        # created を上書き。
        cls.record.created = datetime.timestamp(datetime(2023, 2, 7, tzinfo=timezone.utc))
        # msecs を上書き。
        cls.record.msecs = 0

    def test_default_formatter(self) -> None:
        # デフォルトの Formatter が作成するログメッセージを確認。
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
        formatted_message: str = formatter.format(self.record)
        self.assertEqual(formatted_message, "[2023-02-07 00:00:00,000] [DEBUG] Sample message.")

    def test_JSTFormatter(self) -> None:
        # JSTFormatter は自動で JST で表示することを確認。
        formatter = JSTFormatter('[%(asctime)s] [%(levelname)s] %(message)s')
        formatted_message: str = formatter.format(self.record)
        self.assertEqual(formatted_message, "[2023-02-07 09:00:00,000] [DEBUG] Sample message.")

    def test_JSTFormatter_with_datefmt(self) -> None:
        # まあ、 datefmt と一緒に使うことを想定しているので、そのテストも。
        formatter = JSTFormatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z')
        formatted_message: str = formatter.format(self.record)
        self.assertEqual(formatted_message, "[2023-02-07T09:00:00+0900] [DEBUG] Sample message.")


class TestUTCFormatter(unittest.TestCase):
    # NOTE: なくても良い。が、あると mypy がクラス変数として cls.record あるいは self.record を認識してくれる。
    record: LogRecord

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # ログレコードを作成。 (created, msecs は自動でセットされる。)
        cls.record = LogRecord(
            name="test", level=logging.DEBUG, pathname="", lineno=0, msg="Sample message.", args=(), exc_info=None)
        # created を上書き。
        JST = timezone(timedelta(hours=+9), 'JST')
        cls.record.created = datetime.timestamp(datetime(2023, 2, 7, 9, tzinfo=JST))
        # msecs を上書き。
        cls.record.msecs = 0

    def test_UTCFormatter(self) -> None:
        # UTCFormatter は自動で UTC で表示することを確認。
        formatter = UTCFormatter('[%(asctime)s] [%(levelname)s] %(message)s')
        formatted_message: str = formatter.format(self.record)
        self.assertEqual(formatted_message, "[2023-02-07 00:00:00,000] [DEBUG] Sample message.")

    def test_UTCFormatter_with_datefmt(self) -> None:
        # まあ、 datefmt と一緒に使うことを想定しているので、そのテストも。
        formatter = UTCFormatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%dT%H:%M:%SZ')
        formatted_message: str = formatter.format(self.record)
        self.assertEqual(formatted_message, "[2023-02-07T00:00:00Z] [DEBUG] Sample message.")

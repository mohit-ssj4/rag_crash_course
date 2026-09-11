import logging
import re

import pytest

from src import logger


def test_get_logger():
    log = logger.get_logger("test_module")
    assert log.name == "test_module"
    assert len(log.handlers) == 1
    assert log.propagate is False


def test_logger_no_duplicate_handlers():
    log1 = logger.get_logger("dup_module")
    log2 = logger.get_logger("dup_module")
    assert log1 is log2
    assert len(log1.handlers) == 1


def test_logger_formatting(capsys):
    log = logger.get_logger("format_module")
    log.info("Hello standardized log message!")

    # Capture stderr output
    captured = capsys.readouterr()
    stderr = captured.err

    assert "INFO" in stderr
    assert "format_module" in stderr
    assert "Hello standardized log message!" in stderr

    # Verify format pattern: [YYYY-MM-DD HH:MM:SS] [LEVEL] [MODULE] - MESSAGE
    # Regex: ^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] \[INFO\] \[format_module\] - Hello standardized log message!\s*$
    pattern = r"^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] \[INFO\] \[format_module\] - Hello standardized log message!\r?\n$"
    assert re.match(pattern, stderr) is not None

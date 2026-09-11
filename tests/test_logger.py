import importlib
import logging
import re

from src import config, logger


def test_get_logger(monkeypatch):
    # Make sure config/logger are loaded with standard settings
    monkeypatch.delenv("CONSOLE_LOGGING", raising=False)
    importlib.reload(config)
    importlib.reload(logger)
    log = logger.get_logger("test_module")
    assert log.name == "test_module"
    assert len(log.handlers) == 1
    assert log.propagate is False


def test_logger_no_duplicate_handlers(monkeypatch):
    monkeypatch.delenv("CONSOLE_LOGGING", raising=False)
    importlib.reload(config)
    importlib.reload(logger)
    log1 = logger.get_logger("dup_module")
    log2 = logger.get_logger("dup_module")
    assert log1 is log2
    assert len(log1.handlers) == 1


def test_logger_formatting(capsys, monkeypatch):
    monkeypatch.delenv("CONSOLE_LOGGING", raising=False)
    importlib.reload(config)
    importlib.reload(logger)
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


def test_logger_disabled_console(capsys, monkeypatch):
    # Disable console logging via environment
    monkeypatch.setenv("CONSOLE_LOGGING", "false")
    importlib.reload(config)
    importlib.reload(logger)

    log = logger.get_logger("silent_module")
    # Verify a NullHandler is added
    assert len(log.handlers) == 1
    assert isinstance(log.handlers[0], logging.NullHandler)

    log.info("This should not be printed anywhere!")

    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out == ""

    # Clean up state for subsequent tests
    monkeypatch.delenv("CONSOLE_LOGGING", raising=False)
    importlib.reload(config)
    importlib.reload(logger)

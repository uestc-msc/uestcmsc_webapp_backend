from datetime import datetime


def _write_log(_log: str):
    print(_log)


def _log_time() -> str:
    return datetime.now().strftime("%d/%b/%Y %H:%M:%S")


def _log(event: str, msg: str):
    _write_log(f"[{_log_time()}] [{event}] {msg}")


def log_info(info: str):
    _log('INFO', info)


def log_error(err: str):
    _log('ERROR', err)

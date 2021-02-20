from datetime import datetime


def __write_log(_log: str):
    print(_log)


def __log_time() -> str:
    return datetime.now().strftime("%d/%b/%Y %H:%M:%S")


def __log(event: str, msg: str):
    __write_log(f"[{__log_time()}] [{event}] {msg}")


def log_info(info: str):
    __log('INFO', info)


def log_error(err: str):
    __log('ERROR', err)

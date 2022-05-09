import time

def now_str():
    return time.strftime(
        "%Y-%m-%d %H-%M-%S",
        time.localtime()
    )
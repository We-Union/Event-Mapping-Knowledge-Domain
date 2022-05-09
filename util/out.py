from colorama import Back, Style

def _out(msg, tag):
    print(tag, msg, Style.RESET_ALL)


def debug_out(msg):
    _out(msg, Back.BLUE)

def error_out(msg):
    _out(msg, Back.RED)
    

def success_out(msg):
    _out(msg, Back.GREEN)

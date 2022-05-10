from colorama import Back, Style
import json

def load_json(path):
    with open(path, "r", encoding="utf-8") as fp:
        data = json.load(fp=fp)
    return data

def dump_json(obj, path):
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(obj, fp=fp, ensure_ascii=False, indent=4)

def _out(msg, tag):
    print(tag, msg, Style.RESET_ALL)


def debug_out(msg):
    _out(msg, Back.BLUE)

def error_out(msg):
    _out(msg, Back.RED)
    

def success_out(msg):
    _out(msg, Back.GREEN)

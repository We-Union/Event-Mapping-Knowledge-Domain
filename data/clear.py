# -*- encoding: utf-8 -*-
# purpose: clear " in the original relation

def remove_abnormal(text):
    result = ""
    enter = False
    for i, c in enumerate(text):
        if enter:
            if c != '"':
                result += c
            else:
                if text[i + 1] in ["}"] or text[i + 1: i + 3] in ["],", "]}"] or text[i + 1: i + 4] in [', "', ': "', ': [']:
                    result += c
                    enter = False
        else:
            result += c
            if i > 2:
                pre_str = text[i - 2: i + 1]
                if pre_str in [': "', ', "']:
                    enter = True
        
    return result

wfp = open("data/data_step1.json", "w", encoding="utf-8")
for line in open("data/data.json", "r", encoding="utf-8"):
    line = remove_abnormal(line.strip())
    wfp.write(line)
    wfp.write("\n")
wfp.close()



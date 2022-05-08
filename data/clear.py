# -*- encoding=utf-8 -*-
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

# text = """{"title": "1957 Ice Hockey World Championships", "url": "https://en.wikipedia.org/wiki/1957_Ice_Hockey_World_Championships", "desc": "The 1957 Ice Hockey World Championships were held between 24 February and 5 March 1957 at the Palace of Sports of the Central Lenin Stadium in Moscow, USSR.", "time": ["24 February–5 March"], "place": [], "joiner": [{"type": "GPE", "content": "USSR"}, {"type": "NORP", "content": "Swedish"}, {"type": "GPE", "content": "Sweden"}, {"type": "GPE", "content": "Japan"}, {"type": "NORP", "content": "European"}, {"type": "NORP", "content": "Soviets"}, {"type": "GPE", "content": "Czechoslovakia"}, {"type": "GPE", "content": "the Soviet Union"}, {"type": "PERSON", "content": "Sven "Tumba"}, {"type": "PERSON", "content": "Johansson"}]}"""
# text = remove_abnormal(text)
# print(text)
# json.loads(text)

wfp = open("data/results.json", "w", encoding="utf-8")
for line in open("data/_results.clear.json", "r", encoding="utf-8"):
    line = remove_abnormal(line.strip())
    wfp.write(line)
    wfp.write("\n")
wfp.close()



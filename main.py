import json 

demo = {}

def handle_branklet(line: str):
    desc_i = line.index("\"desc\": ")
    time_i = line.index("\"time\": ")
    print(line[desc_i + 8])
    print(line[time_i - 5])

    desc_string = line[desc_i + 8: time_i - 2]
    print(desc_string)

for line in open("data/results.clear.json", "r", encoding="utf-8"):
    try:
        line = json.loads(line)
    except:
        print(line)
        handle_branklet(line)
        exit(-1)
    joiners = line["joiner"]
    for j in joiners:
        demo[j["type"]] = j["content"]

print(demo)
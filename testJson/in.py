import json

def create_json(hotwords, script):
    if hotwords is not list:
        hotwords = [hotwords]
    print json.dumps({"Entry": [{"hotwords": hotwords, "sctript": script}]}, indent=4, separators=(',', ': '))

create_json(["ok", "google"], "/etc/script/execute1")
create_json(["quelle", "heure"], "/etc/script/execute2")
create_json(["quelle", "temps"], "/etc/script/execute3")

import json
import glados

def main(message):
    obj = json.loads(message)
    print(obj)
    if "agent" in obj:
        if obj["agent"] == "GLaDOS":
            if obj["type"] == "say":
                glados.say(obj["text"])
    return
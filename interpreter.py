import json
import glados

async def main(message):
    obj = json.loads(message)
    print(obj)
    if "agent" in obj:
        if obj["agent"] == "GLaDOS":
            if obj["type"] == "say":
                await glados.say(obj["text"])
    return
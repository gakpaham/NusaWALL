import json

def to_json(value) -> str:
    return json.dumps(value, default=str)

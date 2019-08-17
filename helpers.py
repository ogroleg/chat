import json
import base64


def pack(some_dict):
    return base64.b64encode(json.dumps(some_dict).encode('utf-8')).decode('utf-8')


def unpack(some_str):
    return json.loads(base64.b64decode(some_str.encode('utf-8')).decode('utf-8'))

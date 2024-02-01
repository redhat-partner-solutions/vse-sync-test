#!/usr/bin/env python3

import json

print(
    json.dumps(
        {
            "result": True,
            "reason": None,
            "data": {
                "baz": 99,
            },
        }
    )
)

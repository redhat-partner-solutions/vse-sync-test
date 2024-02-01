#!/usr/bin/env python3

import json

print(
    json.dumps(
        {
            "result": False,
            "reason": "something went wrong",
            "data": {
                "foo": "bar",
            },
        }
    )
)

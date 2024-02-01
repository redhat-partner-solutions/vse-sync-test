#!/bin/bash

printf '[{"path": "%s"}, "%s", {"path": "%s", "title": "rhs"}]' "${1}.png" "${1}_lhs.pdf" "${1}_rhs.pdf"

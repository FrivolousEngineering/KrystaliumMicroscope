#!/usr/bin/env python

import csv
import sys
import json


if len(sys.argv) < 2:
    print("Usage: csv2dict [file]")
    exit(1)


targets = []
actions = []
rows = []
with open(sys.argv[1], newline = "") as f:
    reader = csv.reader(f, quotechar = "'")

    first = True
    for row in reader:
        if first:
            targets = row[1:]
            first = False
        else:
            actions.append(row[0])
            rows.append(row[1:])

table = {}

for r in range(len(rows)):
    row_data = {}
    row = rows[r]
    for i in range(len(row)):
        if not row[i] or row[i].strip() == "None":
            row_data[targets[i]] = []
            continue

        try:
            decoded = json.loads(row[i])
        except json.JSONDecodeError:
            print("Invalid JSON: ", row[i])

        modifiers = []
        for key, value in decoded.items():
            operation = "add"
            if str(value).startswith("+"):
                operation = "add"
                value = value[1:]
            elif str(value).startswith("-"):
                operation = "add"
            elif str(value).startswith("*"):
                operation = "mul"
                value = value[1:]
            elif str(value).startswith("="):
                operation = "set"
                value = value[1:]

            modifiers.append(f"ParameterModifier(\"{key}\", {value}, \"{operation}\")")

        row_data[targets[i]] = modifiers
    table[actions[r]] = row_data


output = json.dumps(table, indent = 4)

with open("effect_table.py", "w") as f:
    f.write("from .types import Color, ParameterModifier\n")
    f.write("\n")
    f.write("effect_table = ")

    for line in output.splitlines(True):
        if line.strip().startswith("\"ParameterModifier"):
            line = line.replace("\"Param", "Param")
            line = line.replace(r'\"', r'"')
            line = line.replace("\"Color", "Color")
            line = line.replace(r')"', ')')
            f.write(line)
        else:
            f.write(line)

    f.write("\n")

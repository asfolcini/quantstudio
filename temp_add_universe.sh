#!/usr/bin/env python3
import sys

# Read the file and find the line at position 674 which previously was 874.
# Add a test menu case for universe mode after the pause

with open('/Users/alberto.sfolcini/Development/quantstudio/ui/tui.py', 'r+') as f:
    lines = f.readlines()
    # Insert after "pause()" on line 874
    INSERT_LINE = 874
    lines.insert(INSERT_LINE, "\n        elif ch == \"2\":  # Run on universe\n")
    lines.insert(INSERT_LINE + 1, "            print(\"UNIVERSE ANALYSIS COMING SOON\")\n")
    lines.insert(INSERT_LINE + 2, "            pause()\n")
    lines.insert(INSERT_LINE + 3, "            continue\n")
    f.seek(0)
    f.writelines(lines)
    f.truncate()

print("✅ Added universe menu placeholder successfully")

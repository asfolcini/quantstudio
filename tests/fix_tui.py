#!/usr/bin/env python3

# Read file
with open('/Users/alberto.sfolcini/Development/quantstudio/ui/tui.py', 'r') as f:
    lines = f.readlines()

# Fix line 823 (index 822) - fix Edge analysis error syntax
if 'console.print("[red]Edge analysis error:[/), str(e)")' in lines[822]:
    lines[822] = lines[822].replace('"[red]Edge analysis error:[/), str(e)")', '"[red]Edge analysis error:[/red]", str(e))')

# Write back
with open('/Users/alberto.sfolcini/Development/quantstudio/ui/tui.py', 'w') as f:
    f.writelines(lines)

print("Fixed syntax errors in tui.py")
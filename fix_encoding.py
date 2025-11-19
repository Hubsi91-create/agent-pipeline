import os

env_path = "backend/.env"

content = ""
try:
    # Try UTF-16 (PowerShell default)
    with open(env_path, "r", encoding="utf-16") as f:
        content = f.read()
    print("Read as UTF-16")
except:
    try:
        # Try UTF-8
        with open(env_path, "r", encoding="utf-8") as f:
            content = f.read()
        print("Read as UTF-8")
    except:
        # Try CP1252 (Windows default)
        with open(env_path, "r", encoding="cp1252") as f:
            content = f.read()
        print("Read as CP1252")

# Clean up BOM if present
if content.startswith('\ufeff'):
    content = content[1:]

# Write back as UTF-8
with open(env_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Saved as UTF-8")

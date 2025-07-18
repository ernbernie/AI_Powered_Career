import os

output_file = "all_code_dump.txt"

# Directories and files to skip
exclude_dirs = {'.venv', '.env', '__pycache__', '.pytest_cache', 'site-packages', 'dist', 'build'}
exclude_files = {'.gitignore', 'Procfile'}

# Extensions to include
included_extensions = {'.html', '.css', '.js', '.py', '.txt', '.md'}

# Keywords to ignore from paths (e.g. .git/objects)
excluded_path_keywords = ['.git/objects', '.git/refs', '.git/info']

py_files = []

def build_tree(path=".", prefix=""):
    lines = []
    try:
        entries = sorted(os.listdir(path))
    except Exception:
        return lines

    entries = [e for e in entries if e not in exclude_dirs]
    for i, entry in enumerate(entries):
        full_path = os.path.join(path, entry)
        rel_path = os.path.relpath(full_path, ".").replace("\\", "/")
        if any(keyword in rel_path for keyword in excluded_path_keywords):
            continue
        connector = "└── " if i == len(entries) - 1 else "├── "
        if os.path.isdir(full_path):
            lines.append(prefix + connector + entry + "/")
            lines.extend(build_tree(full_path, prefix + ("    " if i == len(entries) - 1 else "│   ")))
        else:
            if any(entry.endswith(ext) for ext in included_extensions) and entry not in exclude_files:
                lines.append(prefix + connector + entry)
    return lines

# Collect relevant files
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    for file in files:
        full_path = os.path.join(root, file)
        rel_path = os.path.relpath(full_path, ".").replace("\\", "/")
        if any(keyword in rel_path for keyword in excluded_path_keywords):
            continue
        if (any(file.endswith(ext) for ext in included_extensions) and file not in exclude_files):
            py_files.append(full_path)

# Write output
with open(output_file, 'w', encoding='utf-8') as out:
    # 1. Project Tree
    out.write("PROJECT DIRECTORY STRUCTURE:\n")
    out.write("\n".join(build_tree()) + "\n\n")
    out.write("=" * 60 + "\n\n")

    # 2. Code Files
    for py_file in sorted(py_files, key=lambda f: (0 if 'README.md' in f else 1, f)):
        display_name = py_file.lstrip('./\\')
        out.write(f"{display_name}:\n")
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                out.write(f.read())
        except UnicodeDecodeError:
            with open(py_file, 'r', encoding='utf-8', errors='replace') as f:
                out.write(f.read())
                out.write("\n\n[⚠️ WARNING: UnicodeDecodeError - Non-UTF8 characters replaced]\n")
        out.write("\n\n" + "="*60 + "\n\n")

print(f"✅ Scraped clean code and project structure to {output_file}")

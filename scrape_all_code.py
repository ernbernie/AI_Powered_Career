import os

# Define the output file (overwrites each run)
output_file = "all_code_dump.txt"

# Define directories and files to exclude
exclude_dirs = {'.venv', '.env', '__pycache__', '.pytest_cache', 'site-packages', 'dist', 'build'}
exclude_files = {'.gitignore', 'requirements.txt', 'Procfile', 'README.md'}  # Auxiliary files to skip

# List of file types you want to include (your custom code)
included_extensions = {'.html', '.css', '.js', '.py'}

# Collect only your custom files from project directories
py_files = []

for root, dirs, files in os.walk('.'):
    # Modify dirs in place to skip excluded directories
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    
    # Only process files with your specified extensions, excluding auxiliary files
    for file in files:
        if (any(file.endswith(ext) for ext in included_extensions) and 
            file not in exclude_files):
            py_files.append(os.path.join(root, file))

# Write to output file, overwriting previous content
with open(output_file, 'w', encoding='utf-8') as out:
    for py_file in sorted(py_files):
        # Clean up the file path for display, removing leading ./ or \
        display_name = py_file.lstrip('./\\')
        out.write(f"{display_name}:\n")
        with open(py_file, 'r', encoding='utf-8') as f:
            out.write(f.read())
        out.write("\n\n" + "="*60 + "\n\n")

print(f"All custom code has been saved to {output_file}, overwriting previous content")
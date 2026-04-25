import os

# The files we actually care about for context
TARGET_FILES = ['models.py', 'views.py', 'urls.py', 'forms.py', 'admin.py']
# Folders to ignore so we don't copy thousands of useless files
IGNORE_DIRS = ['venv', 'env', '__pycache__', 'migrations', '.git', 'static', 'media']

with open('complete_codebase.txt', 'w', encoding='utf-8') as outfile:
    for root, dirs, files in os.walk('.'):
        # Remove ignored directories from the search
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            # We want the target Python files and any HTML templates
            if file in TARGET_FILES or file.endswith('.html'):
                filepath = os.path.join(root, file)
                outfile.write(f"\n{'='*60}\n")
                outfile.write(f"FILE: {filepath}\n")
                outfile.write(f"{'='*60}\n\n")
                try:
                    with open(filepath, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f"Could not read file: {e}\n")

print("Done! Look for complete_codebase.txt in your folder and upload it to Gemini.")
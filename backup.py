import os
import zipfile
import datetime

def make_backup():
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    zip_filename = os.path.join(desktop, f"Respaldo_Galletas_System_{timestamp}.zip")
    
    source_dir = r"d:\galletas-system-20260410T155609Z-3-001\galletas-system"
    
    exclude_dirs = {'node_modules', 'venv', '.git', '__pycache__', 'dist', 'dist-electron'}
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)
    
    print(f"Backup created at: {zip_filename}")

if __name__ == "__main__":
    make_backup()

import os
import shutil
import glob
import logging
import zipfile
import datetime

logging.basicConfig(
    filename="Organiser.log", 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

print("Smart File Manager & Backup System")
print("=" * 40)
logging.info("Script Started")

FILE_TYPES = {
    "Images": [".jpg", ".jpeg", ".png", ".svg", ".gif", ".bmp"],
    "PDFs": [".pdf"],
    "Documents": [".txt", ".docx", ".doc", ".rtf"],
    "Data": [".csv", ".xlsx", ".xls", ".json"],
    "Archive": [".zip", ".rar", ".7z"],
    "Videos": [".mp4", ".avi", ".mov", ".mkv"]
}

def create_folder(base_path):
    folders_created = []

    for folder in FILE_TYPES.keys():
        folder_path = os.path.join(base_path, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            folders_created.append(folder)
            print(f"Created Folder: {folder}")
            logging.info(f"Created Folder: {folder}")

    other_path = os.path.join(base_path, "Other")
    if not os.path.exists(other_path):
        os.makedirs(other_path)
        folders_created.append("Other")
        print(f"Created Folder: Other")
        logging.info(f"Created Folder: Other")
    return folders_created

def organize_files(source_path):
    """Move Files to appropriate folders based on extension"""
    stats = {}
    files_moved = 0

    for folder in FILE_TYPES.keys():
        stats[folder] = 0
    stats["Other"] = 0

    all_files = glob.glob(os.path.join(source_path, "*.*"))

    print(f"\nFound {len(all_files)} files to organise....")
    logging.info(f"Found {len(all_files)} files")

    for file_path in all_files:
        filename = os.path.basename(file_path)
        extension = os.path.splitext(filename)[1].lower()

        if filename == "file_organizer.py" or filename.startswith("backup_"):
            continue
        moved = False
        for folder, extensions in FILE_TYPES.items():
           
            if extension in extensions:
                destination = os.path.join(source_path, folder, filename)
                shutil.move(file_path, destination)
                stats[folder] += 1
                files_moved += 1
                moved = True
                print(f"{filename} -> {folder}/")
                logging.info(f"Moved: {filename} -> {folder}/")
                break
        if not moved: 
            destination = os.path.join(source_path, "Other", filename)
            shutil.move(file_path, destination)
            stats["Other"] += 1
            files_moved += 1 
            print(f"{filename} ->  Other/")
            logging.info(f"Moved: {filename} -> Other/")
    return stats, files_moved

def create_backup(source_path):
    """Create a ZIP backup of all files"""

    today = datetime.datetime.now().strftime('%y%m%d')
    backup_name = f"backup_{today}.zip"
    backup_path = os.path.join(source_path, backup_name)

    print(f"\nCreating Backup: {backup_name}")
    logging.info(f"Creating Backup: {backup_name}")

    with zipfile.ZipFile(backup_path, "w") as zip_file:
        for root, dirs, files in os.walk(source_path):
            if backup_name in files:
                continue
            for file in files:
                if file == "file_organizer.py":
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_path)
                zip_file.write(file_path, arcname)
    size_bytes = os.path.getsize(backup_path)
    size_mb = size_bytes / (1024 * 1024)

    print(f"Backup Created: {backup_name} ({size_mb:.2f} MB)")
    logging.info(f"Backup Created: {backup_name} ({size_mb:.2f} MB)")
    return backup_name, size_mb

def generate_report(source_path, stats, total_files, backup_name, backup_size):
    """Create a Summary Report of what was organized"""
    report_path = os.path.join(source_path, "Summary_Report.txt")

    with open(report_path, "w") as report:
        report.write("=" * 50 + "\n")
        report.write("FILE ORGANIZATION SUMMARY REPORT\n")
        report.write("=" * 50 + "\n")
        report.write(f"Date: {datetime.datetime.now().strftime('%y%m%d %H:%M:%S')}\n")
        report.write(f"Source Folder: {source_path}\n\n")
        report.write("-" * 30 + "\n")
        report.write("FILES ORGANISE:\n")
        report.write("-" * 30 + "\n")

        for folder, count in stats.items():
            report.write(f"{folder}: {count} files\n")
        report.write(f"\nTotal files organized: {total_files}\n\n")
        report.write("-" * 30 + "\n")
        report.write("BACKUP INFORMATION:\n")
        report.write("-" * 30 + "\n")
        report.write(f"Backup file: {backup_name}\n")
        report.write(f"Backup size: {backup_size:.2f} MB\n\n")

        report.write("=" * 50 + "\n")
        report.write("END OF REPORT\n")
        report.write("=" * 50 + "\n")
    print(f"\n Report Saved: Summary_Report.txt")
    logging.info("Report Generated")
    return report_path

def main():
    """Main function to run the file organizer"""

    source_path = input("Enter folder path to organize (press enter for downloads): ")
    if not source_path:
        source_path = os.path.expanduser("~/Downloads")
    print(f"Target Folder: {source_path}")
    print("-" * 40)

    if not os.path.exists(source_path):
        print(f"Error: Folder '{source_path}' does not exist!")
        logging.error(f"Folder not Found: {source_path}")
        return

    print("\nStep1: Creating Folders...")
    created = create_folder(source_path)

    print("\nStep2: Organizing files...")
    stats, total_files = organize_files(source_path)
    if total_files == 0:
        print("\n No Files To Organize!")
        return

    print("\nStep3: Creating Backup...")
    backup_name, backup_size = create_backup(source_path)

    print("\nStep4: Generating Report...")
    report_path = generate_report(source_path, stats, total_files, backup_name, backup_size)

    print("\n" + "=" * 50)
    print("ORGANIZATION COMPLETE!")
    print("=" * 50)
    print(f"\n Summary: ")
    for folder, count in stats.items():
        if count > 0:
            print(f"{folder}: {count} files")
    print(f"\nTotal files organized: {total_files}")
    print(f"Backup: {backup_name} ({backup_size:.2f} MB)")
    print(f"Report: Summary_Report.txt")
    print("\n" + "=" * 50)

    logging.info(f"Organization complete: {total_files} file processed")
    print("\n Done! Check your folder for the organized files.")

if __name__ == "__main__":
    main()

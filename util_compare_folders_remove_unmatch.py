import os
import sys
from pathlib import Path

def get_files_without_extension(folder):
    """Return a set of file base names (without extension) in the folder."""
    return set(f.stem for f in Path(folder).iterdir() if f.is_file())

def delete_unmatched_files(folder, other_basenames):
    """Delete files in folder that do not have a matching basename in other_basenames."""
    for f in Path(folder).iterdir():
        if f.is_file() and f.stem not in other_basenames:
            print(f"Deleting: {f}")
            f.unlink()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <folder1> <folder2>")
        sys.exit(1)

    folder1 = sys.argv[1]
    folder2 = sys.argv[2]

    basenames1 = get_files_without_extension(folder1)
    basenames2 = get_files_without_extension(folder2)

    # Files present in folder1 but not in folder2
    delete_unmatched_files(folder1, basenames2)
    # Files present in folder2 but not in folder1
    delete_unmatched_files(folder2, basenames1)

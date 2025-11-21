import os
import json

# Configuration variables
TXT_FOLDER = "/Users/tenchc/Desktop/test"  # Path to folder containing YOLO .txt annotation files
CLASSES_DICT_NEW = {'bitcoin': 0, 'board': 1, 'creditcard': 2, 'money': 3, 'piggybank': 4} # Path to JSON file mapping old classes (or Python dict)
CLASSES_DICT_OLD = {'board': 0, 'money': 1, 'bitcoin': 2, 'piggybank': 3, 'creditcard': 4}  # Path to JSON file mapping new classes (or Python dict)

def load_class_dict(dict_input):
    """
    Loads a class mapping dictionary.
    Accepts either a path to a JSON file or a Python dict.
    """
    if isinstance(dict_input, str):
        # Assume it's a JSON file path
        with open(dict_input, 'r') as f:
            mapping = json.load(f)
    elif isinstance(dict_input, dict):
        mapping = dict_input
    else:
        raise ValueError("Dictionary input must be either a file path or a Python dict")
    return mapping

def get_txt_files(folder):
    """
    Returns a list of paths to all .txt files in the specified folder.
    """
    return [
        os.path.join(folder, fname)
        for fname in os.listdir(folder)
        if fname.endswith(".txt") and os.path.isfile(os.path.join(folder, fname))
    ]

def replace_classes_in_file(txt_file_path, classes_dict_old, classes_dict_new):
    """
    Replaces class IDs in a YOLO .txt file based on the mapping from old to new class dictionaries.
    @param txt_file_path: Path to the .txt file to process
    @param classes_dict_old: Dictionary mapping class names to old class IDs
    @param classes_dict_new: Dictionary mapping class names to new class IDs
    """
    # Create reverse mapping: old_id -> class_name
    old_id_to_name = {v: k for k, v in classes_dict_old.items()}
    
    # Read the file
    with open(txt_file_path, 'r') as f:
        lines = f.readlines()
    
    # Process each line
    updated_lines = []
    for line in lines:
        line = line.strip()
        if not line:  # Skip empty lines
            updated_lines.append(line)
            continue
        
        parts = line.split()
        if len(parts) < 5:  # YOLO format requires at least 5 parts (class_id x y w h)
            print(f"Warning: Invalid line format in {txt_file_path}: {line}")
            updated_lines.append(line)
            continue
        
        old_class_id = parts[0]
        
        # Find the class name for this old class ID
        try:
            old_class_id_int = int(old_class_id)
            class_name = old_id_to_name.get(old_class_id_int)
            
            if class_name is None:
                print(f"Warning: Class ID {old_class_id} not found in old classes dict for {txt_file_path}")
                updated_lines.append(line)
                continue
            
            # Get the new class ID for this class name
            new_class_id = classes_dict_new.get(class_name)
            
            if new_class_id is None:
                print(f"Warning: Class name '{class_name}' not found in new classes dict for {txt_file_path}")
                updated_lines.append(line)
                continue
            
            # Replace the old class ID with the new one
            if old_class_id_int != new_class_id:
                print(f"Replacing class ID {old_class_id_int} -> {new_class_id} ({class_name}) in {os.path.basename(txt_file_path)}")
            parts[0] = str(new_class_id)
            updated_lines.append(' '.join(parts))
            
        except ValueError:
            print(f"Warning: Invalid class ID '{old_class_id}' in {txt_file_path}")
            updated_lines.append(line)
    
    # Write the updated content back to the file
    with open(txt_file_path, 'w') as f:
        f.write('\n'.join(updated_lines))
        if updated_lines:  # Add newline at end if file had content
            f.write('\n')

def main():
    # Load old and new class dicts
    classes_dict_old = load_class_dict(CLASSES_DICT_OLD)
    classes_dict_new = load_class_dict(CLASSES_DICT_NEW)

    # Find all .txt files in folder
    txt_files = get_txt_files(TXT_FOLDER)

    print(f"Loaded {len(txt_files)} .txt files from {TXT_FOLDER}.")
    print(f"Old classes dict: {classes_dict_old}")
    print(f"New classes dict: {classes_dict_new}")
    
    # Process each .txt file
    processed_count = 0
    for txt_file in txt_files:
        replace_classes_in_file(txt_file, classes_dict_old, classes_dict_new)
        processed_count += 1
    
    print(f"Processed {processed_count} .txt files.")

if __name__ == "__main__":
    main()

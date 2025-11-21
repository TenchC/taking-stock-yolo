import os
import json
import pandas as pd
from pathlib import Path
import shutil

PROD_DIR = "/Users/tenchc/Documents/GitHub/taking-stock-yolo-production"
OUTPUT_DIR = PROD_DIR + "/sorted_images"
PROD_DIR = PROD_DIR + "/labeled_images_nov19"
IMAGES_DIR = PROD_DIR + "/images"
LABELS_DIR = PROD_DIR + "/labels"
CATEGORIES_JSON = json.load(open(PROD_DIR + '/notes.json'))

print(f"WORKING DIR: {PROD_DIR}")
print(f"IMAGES DIR: {IMAGES_DIR}")
print(f"LABELS DIR: {LABELS_DIR}")

def load_categories_from_json(json_data):
    """
    Loads categories from a JSON dict (expects a dict with a 'categories' list of {'id':..., 'name':...})
    and adds each category's name and id to the global CATEGORIES dict.
    Can accept either a file path (str) or a dictionary.
    """
    CATEGORIES= {}
    # If json_data is a string, treat it as a file path and load it
    if isinstance(json_data, str):
        with open(json_data, 'r') as f:
            data = json.load(f)
    else:
        # Otherwise, assume it's already a dictionary
        data = json_data
    
    for cat in data.get('categories', []):
        CATEGORIES[cat['name']] = cat['id']
    print(f"CATEGORIES: {CATEGORIES}")
    return CATEGORIES

def load_images_and_labels():
    images = [f for f in os.listdir(IMAGES_DIR) if f != '.DS_Store']
    labels = [f for f in os.listdir(LABELS_DIR) if f != '.DS_Store']
    return images, labels

def move_multiple_label_files(image_file, label_file):
    """
    Move image and label files with multiple labels to OUTPUT_DIR/multiple_label/{images,labels}
    @param image_file: The image filename
    @param label_file: The label filename
    """
    multiple_label_dir_images = Path(OUTPUT_DIR) / 'multiple_label' / 'images'
    multiple_label_dir_labels = Path(OUTPUT_DIR) / 'multiple_label' / 'labels'
    multiple_label_dir_images.mkdir(parents=True, exist_ok=True)
    multiple_label_dir_labels.mkdir(parents=True, exist_ok=True)
    
    # Move image - construct full source path from IMAGES_DIR
    if image_file is not None:
        src_img = Path(IMAGES_DIR) / image_file
        if src_img.exists():
            dest_img = multiple_label_dir_images / image_file
            src_img.replace(dest_img)
            print(f"MOVE_MULTIPLE_LABEL: Moved image {image_file} to {dest_img}")
    
    # Move label - construct full source path from LABELS_DIR
    if label_file is not None:
        src_lbl = Path(LABELS_DIR) / label_file
        if src_lbl.exists():
            dest_lbl = multiple_label_dir_labels / label_file
            src_lbl.replace(dest_lbl)
            print(f"MOVE_MULTIPLE_LABEL: Moved label {label_file} to {dest_lbl}")

def filter_empty_labels(df):
    """
    Filter the dataframe by empty labels and move the images and labels to the OUTPUT_DIR/empty_label/{images,labels}
    @param df: The dataframe to filter
    """
    # Move images and labels with empty labels to OUTPUT_DIR/empty_label/{images,labels}
    empty_label_dir_images = Path(OUTPUT_DIR) / 'empty_label' / 'images'
    empty_label_dir_labels = Path(OUTPUT_DIR) / 'empty_label' / 'labels'
    # print(f"FILTER_EMPTY_LABELS: Moving empty labels to {empty_label_dir_images} and {empty_label_dir_labels}")
    empty_label_dir_images.mkdir(parents=True, exist_ok=True)
    empty_label_dir_labels.mkdir(parents=True, exist_ok=True)

    empty_df = df[df['label_empty'] == True]
    print(f"FILTER_EMPTY_LABELS: {len(empty_df)} images without labels")
    for _, row in empty_df.iterrows():
        print(f"FILTER_EMPTY_LABELS:Moving image: {row['image']} and label: {row['label']}")
        # Move image - construct full source path from IMAGES_DIR
        if row['image'] is not None:
            src_img = Path(IMAGES_DIR) / row['image']
            if src_img.exists():
                dest_img = empty_label_dir_images / row['image']
                src_img.replace(dest_img)
        # Move label (if it exists) - construct full source path from LABELS_DIR
        if row['label'] is not None:
            src_lbl = Path(LABELS_DIR) / row['label']
            if src_lbl.exists():
                dest_lbl = empty_label_dir_labels / row['label']
                src_lbl.replace(dest_lbl)
    print(f"FILTER_EMPTY_LABELS:Moved {len(empty_df)} images and labels to {empty_label_dir_images} and {empty_label_dir_labels}")

def filter_by_category(df, category):
    """
    Filter the dataframe by category and move the images and labels to the OUTPUT_DIR/{category}/{images,labels}
    @param df: The dataframe to filter
    @param category: The category to filter by
    """
    # Move images and labels with the given category to OUTPUT_DIR/{category}/{images,labels}
    category_dir_images = Path(OUTPUT_DIR) / str(category) / 'images'
    category_dir_labels = Path(OUTPUT_DIR) / str(category) / 'labels'
    category_dir_images.mkdir(parents=True, exist_ok=True)
    category_dir_labels.mkdir(parents=True, exist_ok=True)

    category_df = df[df['category'] == category]
    # Reverse lookup: find category name from category ID
    category_name = None
    for name, cat_id in CATEGORIES.items():
        if cat_id == category:
            category_name = name
            break
    print(f"FILTER_BY_CATEGORY: {len(category_df)} images with category {category} ({category_name})")
    for _, row in category_df.iterrows():
        print(f"FILTER_BY_CATEGORY: Moving image: {row['image']} and label: {row['label']}")
        # Move image - construct full source path from IMAGES_DIR
        if row['image'] is not None:
            src_img = Path(IMAGES_DIR) / row['image']
            if src_img.exists():
                dest_img = category_dir_images / row['image']
                src_img.replace(dest_img)
        # Move label (if it exists) - construct full source path from LABELS_DIR
        if row['label'] is not None:
            src_lbl = Path(LABELS_DIR) / row['label']
            if src_lbl.exists():
                dest_lbl = category_dir_labels / row['label']
                src_lbl.replace(dest_lbl)
    print(f"FILTER_BY_CATEGORY: Moved {len(category_df)} images and labels to {category_dir_images} and {category_dir_labels}")



images, labels = load_images_and_labels()
CATEGORIES = load_categories_from_json(CATEGORIES_JSON)


def create_df_from_images_and_labels(images, labels, categories):
    df_rows = []
    for image_file in images:
        # Assume label file has the same stem as image but .txt
        base_name, _ = os.path.splitext(image_file)
        label_file = base_name + '.txt'
        label_path = os.path.join(LABELS_DIR, label_file)
        image_path = os.path.join(IMAGES_DIR, image_file)

        # Determine if label file exists and if empty
        if label_file in labels:
            with open(label_path, 'r') as lf:
                label_lines = [line.strip() for line in lf if line.strip()]
            label_empty = (len(label_lines) == 0)
            # If not empty, fill in category/bbox per line
            if not label_empty:
                # If label has more than 1 line, move to multiple_label folder and skip
                if len(label_lines) > 1:
                    move_multiple_label_files(image_file, label_file)
                    continue
                # If label has exactly 1 line, process it
                for line in label_lines:
                    parts = line.split()
                    if len(parts) == 5:
                        category_id = parts[0]
                        bbox = ' '.join(parts[1:5])
                    else:
                        print(f"Label file is not valid: {label_file}, num parts: {len(parts)} in line {line}")
                        category_id = None
                        bbox = None
                    # Store category id (as int if possible, else None)
                    try:
                        category_id_out = int(category_id) if category_id is not None else None
                    except Exception:
                        category_id_out = category_id
                    df_rows.append({
                        'image': image_file,
                        'label': label_file,
                        'label_empty': label_empty,
                        'category': category_id_out,
                        'bbox': bbox
                    })
            else:
                # label exists, but is empty
                df_rows.append({
                    'image': image_file,
                    'label': label_file,
                    'label_empty': True,
                    'category': None,
                    'bbox': None
                })
        else:
            # No label file for this image
            print(f"No label file for this image: {image_file}")
            df_rows.append({
                'image': image_file,
                'label': None,
                'label_empty': True,
                'category': None,
                'bbox': None
            })
    df = pd.DataFrame(df_rows, columns=['image', 'label', 'label_empty', 'category', 'bbox'])
    return df

df = create_df_from_images_and_labels(images, labels, CATEGORIES)

print("DF: ",df.head())


filter_empty_labels(df)
filter_by_category(df, 0)
filter_by_category(df, 4)

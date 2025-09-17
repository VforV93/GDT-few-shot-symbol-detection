#!/usr/bin/env python3
"""
Script to remove specific categories and their annotations from a COCO annotation file.

Usage:
    python clean_annotation_file_from_labels.py <annotation_file> <category_ids> [output_file]

Example:
    python clean_annotation_file_from_labels.py annotations.json "0,39" cleaned_annotations.json
"""

import json
import argparse
import sys
from pathlib import Path


def clean_coco_annotations(annotation_file_path, category_ids_to_remove, output_file_path=None):
    """
    Remove specified categories and their annotations from a COCO annotation file.
    
    Args:
        annotation_file_path (str): Path to the input COCO annotation file
        category_ids_to_remove (list): List of category IDs to remove
        output_file_path (str, optional): Path for the output file. If None, overwrites input file.
    
    Returns:
        dict: Statistics about what was removed
    """
    # Load the annotation file
    try:
        with open(annotation_file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Annotation file not found: {annotation_file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON file: {e}")
    
    # Validate that required fields exist
    if "categories" not in data:
        raise ValueError("'categories' field not found in annotation file")
    if "annotations" not in data:
        raise ValueError("'annotations' field not found in annotation file")
    
    # Convert category IDs to set for faster lookup
    category_ids_to_remove = set(category_ids_to_remove)
    
    # Count original data
    original_categories_count = len(data["categories"])
    original_annotations_count = len(data["annotations"])
    
    # Remove categories
    categories_before = data["categories"].copy()
    data["categories"] = [cat for cat in data["categories"] if cat["id"] not in category_ids_to_remove]
    categories_removed = [cat for cat in categories_before if cat["id"] in category_ids_to_remove]
    
    # Remove annotations with the specified category IDs
    annotations_before = data["annotations"].copy()
    data["annotations"] = [ann for ann in data["annotations"] if ann["category_id"] not in category_ids_to_remove]
    annotations_removed = [ann for ann in annotations_before if ann["category_id"] in category_ids_to_remove]
    
    # Determine output file path
    if output_file_path is None:
        output_file_path = annotation_file_path
    
    # Save the cleaned annotation file
    try:
        with open(output_file_path, 'w') as f:
            json.dump(data, f, indent=2 if output_file_path != annotation_file_path else None)
    except Exception as e:
        raise IOError(f"Failed to write output file: {e}")
    
    # Prepare statistics
    stats = {
        "categories_removed_count": len(categories_removed),
        "categories_removed": categories_removed,
        "annotations_removed_count": len(annotations_removed),
        "original_categories_count": original_categories_count,
        "original_annotations_count": original_annotations_count,
        "final_categories_count": len(data["categories"]),
        "final_annotations_count": len(data["annotations"]),
        "output_file": output_file_path
    }
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Remove specific categories and their annotations from a COCO annotation file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Remove categories 0 and 39, save to new file
    python clean_annotation_file_from_labels.py annotations.json "0,39" cleaned_annotations.json
    
    # Remove categories 0 and 39, overwrite original file
    python clean_annotation_file_from_labels.py annotations.json "0,39"
    
    # Remove single category
    python clean_annotation_file_from_labels.py annotations.json "5" cleaned_annotations.json
        """
    )
    
    parser.add_argument(
        "annotation_file",
        help="Path to the COCO annotation file"
    )
    
    parser.add_argument(
        "category_ids",
        help="Comma-separated list of category IDs to remove (e.g., '0,39' or '5')"
    )
    
    parser.add_argument(
        "output_file",
        nargs="?",
        default=None,
        help="Output file path (optional, defaults to overwriting input file)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed information about what was removed"
    )
    
    args = parser.parse_args()
    
    # Parse category IDs
    try:
        category_ids = [int(id_str.strip()) for id_str in args.category_ids.split(",")]
    except ValueError:
        print("Error: Category IDs must be integers separated by commas", file=sys.stderr)
        sys.exit(1)
    
    if not category_ids:
        print("Error: At least one category ID must be specified", file=sys.stderr)
        sys.exit(1)
    
    # Validate input file exists
    if not Path(args.annotation_file).exists():
        print(f"Error: Annotation file not found: {args.annotation_file}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Clean the annotations
        stats = clean_coco_annotations(
            args.annotation_file,
            category_ids,
            args.output_file
        )
        
        # Print summary
        print(f"✓ Successfully cleaned annotation file")
        print(f"  Categories removed: {stats['categories_removed_count']} (from {stats['original_categories_count']} to {stats['final_categories_count']})")
        print(f"  Annotations removed: {stats['annotations_removed_count']} (from {stats['original_annotations_count']} to {stats['final_annotations_count']})")
        print(f"  Output file: {stats['output_file']}")
        
        if args.verbose and stats['categories_removed']:
            print("\nRemoved categories:")
            for cat in stats['categories_removed']:
                print(f"  - ID {cat['id']}: {cat['name']} (supercategory: {cat.get('supercategory', 'none')})")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

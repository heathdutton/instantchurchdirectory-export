"""
Data export utilities for JSON generation
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Union, List, Dict


async def export_to_json(
    category: str,
    data: Union[List, Dict],
    base_dir: str = "exports"
) -> str:
    """
    Export data to JSON file with metadata.

    Args:
        category: Category name (families, staff, groups, etc.)
        data: Data to export (list of records or dict)
        base_dir: Base export directory

    Returns:
        str: Path to the created JSON file
    """
    # Create export directory
    export_dir = os.path.join(base_dir, category)
    Path(export_dir).mkdir(parents=True, exist_ok=True)

    # Prepare data with metadata
    if isinstance(data, list):
        total_records = len(data)
        data_key = category
    else:
        # For dict data (like events with birthdays and anniversaries)
        total_records = sum(len(v) if isinstance(v, list) else 1 for v in data.values())
        data_key = None

    export_data = {
        "metadata": {
            "export_date": datetime.utcnow().isoformat() + "Z",
            "total_records": total_records,
            "source": "https://members.instantchurchdirectory.com"
        }
    }

    # Add the actual data
    if data_key:
        export_data[data_key] = data
    else:
        export_data.update(data)

    # Write to file
    filepath = os.path.join(export_dir, f"{category}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    print(f"  Exported {total_records} records to {filepath}")
    return filepath


def create_export_structure(base_dir: str = "exports") -> None:
    """
    Create the export directory structure.

    Args:
        base_dir: Base export directory
    """
    categories = [
        "families/photos",
        "staff/photos",
        "groups/photos",
        "additional_pages/assets"
    ]

    for category in categories:
        path = os.path.join(base_dir, category)
        Path(path).mkdir(parents=True, exist_ok=True)

    print(f"Created export directory structure at {base_dir}/")

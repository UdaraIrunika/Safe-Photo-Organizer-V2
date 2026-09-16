from pathlib import Path

from app.services.date_folders import is_date_folder, build_organized_path


def test_is_date_folder_strict_validation():
    assert is_date_folder("2024-01-30") is True
    assert is_date_folder("2024-13-30") is False
    assert is_date_folder("2024-1-30") is False
    assert is_date_folder("not-a-date") is False


def test_build_organized_path_keeps_parent_structure():
    source_root = Path("F:/MY DATA/MY PHONE ALBUMS")
    file_path = source_root / "Family" / "image1.jpg"
    organized = build_organized_path(source_root, file_path, "2024-01-30")
    assert organized == source_root / "Family" / "2024-01-30" / "image1.jpg"


def test_build_organized_path_ignores_existing_date_folders():
    source_root = Path("F:/MY DATA/MY PHONE ALBUMS")
    file_path = source_root / "Family" / "2024-01-30" / "image1.jpg"
    assert build_organized_path(source_root, file_path, "2024-01-30") is None

from pathlib import Path

from app.services.filename_date_parser import detect_filename_date


def test_detect_date_from_ymd_hms_filename():
    result = detect_filename_date("20240130_080421.jpg")
    assert result is not None
    assert result["date"] == "2024-01-30"
    assert result["source"] == "FILENAME"


def test_detect_date_from_whatsapp_pattern():
    result = detect_filename_date("IMG-20240130-WA0001.jpg")
    assert result is not None
    assert result["date"] == "2024-01-30"


def test_detect_date_from_screenshot_pattern():
    result = detect_filename_date("Screenshot_2024-01-30-123456.png")
    assert result is not None
    assert result["date"] == "2024-01-30"


def test_reject_invalid_random_number_pattern():
    result = detect_filename_date("12345678.jpg")
    assert result is None


def test_detect_date_from_parent_folder_pattern():
    result = detect_filename_date("Family Trip/2024_01_30/image.jpg", parent_folder="Family Trip/2024_01_30")
    assert result is not None
    assert result["date"] == "2024-01-30"

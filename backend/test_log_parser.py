import os
import pytest
from log_parser import parse_log
import subprocess
import sys

# Install required modules
def install_requirements():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "../backend/requirements.txt"])

install_requirements()

SAMPLE = os.path.abspath("../tmp/testlogs/2019-08-25_10-00-00_Iris.bin")

def test_parse_log_success():
    result = parse_log(SAMPLE)
    assert result["flight_time_sec"] > 0
    assert result["max_altitude"] > 0

def test_parse_log_missing():
    bad = parse_log("does_not_exist.bin")
    assert "error" in bad

result = parse_log("test_log.bin")
print(result)

def test_log_parsing_error_handling():
    # Test with non-existent file
    result = parse_log("nonexistent.bin")
    assert "error" in result
    print("✅ Error handling test passed")

def test_uploaded_files_directory():
    # Test that uploaded_files directory exists
    assert os.path.exists("uploaded_files") or os.path.exists("./uploaded_files")
    print("✅ Directory structure test passed")

if __name__ == "__main__":
    test_log_parsing_error_handling()
    test_uploaded_files_directory()
    print("🎯 All basic tests passed!")

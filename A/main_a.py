from get_download_method import get_download_ideas
from try_download_ideas import try_ideas_and_run_code
from analyze_dataset import analyze_and_run_code
from zip_files_final import zip_folder_with_uuid

def a_pipeline():
    get_download_ideas()
    try_ideas_and_run_code()
    analyze_and_run_code()
    zip_folder_with_uuid()

if __name__ == "__main__":
    a_pipeline()



import os, sys, json, csv
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the S folder to sys.path so Python can find the module inside it
sys.path.append(parent_dir)

from sortgs_update import sortgs_main
from utils import read_dataset_name

def evaluate_paper(obj):
    print()

def get_gs_rank_res():
    dataset_name = read_dataset_name()
    sortgs_main(keyword_name=dataset_name)

def csv_to_json(csv_file="draft/query_gs_res.csv", json_file="draft/query_gs_res.json"):
    # Read CSV file and store the data
    data = []
    with open(csv_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)

    # Write data to JSON file
    with open(json_file, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4, ensure_ascii=False)

def get_gs_papers():
    get_gs_rank_res()
    csv_to_json()   


if __name__ == "__main__":
    # get_gs_rank_res()
    # csv_to_json()

    get_gs_papers()
    print()
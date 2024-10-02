# get potential paper website link from 1. dataset websites 2. search engine
import sys
import os

subfolder_path1 = os.path.join(os.getcwd(), 'S')
subfolder_path2 = os.path.join(os.getcwd(), 'E')
subfolder_path3 = os.path.join(os.getcwd(), 'A')
sys.path.append(subfolder_path1)
sys.path.append(subfolder_path2)
sys.path.append(subfolder_path3)

from S.main_s import s_pipeline
from E.main_e import e_pipeline
from A.main_a import a_pipeline
from A.main_sea import sea_pipeline

def sea_pipeline_without_input(dataset_name, dataset_desc):
    s_pipeline(dataset_name=dataset_name, dataset_desc=dataset_desc, need_input=False)
    e_pipeline()
    a_pipeline()

# arr is a list of dataset names
def batch_get_experiment_res(arr):
    for ele in arr:
        sea_pipeline_without_input(ele)
    

if __name__ == "__main__":
    sea_pipeline()
    print()

# get potential paper website link from 1. dataset websites 2. search engine
import sys
import os

# Get the absolute path to the parent directory of the S and E folders
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the S folder to sys.path so Python can find the module inside it
sys.path.append(os.path.join(parent_dir, 'S'))
sys.path.append(parent_dir)

from main_e import e_pipeline
from main_s import s_pipeline

def se_pipeline():
    s_pipeline()
    e_pipeline()

if __name__ == "__main__":
    se_pipeline()

# get potential paper website link from 1. dataset websites 2. search engine
import sys
import os

# Get the absolute path to the parent directory of the S and E folders
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the S folder to sys.path so Python can find the module inside it
sys.path.append(os.path.join(parent_dir, 'S'))
sys.path.append(os.path.join(parent_dir, 'E'))
sys.path.append(parent_dir)

from main_a import a_pipeline

from E.main_es import se_pipeline

def sea_pipeline():
    se_pipeline()
    a_pipeline()

if __name__ == "__main__":
    sea_pipeline()

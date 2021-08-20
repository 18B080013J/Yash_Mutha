import pandas as pd
import numpy as np
import os
import glob

base_path = os.path.join(
    os.path.dirname(__file__),
    'data'
)

raw_data_path = os.path.join(base_path, 'raw')
processed_data_path = os.path.join(base_path, 'processed')

files = glob.glob("{}/*.zip".format(processed_data_path))
for _file in files:
    directory_path = _file
    csv_files = glob.glob("{}/*.csv".format(directory_path))



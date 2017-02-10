#/usr/bin/python3

# Description:     Clean and assemble the unparsed files
# Author:          Bruce Y. Li
# Date:            12/01/2016

import parser as ps
import os
import re
import json
from bs4 import BeautifulSoup
import configparser

# Load configurations
config = configparser.ConfigParser()
config.read('config.ini')

# Change to the root dir
os.chdir(config['Default']['ROOTDIR']

# Step One: Load unparsed index
idx = []
with open('index_unparsed.csv', 'rt') as f:
    for line in f.readlines():
        items = re.split(',', line)
        fileName = items[5].strip() + '/' + items[4]
        idx.append(fileName)
        
idx.pop(0)

# Step Two: Clean and Move the files
for i in idx:
    origin = 'raw/' + i
    output = 'unparsed/' + i
    
    if not os.path.exists(output):
        with open(origin, 'rt') as f:
            data = f.read()

        with open(output, 'wt') as f:
            f.write(ps.clean_text(data))

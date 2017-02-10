#!/usr/bin/python3

# This code takes out management CV discussion from item ones
import re
import os
import configparser

def clean_emp(year):
    """
    Clean the employement section in 10K
    """
    baseDir = 'processed/' + str(year) + '/'
    fList = os.listdir(baseDir)
    
    emp = re.compile(r'\n( *)employee(s?)(\s*)(\n{1,}).*\n', flags=re.I)
    
    for i in fList:
        with open(baseDir + i, 'rt') as f:
            text = f.read()
        newText = emp.sub('', text)
        with open(baseDir + i, 'wt') as f:
            f.write(newText)

# Load configurations
config = configparser.ConfigParser()
config.read('config.ini')

# Change to the root dir
os.chdir(config['Default']['ROOTDIR']

for iYear in range(int(config['Default']['SYEAR']), 
                   int(config['Default']['EYEAR']) + 1):
    clean_emp(iYear)

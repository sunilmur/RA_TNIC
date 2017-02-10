#!/usr/bin/python

# --- Setup --- #
import os
import re
from bs4 import BeautifulSoup
import json
import parser as ps
import configparser

def parser_wrapper(fList, year, logMode):
    """
    A Wrapper for parsing the 10Ks
    Input:
        fList: list of files to be parsed. Full path preferred
        year: year of filing date
        logMode: if 1 - log all the parsed files to raw/parsed.txt
                 if 0 - does not log anything
    """
    
    # Generate Folder for output
    rootDir = 'processed/' + str(year) + '/'
    
    if not os.path.exists(rootDir):
        os.makedirs(rootDir)
    
    for i in fList:
        print(i)
        cik = re.split('_', i.replace('raw/' + str(year) + '/', ''))[0]
        header = ps.extract_header(i)
        outName = rootDir + cik + '-' + header['fdate'] + '.txt'

        if not os.path.exists(outName):
            try:
                txt = ps.clean_text(ps.load_file(i))
            except UnicodeDecodeError:
                continue
            
            
            if logMode == 1:
                with open('raw/parsed.txt', 'a') as f:
                    f.write('\n' + i)
            
            try:
                it1 = ps.item_one_extract_1(txt)
            except MemoryError:
                continue

            if it1 == -1:
                print('    [Error] ext - multiple match')
                continue
            if it1 == -2:
                print('    [Error] ext - wrong stop')
                continue

            valid = ps.validate(it1)
            if valid == 1:
                ps.write_it1(it1, outName)
                ps.write_idx(year, cik, header['fy'], header['fdate'])
            if valid == 0:
                print('    [Error] val - not end in period')
                invalid.append(i)
            if valid == -1:
                print('    [Error] val - item one is none')
            if valid == -2:
                print('    [Error] val - item one too short')



# ==== Main ==== #
config = configparser.ConfigParser()
config.read('config.ini')

# Change to the root dir
os.chdir(config['Default']['ROOTDIR']

for iYear in range(int(config['Default']['SYEAR']), 
                   int(config['Default']['EYEAR']) + 1):
    with open('raw/parsed.txt', 'rt') as f:
        toExclude = re.split('\n', f.read())

    fList = os.listdir('raw/' + str(iYear) + '/')
    fList = ['raw/' + str(iYear) + '/' + x for x in fList]
    fList = list(set(fList) - set(toExclude))

    print(len(fList))
    parser_wrapper(fList, iYear, 1)

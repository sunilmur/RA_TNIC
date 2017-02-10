#!/usr/bin/python3

# Description:   This code prepares for the 10K files, including downloading and recoding
# Author:        Bruce (Yuan) Li / liyuan@villagel.com
# Date:          09/05/2016

import sys, os, re
from ftplib import FTP
import json
import configparser

# Steps for downloading files
#    1 - Step 1: Specify a Year, and download idx file
#    2 - Step 2: Extract from idx and get 10K url
#    3 - Step 3: Download file (stable and able to maintain the list)
#    4 - Step 4: Recodify the steps

def download_idx(year):
    """
    Download the idx file for 10K files
    """
    print('Downloading for year ' + str(year))
    if not os.path.exists('raw/idx/'):
        os.mkdir('raw/idx/')
        
    url = 'ftp.sec.gov'
    path = ['/edgar/full-index/' + str(year) + '/QTR' + str(x) + '/' for x in range(1,5)]
    
    ftp = FTP(url)
    ftp.login()
    
    
    for i in path:
        print('    Entering ' + i)
        ftp.cwd(i)
        qtr = re.search(r'QTR\d', i).group(0)
        zip_name = 'raw/idx/form_' + str(year) + '_' + qtr + '.zip'
        idx_name = 'raw/idx/form_' + str(year) + '_' + qtr + '.idx'
        print('    Retriving...')
        ftp.retrbinary('RETR form.zip', open(zip_name, 'wb').write)
        
        print('    Unzipping...')
        cmd_unzip = 'unzip -o ' + zip_name + ' -d ' + 'raw/idx/'
        cmd_renme = 'mv raw/idx/form.idx ' + idx_name
        os.system(cmd_unzip)
        os.system(cmd_renme)

def gen_idx(year):
    """
    Generate the idx file for 10K files
    """
    ten_k_list = []
    for i in range(1,5):
        fName = 'raw/idx/form_' + str(year) + '_QTR' + str(i) + '.idx'
        with open(fName, 'rt') as f:
            for line in f.readlines():
                info = re.split('\s{2,}', line)
                if len(info) == 6:
                    if re.match(r'10-K.*', info[0], flags = re.IGNORECASE):
                        ten_k_list.append({'name':info[1],
                                           'cik':info[2],
                                           'link':info[4]})
    return(ten_k_list)

def download_10k(fList, year):
    """
    Download the files in the fList from edgar FTP
    """
    if not os.path.exists('raw/' + str(year)):
        os.makedirs('raw/' + str(year))
    
    url = 'ftp.sec.gov'
    ftp = FTP(url)
    ftp.login()
    
    for i in fList:
        fName = re.search(r'/(\d)*/(\d|-)*\.txt', i).group(0)
        fName = re.sub(r'^/', '', fName)
        fName = fName.replace('/', '_')
        tempFile = 'raw/temp.txt'
        fPath = 'raw/' + str(year) + '/' + fName
        ftpDir = '/' + re.search(r'edgar/data/(\d)*/', i).group(0)
        ftpFile = re.search('/(\d|-)*.txt', i).group(0)
        ftpFile = ftpFile.replace('/', '')
    
        if not os.path.exists(fPath):
            print('    Retriving ' + fName)
            status1 = ftp.cwd(ftpDir)
            if re.search('successful', status1):
                status2 = ftp.retrbinary('RETR ' + ftpFile, open(tempFile, 'wb').write)
                if re.search('complete', status2):
                    os.rename(tempFile, fPath)

# Load configurations
config = configparser.ConfigParser()
config.read('config.ini')

# Change to the root dir
os.chdir(config['Default']['ROOTDIR']

for iYear in range(int(config['Default']['SYEAR']), 
                   int(config['Default']['EYEAR']) + 1):
    # Step 1 - Download the IDX file
    download_idx(iYear)
    # Step 2 - Generate the JSON link
    lib = gen_idx(iYear)
    # Step 3 - Perform Downloading
    with open('raw/idx/library_' + str('iYear') + '.json', 'rt') as f:
        lib = json.load(f)
    to_down = []
    for i in lib:
        to_down.append('/' + i['link'])
    download_10k(to_down, iYear)

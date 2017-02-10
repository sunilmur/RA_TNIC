# This file contains all the functions to parse the 10-K files

# Usage: import parser

# --- Setup --- #
import os
import re
from bs4 import BeautifulSoup
import json

# --- Functions --- #
def load_file(fname):
    """
    Load the raw file
    
    Input:
        full path of the source file
    Output:
        string of the source text
    """
    with open(fname) as f:
        data = f.read()
 
    return(data)


def extract_header(file):
    """
    Extract the header information from the text
    """

    with open(file, 'rt') as f:
        FYEnd = ''
        FDate = ''
    
        for i in f.readlines():
            if re.search(r'^CONFORMED PERIOD OF REPORT', i):
                FYEnd = re.search(r'\d+', i).group(0)
            if re.search(r'^FILED AS OF DATE', i):
                FDate = re.search(r'\d+', i).group(0)
            if FYEnd != '' and FDate != '':
                break
    
    return({'fy':FYEnd, 'fdate':FDate})


def clean_text(raw):
    """
    Purge all html tags and keep only the text information
    
    Input:
        string of the source text
    Output:
        cleaned text
    """
    data = re.sub(r'(</[P|p]>)', r'\n\n\1', raw)
    data = re.sub(r'(</[D|d][I|i][V|v]>)', r'\n\n\1', data)    
    soup = BeautifulSoup(data, 'lxml')
    txt = soup.get_text('\n')
    
    # Replaces special characters
    txt = txt.replace("&#038;", "&")
    txt = txt.replace("&#043;", "+")
    txt = txt.replace("&#146;", "\'")
    txt = txt.replace("&#145;", "")
    txt = txt.replace("&#147;", "\"")
    txt = txt.replace("&#148;", "\"")
    txt = txt.replace("&#149;", "•")
    txt = txt.replace("&#151;", "-")
    txt = txt.replace("&nbsp;", " ")
    txt = txt.replace("&#150;", "-")
    txt = txt.replace("&reg;", "")
    txt = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', txt)
    
    # Formalize line
    txt = re.sub(r' +', ' ', txt)
    txt = re.sub(r'\n{2,}', r'DOUBLEDOUBLE', txt)
    txt = re.sub(r'\n', ' ', txt)
    txt = re.sub(r'DOUBLEDOUBLE', r'\n\n', txt)
    
    return(txt)


def validate(txt):
    """
    Validate that item one is correctly extracted
    
    Input:
        item one
    Output:
        result variable
             1 - pass validation test
             0 - the pasrsing is failed
            -1 - item one is none
            -2 - item one is too short
            
            
    """
    if txt is None:
        return(-1)
    
    if len(txt) < 500:
        return(-2)
    
    # Normalize string
    tester = txt[len(txt)-1000:len(txt)].lower()
    tester = re.sub(r'table of content(s?)', '', tester, flags = re.IGNORECASE)
    tester = re.sub(r'\s\d{1,}\s', '', tester)
    tester = re.sub(r'[^A-Za-z0-9\.]', '', tester)
    tester = re.sub(r'\d*$', '', tester)
          
    # Check if the end is a period
    checker = re.findall(r'\.$', tester)
    
    if len(checker) > 0:
        return(1)
    else:
        try:
            stopper = re.search(r'\.[^\.]*?$', tester).group(0) 
        except AttributeError:
            return(-2)
        stopper = re.sub(r'index', '', stopper, flags = re.I)
        stopper = re.sub(r'financialstatement(s?)', '', stopper, flags = re.I)
        stopper = re.sub(r'\d*', '', stopper)
        if len(stopper) < 30:
            return(1)
        else:
            return(stopper)
    
    
def item_one_extract_1(txt):
    """
    Extract Item One from raw txt files
    
    Input:
        cleaned text
    Output:
        item one
        -1 - has multiple match
        -2 - stop sign broken (Add a fixer module)
    """
    reg1 = re.compile(r'^(\s*)i(\s*)t(\s*)e(\s*)m(\s*|\n*)1[\.|\s|:](.|\n)*?(^(\s*)i(\s*)t(\s*)e(\s*)m(\s*|\n*)1(\.?)(\s*|\n*)a[\.|\s|:]).*?\n', 
                      flags = re.I|re.M)
    reg2 = re.compile(r'^(\s*)i(\s*)t(\s*)e(\s*)m(\s*|\n*)1[\.|\s|:](.|\n)*?(^(\s*)i(\s*)t(\s*)e(\s*)m(\s*|\n*)2[\.|\s|:]).*?\n', 
                  flags = re.I|re.M)
    reg3 = re.compile(r'^(\s*)i(\s*)t(\s*)e(\s*)m(\s*|\n*)s(\s*|\n*)1(\.?)(\s*|\n*)a(\s*|\n*)n(\s*|\n*)d(\s*|\n*)2[\.|\s|:](.|\n)*?(^(\s*)i(\s*)t(\s*)e(\s*)m(\s*|\n*)1(\s*|\n*|\.)a[\.|\s|:]).*?\n', 
                      flags = re.I|re.M)
    
    res = []
    itr1 = reg1.finditer(txt)
    
    for i in itr1:
        if len(i.group(0)) > 500:
            res.append(i.group(0))
        
    if len(res) == 1:
        endHook = re.search(r'^(\s*)i(\s*)t(\s*)e(\s*)m(\s*|\n*)1(\.?)(\s*|\n*)a[\.|\s|:].*?\n', res[0], 
                            flags = re.I|re.M)
        endStr = endHook.group(0).strip()
        if len(endStr) > 100:
            if re.search(r'risk(\s*)factor(s?)\s{2,}', endStr, flags = re.I):
                return(res[0].replace(endStr, '').strip())
            else:
                return(-2)
        else:
            item_one = res[0].replace(endStr, '')
            return(item_one.strip())
    elif len(res) == 0:
        # Now try the second parsing algo
        itr2 = reg3.finditer(txt)
        for i in itr2:
            if len(i.group(0)) > 500:
                res.append(i.group(0))
        if len(res) == 1:
            endHook = re.search(r'^(\s*)i(\s*)t(\s*)e(\s*)m(\s*|\n*)1(\s*|\n*)a[\.|\s|:].*?\n', res[0], 
                            flags = re.I|re.M)
            endStr = endHook.group(0).strip()
            if len(endStr) > 100:
                if re.search(r'risk(\s*)factor(s?)\s{2,}', endStr, flags = re.I):
                    return(res[0].replace(endStr, '').strip())
                else:
                    return(-2)
            else:
                item_one = res[0].replace(endStr, '')
                return(item_one.strip())
        else:
            return(res)
    elif len(res) == 2:
        endHook = re.search(r'^(\s*)i(\s*)t(\s*)e(\s*)m(\s*|\n*)1(\.?)(\s*|\n*)a[\.|\s|:].*?\n', res[0], 
                            flags = re.I|re.M)
        endStr = endHook.group(0).strip()
        if len(endStr) > 100:
            if re.search(r'risk(\s*)factor(s?)\s{2,}', endStr, flags = re.I):
                return(res[1].replace(endStr, '').strip())
            else:
                return(-2)
        else:
            item_one = res[1].replace(endStr, '')
            return(item_one.strip())
    else:
        return(-1)
    
    
def write_it1(it1, fName):
    """
    Write item one to file
    """
    with open(fName, 'wt') as f:
        f.write(it1)
        
        
def load_idx_old(year):
    """
    Load teh idx file for already parsed file
    """
    idx = []
    with open('fdate' + str(year) + '_old.idx', 'rt') as f:
        for line in f.readlines():
            dat = re.split(r'\t', line.strip())
            idx.append({'cik':dat[0],
                        'fy':dat[1],
                        'fdate':dat[2]})
                
    return(idx)

def load_idx(year):
    """
    Load teh idx file for already parsed file
    """
    idx = []
    with open('fdate' + str(year) + '.idx', 'rt') as f:
        for line in f.readlines():
            dat = re.split(r'\t', line.strip())
            idx.append({'cik':dat[0],
                        'fy':dat[1],
                        'fdate':dat[2],
                        'fname':dat[3]})
                
    return(idx)


def write_idx(year, cik, fy, fdate):
    """
    Write to the idx file
    """
    idxFile = 'fdate' + str(year) + '.idx'
    fName = cik + '-' + fdate + '.txt'
    
    with open(idxFile, 'at') as f:
        f.write(cik + '\t' + fy + '\t' + fdate + '\t' + fName + '\n')

# SEC 10K Files Parsing
The goal of this project is to extract **Item 1** from the 10K file. The code will run by each filing year. The core code are stored in the `production/` folder. For developing and debugging purpose, you should use the `IPython Notebook` stored in the `debug/` folder. 

## Workflow
1. Download all 10K files from SEC Edgar FTP server
2. Generate raw file index, which contains `filing date` and `fiscal end`
3. Extract Item One, and save them to the `parsed/` folder
4. Collect the index files and generate evaluation statistics
5. Clean and save unparsed files to `unparsed/` folder


## How to use the code?
1. For production, go to `production` folder
1. Change the configuration files accordingly. I have two configuration files under `production/` folder.
    1. `config.R`: this is input to the `gen_index.R`
    2. `config.ini`: this is input to all `.py` files
2. Run `parse_wrapper.sh`, there you will be prompt to 5 choices. Note I use a batch wrapper because I want to keep the code running when encounter unexpected error. This is achieved by using `until`.
    1. Download raw files - `raw_downloader.py`
    2. Parse 10Ks - `parse_10k.py`
    3. Purge employee section - `post_clean.py`
    4. Generate index file - `gen_index.R`
    5. Clean unparsed raw files - `unparsed_post.py`
 
## Folder Structure
```
/
|----- READMD.md
|----- raw/ : by filing year
       |----- 2009
       |----- 2010
       |----- ...
|----- parsed/ : by filing year
       |----- 2009
       |----- 2010
       |----- ...
/----- unparsed/ : by fiscal year
       |----- 2009
       |----- 2010
       |----- ...
/* Code Section */
|----- production: Only .py files and bash wrapper
|----- debug: IPython notebook files
|----- tools: Other codes
|----- old: historical codes to deal with special cases
```

## Key Input
Note we do need an index file from Jerry, which contains all the possible cik-fyear links. We then take the intersection of this sample and the cik-fyear available from the Edgar. The result sample is the base for our parsing.

## File structure for index file
| Variable    | Description                                                   |
| -----       | ---                                                           |
| cik         | CIK Number                                                    |
| fiscal_year | Fiscal Year of the 10K                                        |
| fiscal_end  | Fiscal end date of the 10K                                    |
| filing_data | Filing date of the 10K                                        |
| filing_year | Filing year of the 10K                                        |
| file_name   | Name of the file                                              |
| flag        | Flag == 1 if the output is to be included in the final sample |

#!/usr/bin/R

# Description:    Generate Index files and Perform Evaluation
# Author:         Bruce Y. Li
# Date:           11/22/2016

# --- Setup --- #
## Load libraries
library(data.table)
library(stringr)

## Load configuration
source('config.R')
setwd(ROOTDIR)

## Note:
##     jList - cik-year obs where both 10Ks are available
##     rList - raw file tracking list
##     pList - parsed files list

# --- Main --- #
## From Jerry's List
jList <- fread(INDEXMAIN)
setnames(jList, "year", "fiscal_year")
setkeyv(jList, c("cik", "fiscal_year"))
jList <- unique(jList)
jList <- jList[fiscal_year %in% FSYEARS]

## Raw File List
raw <- data.table()
for (iYear in FLYEARS) {
    dat <- fread(paste0("afdate", iYear, ".idx"))
    # if (iYear == 2012) {
    #     dat[, V1 := unlist(str_split(V1, '-'))[1]]
    # }
    raw <- rbindlist(list(raw, dat))
}

setnames(raw, c("cik", "fiscal_end", "filing_date", "file_name"))
raw[, cik := as.numeric(cik)]
raw[, fiscal_year := floor(fiscal_end / 10000)]
setkeyv(raw, c("cik", "fiscal_year"))

## Get the union of the two sources 
checker <- unique(raw[, .(cik, fiscal_year, flag = 1)])
jList <- merge(jList, checker, all.x = T, all.y = F)
jList <- jList[flag == 1]
jList$flag <- NULL

## Generate raw file tracking list
rList <- raw[cik %in% unique(jList$cik)]
rList[, out_name := paste0(cik, '-', filing_date, '.txt')]

## Coverage checker
pList <- data.table()
for (iYear in FLYEARS) {
    pList <- rbindlist(list(pList,
                            fread(paste0('fdate', iYear, '.idx'))))
setnames(pList, c("cik", "fiscal_end", "filing_date", "file_name"))
pList[, fiscal_year := floor(fiscal_end / 10000)]
pList[, flag := 1]
pList <- pList[fiscal_year %in% FSYEARS]
setkeyv(pList, c("cik", "fiscal_year"))

checker2 <- unique(pList[flag == 1, .(cik, fiscal_year, flag)])
checker3 <- unique(pList[, .(file_name, flag = 1)])

## Coverage
jList <- merge(jList, checker2, all.x = T, all.y = F)
rList <- merge(rList, checker3, all.x = T, all.y = F,
               by.x = "out_name", by.y = "file_name")

## Output
print("Coverage Rate is:")
print(jList[, sum(flag, na.rm = T)/.N, by = .(fiscal_year)])
print(jList[is.na(flag), .N, by = .(fiscal_year)])
print("Processed Rate is:")
print(rList[fiscal_year >= 2014, sum(flag, na.rm = T)/.N, by = .(fiscal_year)])

## Write the index file
pList[, filing_year := floor(filing_date / 10000)]
pList$flag <- NULL
pList <- pList[order(cik, fiscal_year, filing_date)]
pList[, rank := 1:.N, by = .(cik, fiscal_year, filing_date)]
pList[rank == 1, flag := 1]
pList[rank != 1, flag := 0]
pList$rank <- NULL
write.table(pList, "index_parsed.csv", quote = F, row.names = F, sep = ',')

# --- Generate Unparsed Index --- #
for (iYr in FLYEARS) {
    if (!dir.exists(paste0(UNPFOLDER, iYr))) {
        dir.create(paste0(UNPFOLDER, iYr))
    }
}
rawList <- merge(raw, jList[is.na(flag), .(cik, fiscal_year)],
                 by.x = c("cik", "fiscal_year"),
                 by.y = c("cik", "fiscal_year"),
                 all.x = F, all.y = T)
rawList[, filing_year := floor(filing_date / 10000)]
rawList[, flag := NA]

write.table(rawList, "index_unparsed.csv", row.names = F, quote = F, sep = ',')

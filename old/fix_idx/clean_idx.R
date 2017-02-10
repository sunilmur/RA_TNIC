#!/usr/bin/R

# Description:    Merges and Cleans the idx file
# Author:         Bruce Y. Li
# Date:           11/21/2016


library(data.table)

# Change Dir
IDXDIR <- "E:/10k/New10K/"
setwd(IDXDIR)

# Loop over
dat <- data.table()

for (iYear in 2009:2012) {
    idx <- fread(paste0("fdate", iYear, ".idx"),
                 stringsAsFactors = F, header = F, sep = '\t')
    setnames(idx, c("cik", "fiscal_end", "filing_date", "file_name"))
    idx[, fiscal_year := floor(fiscal_end / 10000)]
    idx <- idx[order(cik, fiscal_end, filing_date)]   
    idx[, rank := 1:.N, by = .(cik, fiscal_year)]
    idx[rank == 1, flag := 1]
    idx[rank != 1, flag := 0]
    
    dat <- rbindlist(list(dat, idx[, .(cik, fiscal_end, fiscal_year,
                                  filing_date, file_name, flag)]))
}

# Merge with old idx
oldIdx <- fread("processed/10K_new.idx", sep = '\t', header = T,
                stringsAsFactors = F)

dat <- rbindlist(list(dat, oldIdx))

# Output to File
write.table(dat, file = "10k_2009_2016.idx", quote = F,
            sep = '\t', row.names = F, col.names = T)
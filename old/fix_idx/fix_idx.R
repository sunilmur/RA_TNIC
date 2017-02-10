# This code fixes the idx file

library(data.table)
library(stringr)

fix_idx <- function(year) {
    # Fix the idx file from previous parsing results
  
    # Prepare dataset
    dat <- data.table(read.table(paste0('afdate',
                                        year, '.idx'), stringsAsFactors = F))
    # Generate count
    dat <- dat[, cnt := .N, by = V1]
    
    # Get the files 
    fList <- unique(dir(paste0('processed/', year, '/')))
    fList <- as.numeric(str_replace_all(fList, '\\.txt', ''))
    cikL <- unique(dir(paste0('bak/', year, '/')))
    cikL <- as.numeric(str_replace_all(cikL, '\\.txt', ''))
    
    # Keep only parsable files
    dat <- dat[V1 %in% fList | V1 %in% cikL]
    if (length(cikL) > 0) {
        toRedo <- dat[V1 %in% cikL]$V4
    } else {
        toRedo <- dat[cnt > 1]$V4
        # Move parsed files to bak folder
        for (i in unique(dat[cnt > 1]$V1)) {
            oldF <- paste0('processed/', year, '/', i, '.txt')
            newF <- paste0('bak/', year, '/', i, '.txt')
            file.rename(oldF, newF)
        }
    }
    
    # Write the target files to a txt file
    write.table(toRedo, paste0('fix_', year, '.txt'), 
                sep = '\n', col.names = F,
                row.names =  F, quote = F)
    write.table(dat[cnt == 1, .(V1, V2, V3)],
                paste0('fdate', year, '.idx'),
                sep = '\t', col.names = F,
                row.names = F, quote = F)
}

fix_idx(2016)

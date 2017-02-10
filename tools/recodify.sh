#!/bin/bash

# Description:    To recode non utf-8 fileencodings to utf-8
# Author:         Yuan Li / yli268@usc.edu
# Date:           11/19/2015

fList=$(ls 2012/)

for f in $fList
do
  encoding=$(file -i $f | sed "s/.*charset=\(.*\)$/\1/")
  if [ "${encoding}" == "iso-8859-1" ] 
  then
    echo "recoding file $f"
    recode ${encoding}..utf-8 $f
  fi
done

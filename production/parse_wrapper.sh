#!/bin/sh

echo "What do you want to do?"
echo "    [1] Download raw files"
echo "    [2] Parse 10Ks"
echo "    [3] Purge employee section"
echo "    [4] Generate index file"
echo "    [5] Clean unparsed raw files"

read choice

if [ $choice == 1 ]; then
    until python3 raw_downloader.py; do
        echo "Restarting..."
        sleep 1
    done
elif [ $choice == 2 ]; then
    until python3 parse_10k.py; do
        echo "Restarting..."
        sleep 1
    done
elif [ $choice == 3 ]; then
    until python3 post_clean.py; do
        echo "Restarting..."
        sleep 1
    done
elif [ $choice == 4 ]; then
    R CMD BATCH gen_index.R
elif [ $choice == 5 ]; then
    until python3 unparsed_post.py; do
        echo "Restarting..."
        sleep 1
    done
fi

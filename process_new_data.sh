#!/bin/bash
################################################################################
# Calculate vpip and pfr on the latest session and all sessions together.
#
# First, this script creates a session playlist (i.e. list of filenames) for
# the latest (i.e. from today) batch of files and a session playlist for all
# data files.
# 
# Then, this script calls summarize.py on those playlists to calculate the vpip and
# pfr and save them to logfiles located in the results/ folder.
#
# To run: ./process_new_data <playlist number> <todays date>.
# 
# (The date tag isn't used currently.)
################################################################################
function process_new_data(){
  if [ -z "$1" ] || [ -z "$1" ]; then 
    echo "Usage ./process_new_data <playlist number> <todays date>."
  fi

  # remove spaces from filenames
  for f in raw_data/*\ *; do mv "$f" "${f// /_}"; done 2> /dev/null

  # Add raw data files from today to playlists
  find raw_data/* -maxdepth 1 -type f -mtime -1 -exec basename {} \; > data/pl$1.pl
  find raw_data/* -maxdepth 1 -type f -exec basename {} \; > data/all.pl

  # Add content of this new playlist to data file
  for i in `cat data/pl$1.pl`; do cat raw_data/${i}; done > data/pl$1.txt
  for i in `cat data/all.pl`; do cat raw_data/${i}; done > data/all.txt

  # run main.py in this data file
  python summarize.py data/pl$1.txt results/results_pl$1.txt
  python summarize.py data/all.txt results/results_pl0-pl$1.txt
}

plnumber=$1 
date=$2

echo "Playlist number: $plnumber"
echo "Date tag: $date"

echo "Session $plnumber results saving to results/results_pl$plnumber.txt."
echo "Results from all sessions being saved to results/results_pl0-pl$plnumber.txt."

process_new_data $plnumber $date

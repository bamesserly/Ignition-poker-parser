#!/bin/bash

# 1. remove spaces
# 2. add files to session playlist 
# 3. add file content to session data file
# 4. run main.py on session data file > results_pl#_todaysdate.txt
# 5. add files to total playlist 
# 6. add file content to total data file
# 7. run main.py on total data file > results_pl0_pl#_todaysdate.txt


function process_new_data(){
  if [ -z "$1" ] || [ -z "$1" ]; then 
    echo "Usage ./process_new_data <playlist number> <todays date>."
  fi

  # remove spaces from filenames
  for f in raw_data/*\ *; do mv "$f" "${f// /_}"; done 2> /dev/null

  # Add raw data files from today to playlists
  find raw_data/* -maxdepth 1 -type f -mtime -1 -exec basename {} \; > data/pl$1.pl
  find raw_data/* -maxdepth 1 -type f -mtime -1 -exec basename {} \; >> data/all.pl

  # Add content of this new playlist to data file
  for i in `cat data/pl$1.pl`; do cat raw_data/${i} >> data/pl$1.txt; done
  for i in `cat data/all.pl`; do cat raw_data/${i} >> data/all.txt; done

  echo "1"

  # run main.py in this data file
  python main.py data/pl$1.txt >> results/results_pl$1.txt
  python main.py data/all.txt >> results/results_pl0-pl$1.txt
}

plnumber=$1
date=$2

echo "Playlist number: $plnumber"
echo "Date tag: $date"

echo "Session $plnumber results saving to results/results_pl$plnumber.txt."
echo "Results from all sessions being saved to results/results_pl0-pl$plnumber.txt."

process_new_data $plnumber $date

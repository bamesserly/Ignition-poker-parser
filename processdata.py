# 1. remove spaces from filenames
# 2. add files to session playlist 
# 3. add file content to session data file
# 4. run main.py on session data file > results_pl#_todaysdate.txt
# 5. add files to total playlist 
# 6. add file content to total data file
# 7. run main.py on total data file > results_pl0_pl#_todaysdate.txt

from pathlib import Path
import glob
from main import run
from sys import argv

def RemoveSpacesFromFilename(d):
    for f in Path(d).glob("*.*"):
        print(f)
        if f.is_file():
            f.rename(str(f).replace(" ","_"))


def ConsolidateRawData(d):
    with open("all_data.txt", "wb") as outfile:
        for infile in Path(d).glob("*.txt"):
            with open(infile, "rb") as f:
                outfile.write(f.read())

if __name__ == "__main__":
    ConsolidateRawData(argv[1])
    run("all_data.txt")

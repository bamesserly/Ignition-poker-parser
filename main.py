################################################################################
# Main executable for the ignition poker parsing package
# input: directory of ignition hand history data files
# output: vpip, pfr, and pre-flop open chart
#
# More specifically this script does:
# 1. Gets location directory of ignition hand history files (put all files in
# one directory).
# 2. Concatenates input files into one big file for easier parsing.
# 3. Parses them with the parsing code found in ignition.py.
# 4. Calculates, prints, and saves in a logfile the vpip and pfr.
# 5. Plots and saves the open pre chart.
#
# Usage: python main.py input_dir
################################################################################
from ignition import ParsedHandList
from prechart import ConsolidateRawData, ProcessData, PlotPreOpenChart
from summarize import Summarize
from sys import argv

if __name__ == "__main__":
    logfile = None
    try:
        logfile = argv[2]
    except IndexError:
        pass

    try:
        indir = argv[1]
    except IndexError:
        print("Input data directory is required")
        indir = input("Enter input data dir> ")
        print("Getting data from", indir)
        print()
        logfile = (
            "summary.txt"
            if input(
                "Do you want to save detailed summary to a txt file?\nType y or else just press enter> "
            ).lower()
            == "y"
            else None
        )
        if logfile:
            print("Saving data to logfile", logfile)
        print()

    # Consolidate all raw ignition txt files located in the indir into one file
    consolidated_data_file = ConsolidateRawData(indir)

    # Parse the hands into lists by action_type
    h = ParsedHandList(consolidated_data_file)

    Summarize(h, logfile)

    # Turn parsed hands into csv files and then into data frames
    df = ProcessData(h)

    # Plot!
    PlotPreOpenChart(df)

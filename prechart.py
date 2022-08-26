################################################################################
# From a directory containing ignition hand history files, create a png chart
# showing your open/3b preflop frequencies.
#
# input: directory of ignition hand history data files
#
# Uses the parsing functionality of ignition.py. Passes parsed hands to pandas.
#
# usage: python prechart.py directory_containing_raw_ignition_txt_files
################################################################################
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import glob
from sys import argv
from ignition import ParsedHandList


kCARDS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
kSUITS = ["h", "d", "s", "c"]


# Combine all txt files in raw_data_dir/ into a single outfile
def ConsolidateRawData(raw_data_dir, outfile="cache/all_data.txt"):
    with open(outfile, "wb") as o:
        for infile in Path(raw_data_dir).glob("*.txt"):
            with open(infile, "rb") as f:
                o.write(f.read())
    return outfile


# Take a parsed hand list and make one csv for each action: raise, call, fold.
# Return a dict of csv files {'raise':'raise.csv', ... }.
def WriteHandsToCSV(parsed_data):
    csv_files = {}
    for action_type, hands_for_action in parsed_data.hero_range.items():
        action_csv_file = "cache/{}.csv".format(action_type.lower())
        csv_files[action_type.lower()] = action_csv_file
        with open(action_csv_file, "w+") as f:
            f.write("card1,card2\n")
            for i in hands_for_action:
                f.write(",".join(i) + "\n")
    return csv_files


# Make DF from csv and do initial processing, the result of which is, e.g.:
# cards | fold
# 72o   | 9
# 73o   | 12
# ...
def MakeDF(tag, csv):
    df = pd.read_csv(csv)
    df["formatted"] = df.apply(lambda row: CombineCards(row), axis=1)
    return_df = pd.DataFrame(df.formatted.value_counts().reset_index())
    return_df.columns = ["cards", tag]
    return_df.set_index("cards", inplace=True, drop=True)
    return return_df


# Combine two cols into one and summarize suited-offsuit
# card1 | card2
# '3c'  | 'Jh'   --> 'J3o'
# '4s'  | '5s'   --> '54s'
def CombineCards(row):
    card1 = row["card1"].strip("' ")
    card2 = row["card2"].strip("' ")
    c1, s1 = card1[0].upper(), card1[1].lower()
    c2, s2 = card2[0].upper(), card2[1].lower()
    # first, order the cards
    if kCARDS.index(c1) < kCARDS.index(c2):
        c1, c2 = c2, c1
    if s1 != s2:
        return c1 + c2 + "o"
    else:
        return c1 + c2 + "s"


# If offsuit, change the order of the cards, e.g.
# AKs --> (KA) shows in top-right triangle
# AKo --> (AK) shows in bottom-left triangle
def ParseIsSuited(x):
    if x[2] == "o":
        return (x[0], x[1])
    else:
        return (x[1], x[0])


# Turn parsed hands into csv files and then into data frames
def ProcessData(parsed_hands):
    # Write each hand list to CSV
    csv_files = WriteHandsToCSV(parsed_hands)

    # Turn each csv into a df
    data_frames = [MakeDF(action, file) for action, file in csv_files.items()]

    def CalcRaiseWgt(row):
        return (row["raise"] / (row["fold"] + row["call"] + row["raise"])).round(4)

    def CalcCallWgt(row):
        return (row["call"] / (row["fold"] + row["call"] + row["raise"])).round(4)

    def CalcTotal(row):
        return int(row["fold"] + row["call"] + row["raise"])

    # Combine into single df and add some info. Result is:
    # cards | raise | call | fold | raise_freq | N
    df = pd.concat(data_frames, join="outer", axis=1, sort=False)
    df.fillna(0, inplace=True)
    df.index.name = "cards"
    df["raise_wgt"] = df.apply(lambda row: CalcRaiseWgt(row), axis=1)
    df["call_wgt"] = df.apply(lambda row: CalcCallWgt(row), axis=1)
    df["n"] = df.apply(lambda row: CalcTotal(row), axis=1)

    return df


# Make one list for first hole cards (x-axis), another list for second hole
# card (y-axis).
# x > y --> suited
# y > x --> offsuit
def GetListsOfHoleCards(df):
    # All the hands you've ever been dealt at least once
    # hands = [('K', 'Q'), ('A', 'T'), ('A', 'K'), ... ]
    # If offsuit, keep the order of the cards. If suited, switch the order.
    # This is how we place suited in top right and off suit in bottom left.
    hands = [ParseIsSuited(i) for i in df.index]

    # Convert cards to numbers (e.g. '2' --> 0, 'A' --> 13) for plotting
    x = [i[0] for i in hands]
    x = [kCARDS.index(i) for i in x]
    y = [i[1] for i in hands]
    y = [kCARDS.index(i) for i in y]

    return x, y


# Add text to each cell: the hand (e.g. AA), the raise frequency (e.g.  97.9%),
# and how many times the hand was dealt (e.g. 5 times)
def AddTextToCells(h2d, hole_cards_dealt, bins_x, bins_y):
    counts = h2d[0] # 2d matrix of number of entries in each bin
    for i in range(counts.shape[0]):
        for j in range(counts.shape[1]):
            cell_count = counts[i, j]
            cell_count = (cell_count * 100.).round(1)  # make it a percent
            txt_color = "white" if cell_count > 25 else "black" # making txt visible on background color
            lbl = ""

            # Number of times this hand has been dealt.
            N = 0
            try:
                N = hole_cards_dealt[(i, j)]
            except:
                pass

            # Text that goes in each cell.
            # "s" in the top right, "o" in bottom left, and nothing along the
            # diagonal
            if i > j:
                lbl = "{0}{1}o\n{2}%\n({3})".format(kCARDS[i], kCARDS[j], cell_count, N)
            elif i == j:
                lbl = "{0}{1}\n{2}%\n({3})".format(kCARDS[i], kCARDS[j], cell_count, N)
            else:
                lbl = "{0}{1}s\n{2}%\n({3})".format(kCARDS[j], kCARDS[i], cell_count, N)

            # Add the text to the cell
            plt.text(
                bins_x[i] + 0.5,
                bins_y[j] + 0.5,
                lbl,
                ha="center",
                va="center",
                color=txt_color,
            )


# From a specially-formatted data frame, plot your open (raise or 3b) frequency
def PlotPreOpenChart(df):
    x_vals, y_vals = GetListsOfHoleCards(df)

    # Cell content is the raise_frequency
    #z_vals = df["raise_wgt"].to_list()
    z_vals = df["call_wgt"].to_list()

    # Map each card combo to how many times that combo was dealt.
    # e.g. hole_cards_dealt = { (12,12) : 5, (12,11) : 9, ... } means AA dealt
    # 5 times ever, and AK suited dealt 9 times.
    n_times_dealt = df["n"].to_list()
    hole_cards_dealt = dict(zip(tuple(zip(x_vals, y_vals)), n_times_dealt))

    # Plot
    bins_x = bins_y = np.arange(0, len(kCARDS) + 1)  # 13 bins, 1 for each card
    fig, ax = plt.subplots(figsize=(15, 10))  # make a 15x10 size canvas
    h2d = ax.hist2d(
        x_vals, y_vals, bins=[bins_x, bins_y], cmap=plt.cm.Reds, weights=z_vals
    )  # ship it
    fig.colorbar(h2d[3])  # Color scale legend
    ax.invert_xaxis()  # AA at the top left
    ax.axes.xaxis.set_visible(False)  # hide tick marks and axis labels
    ax.axes.yaxis.set_visible(False)  # hide tick marks and axis labels

    n_total_hands = df["n"].sum()
    #fig.suptitle(f"Open or 3B frequency\n({n_total_hands} hands)", fontsize=20)
    fig.suptitle(f"Call pre frequency\n({n_total_hands} hands)", fontsize=20)

    # The hand, raise freq, and number of times dealt
    AddTextToCells(h2d, hole_cards_dealt, bins_x, bins_y)

    # Display and save as png
    plt.show()
    #fig.savefig("cache/open_pre.png")
    fig.savefig("cache/call_pre.png")


if __name__ == "__main__":

    # Consolidate all raw ignition txt files located in the indir into one file
    consolidated_data_file = ConsolidateRawData(argv[1])

    # Parse the hands into lists by action_type
    h = ParsedHandList(consolidated_data_file)

    # Turn parsed hands into csv files and then into data frames
    df = ProcessData(h)

    # Plot!
    PlotPreOpenChart(df)

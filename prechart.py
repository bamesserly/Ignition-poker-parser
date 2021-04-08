# libraries
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

kCARDS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
kSUITS = ["h", "d", "s", "c"]


# Combine two rows into one and summarize suited-offsuit
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


# AKs --> (KA) top-right triangle
# AKo --> (AK) bottom-left triangle
def ParseIsSuited(x):
    if x[2] == "o":
        return (x[0], x[1])
    else:
        return (x[1], x[0])


def PlotHands(df):
    n_total_hands = df["n"].sum()


    # All the hands you've ever been dealt at least once
    # hands = [('K', 'Q'), ('A', 'T'), ('A', 'K'), ... ]
    # If offsuit, keep the order of the cards. If suited, switch the order.
    # This is how we place suited in top right and off suit in bottom left.
    hands = [ParseIsSuited(x) for x in df.index]

    # Make one list for first hole cards (x-axis), andother list for second
    # hole card (y-axis).
    # Convert cards to numbers (e.g. '2' --> 0, 'A' --> 13) for plotting
    # x > y --> suited
    # y > x --> offsuit
    x = [i[0] for i in hands]
    x = [kCARDS.index(i) for i in x]
    y = [i[1] for i in hands]
    y = [kCARDS.index(i) for i in y]

    # Cell content is the raise_frequency
    wgts = df["raise_wgt"].to_list()

    # Map each card combo to how many times that combo was dealt.
    # e.g. hole_cards_dealt = { (12,12) : 5 } means AA dealt 5 times ever
    n_times_dealt = df["n"].to_list()
    hole_cards_dealt = dict(zip(tuple(zip(x, y)), n_times_dealt))

    # Plot
    bins_x = bins_y = np.arange(0, len(kCARDS) + 1)  # 13 bins, 1 for each card
    fig, ax = plt.subplots(figsize=(15, 10))  # make a 15x10 size canvas
    h2d = ax.hist2d(
        x, y, bins=[bins_x, bins_y], cmap=plt.cm.Reds, weights=wgts
    )  # plot!
    fig.colorbar(h2d[3])  # Color scale legend
    ax.invert_xaxis()  # AA at the top left
    ax.axes.xaxis.set_visible(False)  # hide tick marks and axis labels
    ax.axes.yaxis.set_visible(False)  # hide tick marks and axis labels
    fig.suptitle("Open or 3B frequency\n({} hands)".format(n_total_hands), fontsize=20)  # title

    # Print in each cell: the hand (AA), the raise frequency (100%), and how
    # many times the hand was dealt (5x)
    counts = h2d[0]
    for i in range(counts.shape[0]):
        for j in range(counts.shape[1]):
            c = counts[i, j]
            c = (c * 100.).round(1)  # make it a percent
            color = "white" if c > 25 else "black"
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
                lbl = "{0}{1}o\n{2}%\n({3})".format(kCARDS[i], kCARDS[j], c, N)
            elif i == j:
                lbl = "{0}{1}\n{2}%\n({3})".format(kCARDS[i], kCARDS[j], c, N)
            else:
                lbl = "{0}{1}s\n{2}%\n({3})".format(kCARDS[j], kCARDS[i], c, N)

            # Add the text to the cell
            plt.text(
                bins_x[i] + 0.5,
                bins_y[j] + 0.5,
                lbl,
                ha="center",
                va="center",
                color=color,
            )

    # Display the plot and save it to png
    plt.show()
    fig.savefig("open_pre.png")


def ProcessDF(df, action):
    df["formatted"] = df.apply(lambda row: CombineCards(row), axis=1)
    return_df = pd.DataFrame(df.formatted.value_counts().reset_index())
    return_df.columns = ["cards", action]
    return_df.set_index("cards", inplace=True, drop=True)
    return return_df


if __name__ == "__main__":
    # Clean/process the raise, call, fold data
    dfr = pd.read_csv("raise_pl0_pl3.txt")
    dfr = ProcessDF(dfr, "raise")

    dfc = pd.read_csv("call_pl0_pl3.txt")
    dfc = ProcessDF(dfc, "call")

    dff = pd.read_csv("fold_pl0_pl3.txt")
    dff = ProcessDF(dff, "fold")

    def CalcRaiseWgt(row):
        return (row["raise"] / (row["fold"] + row["call"] + row["raise"])).round(4)

    def CalcTotal(row):
        return int(row["fold"] + row["call"] + row["raise"])

    # Combine data to be of the form
    # df = cards | raise | call | fold | raise_freq | N
    df = pd.concat([dfr, dfc, dff], join="outer", axis=1, sort=False)
    df.fillna(0, inplace=True)
    df.index.name = "cards"
    df["raise_wgt"] = df.apply(lambda row: CalcRaiseWgt(row), axis=1)
    df["n"] = df.apply(lambda row: CalcTotal(row), axis=1)

    PlotHands(df)

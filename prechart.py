# libraries
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from string import whitespace

kCARDS = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
kSUITS = ["h", "d", "s", "c"]


class Hand:

    def __init__(self, raw_hand):
        self.good = self.ValidateHand(raw_hand)
        self.card1 = raw_hand[0][0].upper()
        self.card2 = raw_hand[1][0].upper()
        self.suit1 = raw_hand[0][1].lower()
        self.suit2 = raw_hand[1][1].lower()
        self.suited = self.suit1 == self.suit2
        # first order the cards
        if kCARDS.index(self.card1) < kCARDS.index(self.card2):
            self.card1, self.card2 = self.card2, self.card1
        # reverse their order if they're suited
        if self.suited:
            self.card1, self.card2 = self.card2, self.card1

    # check that hand has form ['2d', 'Jd']
    def ValidateHand(self, raw_hand):
        if len(raw_hand) != 2:
            return False
        if not all([len(x) == 2 for x in raw_hand]):
            return False
        if not all([x[0].upper() in kCARDS for x in raw_hand]):
            return False
        if not all([x[1].lower() in kSUITS for x in raw_hand]):
            return False
        return True


# output [(<card1>, <card2>, is_suited), ...]
def ParseHands(hands):
    n_bad_hands = 0
    parsed_hands = []
    for raw_hand in hands:
        h = Hand(raw_hand)
        if not h.good:
            n_bad_hands = n_bad_hands + 1
            continue
        parsed_hands.append((h.card1, h.card2, h.suited))

    print("n bad hands:", n_bad_hands)
    # print("\n".join(str(h) for h in parsed_hands))

    return parsed_hands, n_bad_hands


def PlotHands(df, weights=None, tag=None):
    hands_list = [
        [x.strip(whitespace + "\"'"), y.strip(whitespace + "\"'")]
        for x, y in zip(df["card1"], df["card2"])
    ]
    parsed_hands, n_bad_hands = ParseHands(hands_list)
    x = [i[0] for i in parsed_hands]
    x = [kCARDS.index(i) for i in x]
    y = [i[1] for i in parsed_hands]
    y = [kCARDS.index(i) for i in y]
    is_suited = [i[2] for i in parsed_hands]

    bins_x = bins_y = np.arange(0, len(kCARDS) + 1)

    f, ax = plt.subplots(figsize=(10, 10))
    h2d = ax.hist2d(x, y, bins=[bins_x, bins_y], cmap=plt.cm.Reds, weights=weights)
    f.colorbar(h2d[3])
    ax.invert_xaxis()
    counts = h2d[0]
    for i in range(counts.shape[0]):
        for j in range(counts.shape[1]):
            c = counts[i, j]
            color = "white" if c > 10 else "black"
            percent = ""
            if weights:
                c = (c * 100.).round(2)
                color = "white" if c > 0.09 else "black"
                percent = "%"
            else:
                c = int(c)
            lbl = ""
            if i > j:
                lbl = "{0}{1}o\n{2}".format(kCARDS[i], kCARDS[j], c) + percent
            elif i == j:
                lbl = "{0}{1}\n{2}".format(kCARDS[i], kCARDS[j], c) + percent
            else:
                lbl = "{0}{1}s\n{2}".format(kCARDS[j], kCARDS[i], c) + percent
            plt.text(
                bins_x[i] + 0.5,
                bins_y[j] + 0.5,
                lbl,
                ha="center",
                va="center",
                color=color,
            )

    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)

    f.suptitle(tag, fontsize=20)

    plt.show()
    f.savefig("{}.png".format(tag))


if __name__ == "__main__":
    df_raise = pd.read_csv("raise_pl0_pl3.txt")
    df_fold = pd.read_csv("fold_pl0_pl3.txt")
    df_call = pd.read_csv("call_pl0_pl3.txt")
    n_hands = len(df_raise.index) + len(df_fold.index) + len(df_call.index)
    raise_weights = [1. / float(n_hands)] * len(df_raise.index)
    fold_weights = [1. / float(n_hands)] * len(df_fold.index)
    call_weights = [1. / float(n_hands)] * len(df_call.index)
    PlotHands(df_raise, tag="raise_frequency")
    PlotHands(df_call, tag="call_frequency")
    PlotHands(df_fold, tag="fold_frequency")

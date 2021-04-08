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

def IsSuited(row):
    card1 = row['card1'].strip("' ")
    card2 = row['card2'].strip("' ")
    c1, s1 = card1[0].upper(), card1[1].lower()
    c2, s2 = card2[0].upper(), card2[1].lower()
    if s1 == s2:
        return True
    else:
        return False

# Cards ordered without suits, e.g. "AA", "J3"
def BareCards(row):
    c1 = row["card1"].strip("' ")
    c1 = c1[0].upper()
    c2 = row["card2"].strip("' ")
    c2 = c2[0].upper()
    # first order the cards
    if kCARDS.index(c1) < kCARDS.index(c2):
        c1, c2 = c2, c1
    return c1 + c2

def FormatCards(row):
    card1 = row["card1"].strip("' ")
    card2 = row["card2"].strip("' ")
    c1, s1 = card1[0].upper(), card1[1].lower()
    c2, s2 = card2[0].upper(), card2[1].lower()
    # first order the cards
    if kCARDS.index(c1) < kCARDS.index(c2):
        c1, c2 = c2, c1
    if s1==s2:
        return c1+c2+'s'
    #elif c1 == c2:
    #    return c1+c2
    else:
        return c1+c2+'o'

if __name__ == "__main__":
    dfr = pd.read_csv("raise_pl0_pl3.txt")
    dfr['formatted'] = dfr.apply (lambda row: FormatCards(row), axis=1)
    dfr = pd.DataFrame(dfr.formatted.value_counts().reset_index())
    dfr.columns = ['cards', 'raise']
    dfr.set_index('cards', inplace=True, drop=True)

    dfc = pd.read_csv("call_pl0_pl3.txt")
    dfc['formatted'] = dfc.apply (lambda row: FormatCards(row), axis=1)
    dfc = pd.DataFrame(dfc.formatted.value_counts().reset_index())
    dfc.columns = ['cards', 'call']
    dfc.set_index('cards', inplace=True, drop=True)

    dff = pd.read_csv("fold_pl0_pl3.txt")
    dff['formatted'] = dff.apply (lambda row: FormatCards(row), axis=1)
    dff = pd.DataFrame(dff.formatted.value_counts().reset_index())
    dff.columns = ['cards', 'fold']
    dff.set_index('cards', inplace=True, drop=True)

    df = pd.concat([dfr, dfc, dff], join='outer', axis=1, sort=False)
    df.index.name = 'cards'
    df.fillna(0, inplace=True)
    #df.sort_index(inplace=True, ascending=False)

    def CalcRaiseWgt(row):
        return (row['raise']/(row['fold'] + row['call'] + row['raise'])).round(3)

    df['raise_wgt'] = df.apply (lambda row: CalcRaiseWgt(row), axis=1)

    def PlotHands(df):
        def Parse(x):
            if x[2] = 'o'
                return (x[0],x[1],False)
        parsed_hands = [(x[0],x[1]) for x in df.index]
        hands_list = [[x[0],x[1]] for x in df.index]
        print(hands_list)
        bins_x = bins_y = np.arange(0, len(kCARDS) + 1)
        #f, ax = plt.subplots(figsize=(10, 10))
        #h2d = ax.hist2d(x, y, bins=[bins_x, bins_y], cmap=plt.cm.Reds, weights=weights)

    PlotHands(df)

'''
    hands_list = [
        x
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
    #values = df['formatted'].value_counts().keys().tolist()
    #counts = df['formatted'].value_counts().tolist()
    ##df1 = pd.concat([values, counts], keys=['cards', 'raised'], axis=1)
    #df1 = df['formatted'].value_counts()#.rename_axis('unique_values').to_frame('counts')
    #print(df1)
    #df_fold = pd.read_csv("fold_pl0_pl3.txt")
    #df_call = pd.read_csv("call_pl0_pl3.txt")
    #n_hands = len(df_raise.index) + len(df_fold.index) + len(df_call.index)
    #raise_weights = [1. / float(n_hands)] * len(df_raise.index)
    #fold_weights = [1. / float(n_hands)] * len(df_fold.index)
    #call_weights = [1. / float(n_hands)] * len(df_call.index)
    #PlotHands(df_raise, tag="raise_frequency")
    #PlotHands(df_call, tag="call_frequency")
    #PlotHands(df_fold, tag="fold_frequency")
'''

from ignition import ParsedHandList
from pprint import pprint
from sys import argv

## usage: python summarize.py example_ignition.txt


def Summarize(h):
    print(h)
    print("SUMMARY\n========")
    for action_type, hands_for_action in h.hero_range.items():
        print(action_type + ":")
        pprint(hands_for_action)
    print()
    print(
        "VPIP = {}  ({}/{} over {} hands)".format(
            round(h.vpip, 4), h.calls_raises, h.n, h.n_hands
        )
    )
    print(
        "PFR  = {}  ({}/{} over {} hands)".format(
            round(h.pfr, 4), h.raises, h.n, h.n_hands
        )
    )


if __name__ == "__main__":
    h = ParsedHandList(argv[1])
    Summarize(h)

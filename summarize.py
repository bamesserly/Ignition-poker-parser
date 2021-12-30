################################################################################
# Return the vpip and pfr from a single ignition hand history data file
# Usage: python summarize.py my_logfile.txt
################################################################################
from ignition import ParsedHandList
from pprint import pformat
from sys import argv, exit
import logging


def SetupLogger(name="root"):
    shandler = logging.StreamHandler()
    shandler.setLevel(logging.INFO) # only info+ will be logged
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG) # lowest level that can ever by logged
    logger.addHandler(shandler)
    return logger


def Summarize(h, logfile):
    logger = SetupLogger()
    if logfile:
        fhandler = logging.FileHandler(logfile, "w+")
        fhandler.setLevel(logging.DEBUG)
        logger.addHandler(fhandler)
    logger.debug(h)
    logger.info("SUMMARY\n========")
    for action_type, hands_for_action in h.hero_range.items():
        logger.debug(action_type + ":")
        logger.debug(pformat(hands_for_action))
    logger.info(
        "VPIP = {}  ({}/{} over {} hands)".format(
            round(h.vpip, 4), h.calls_raises, h.n, h.n_hands
        )
    )
    logger.info(
        "PFR  = {}  ({}/{} over {} hands)".format(
            round(h.pfr, 4), h.raises, h.n, h.n_hands
        )
    )


if __name__ == "__main__":
    try:
        data_file = argv[1]
    except IndexError:
        exit("ERROR: missing input data."
             "\nUsage: python summarize.py example_ignition.txt <logfile.txt>")
    try:
        logfile = argv[2]
    except IndexError:
        logfile = None
    h = ParsedHandList(argv[1])
    Summarize(h, logfile)

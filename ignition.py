import re

class HoleCards:
    """All the hole cards at the table, with a property to retrieve just
    hero's cards.
    """
    def __init__(self, cardlist = None, heroidx = None):
        if cardlist:
            self.cardlist = cardlist
        else:
            self.cardlist = []
        self._heroidx = heroidx
        if heroidx:
            self.hero = cardlist[heroidx]
        else:
            self.hero = None
    @property
    def heroidx(self):
        return self._heroidx
    @heroidx.setter
    def heroidx(self, i):
        self._heroidx = i
        self.hero = self.cardlist[i]
    def append(self, e):
        self.cardlist.append(e)
    def tag_hero(self):
        self.heroidx = len(self.cardlist) - 1
    def __repr__(self):
        return repr(self.cardlist)
    def __getitem__(self, i):
        return self.cardlist[i]

class BettingRound:
    def __init__(self, lines):
        self.cards = HoleCards()
        self.actions = []
        _round_name_re = re.compile(r"^([A-Z ]+) \*\*\*.*$")
        _street_cards_re = re.compile(r".*\[(.*)\].*")
        # "street" hits only last [Kh] construct because 1st * is greedy.
        _hole_cards_re = re.compile(r".*Card dealt to a spot \[(.*)\]")
        assert ('HOLE' in lines[0]
                or 'FLOP' in lines[0]
                or 'TURN' in lines[0]
                or 'RIVER' in lines[0] )
        match = _round_name_re.match(lines[0])
        self.round_name = match.group(1)
        if '[' in lines[0]:
            # only for flop/turn/riv
            match = _street_cards_re.match(lines[0])
            self.cards.cardlist = match.group(1).split()
        for L in lines[1:]:
            if 'Card dealt to a spot' in L:
                assert not '[' in lines[0] # assert not flop/turn/riv
                match = _hole_cards_re.match(L)
                self.cards.append(match.group(1).split()) # list of lists
                if '[ME]' in L:
                    self.cards.tag_hero()
            elif ('Seat sit down' in L
                  or 'Table deposit' in L
                  or 'Seat stand' in L
                  or 'Table enter user' in L
                  or 'Table leave user' in L
                  or 'Seat re-join' in L):
                continue
            elif ' : ' in L:
                self.actions.append(L)
            else:
                print('*** unhandled line ' + self.round_name +
                      str(lines.index(L)) + ':' + L )
        ### Tally hero's preflop raises, calls, and all actions.
        if self.round_name == 'HOLE CARDS':
            self.raise_n = 0
            self.call_n = 0
            self.action_n = 0
            self.hero_first = ''
            for a in self.actions:
                if '[ME]' in a:
                    self.action_n += 1
                    if 'Raises' in a:
                        self.raise_n += 1
                        if self.action_n == 1:
                            self.hero_first = 'Raise'
                    elif 'Calls' in a:
                        self.call_n += 1
                        if self.action_n == 1:
                            self.hero_first = 'Call'
                    elif 'Folds' in a:
                        if self.action_n == 1:
                            self.hero_first = 'Fold'

    def __repr__(self):
        return str(self.__dict__)

class Hand:
    def __init__(self, string):
        _hand_num_re = re.compile(r"^Hand #(\d+) .*$")
        self.seats = None
        self.preflop = None
        self.flop = None
        self.turn = None
        self.river = None
        self.summary = None
        ## step 2: split each hand into segments
        s = string.split('\n*** ')
        while s:
            # Not known whether flop, turn, riv, or summary is in there.
            ## step 3: split each segment into lines
            v = s.pop(0).splitlines()
            if 'Hand #' in v[0]:
                self.seats = v
            elif 'HOLE' in v[0]:
                self.preflop = BettingRound(v)
            elif 'FLOP' in v[0]:
                self.flop = BettingRound(v)
            elif 'TURN' in v[0]:
                self.turn = BettingRound(v)
            elif 'RIVER' in v[0]:
                self.river = BettingRound(v)
            elif 'SUMMARY' in v[0]:
                self.summary = v
            else:
                assert False
        assert len(s) == 0
        ## step 4: parse various elements at sub-line level
        match = _hand_num_re.match(self.seats[0])
        self.hand_number = int(match.group(1))

    def __repr__(self):
        return str(self.__dict__)

    def __getitem__(self, i):
        keys_ordered = "seats preflop flop turn river summary".split()
        return self.__dict__[keys_ordered[i]]

class ParsedHandList:
    def __init__(self, filename):
        input = open(filename).read()
        hands_raw = input.split('Ignition ')
        self.hand_list = []
        self.hand_nums = []
        empty = hands_raw.pop(0) # remove 1st always empty element
        assert empty == ''
        for h in hands_raw:
            candidate = Hand(h)
            if candidate.hand_number in self.hand_nums:
                continue
            else:
                self.hand_nums.append(candidate.hand_number)
                self.hand_list.append(candidate)
        ### Compute hero's VPIP, PFR, and hands sorted by action, over
        ### all these hands.
        self.calls_raises = 0
        self.raises = 0
        self.n = 0
        self.hero_range = {'Raise':[], 'Call':[], 'Fold':[]}
        for x in self.hand_list:
            self.calls_raises += (x.preflop.call_n + x.preflop.raise_n)
            self.raises += x.preflop.raise_n
            self.n += x.preflop.action_n
            for k in self.hero_range.keys():
                if x.preflop.hero_first == k:
                    self.hero_range[k].append(x.preflop.cards.hero)
        self.n_hands = len(self.hand_list)
        self.vpip = float(self.calls_raises) / self.n
        self.pfr = float(self.raises) / self.n

    def __repr__(self):
        R = ''
        for x in self.hand_list:
            R += '{} (#{})\n'.format(x.preflop.cards.hero, x.hand_number)
            for a in x.preflop.actions:
                if '[ME]' in a:
                    R += (a + '\n')
            R += '\n'
        return R

    def __getitem__(self, i):
        return self.hand_list[i]

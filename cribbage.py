#!/usr/bin/env python3
# coding=utf-8

from itertools import combinations
from math import ceil

from scipy.misc import comb

CLUBS = 0
DIAMONDS = 1
HEARTS = 2
SPADES = 3

RANKS = ['Ace',
         'Two',
         'Three',
         'Four',
         'Five',
         'Six',
         'Seven',
         'Eight',
         'Nine',
         'Ten',
         'Jack',
         'Queen',
         'King']

SUITS = [('Clubs', '♣', '\033[30m'),
         ('Diamonds', '♦', '\033[31m'),
         ('Hearts', '♥', '\033[31m'),
         ('Spades', '♠', '\033[30m')]


class Card:
    def __init__(self, rank, suit):
        if rank < 1 or rank > 13:
            raise ValueError('invalid rank')
        elif suit < 0 or suit > 3:
            raise ValueError('invalid suit')

        self._rank = rank
        self._suit = suit

    def __lt__(self, other):
        return self.get_value() < other.get_value()

    def __eq__(self, other):
        return self.get_value() == other.get_value()

    def __str__(self):
        return self.get_long_string()

    def __repr__(self):
        return '<Card rank=%d suit=%d>' % (self._rank, self._suit)

    def get_long_string(self):
        return RANKS[self._rank - 1] + ' of ' + SUITS[self._suit][0]

    def get_rank(self, cribbage=False):
        if cribbage:
            return self._rank if self._rank <= 10 else 10
        else:
            return self._rank

    def get_short_string(self, colour=False):
        string = (str(self._rank) if 2 <= self._rank <= 10 else RANKS[self._rank - 1][0]) + SUITS[self._suit][1]

        if colour:
            string = SUITS[self._suit][2] + string + '\033[0m'

        return string

    def get_suit(self):
        return self._suit

    def get_value(self):
        return (self._rank - 1) * 4 + self._suit

    @classmethod
    def from_short(cls, short):
        rank, suit = -1, -1

        # Determine the rank.
        if short[0] == 'A':
            rank = 1
        elif short[0] == 'T':
            rank = 10
        elif short[0] == 'J':
            rank = 11
        elif short[0] == 'Q':
            rank = 12
        elif short[0] == 'K':
            rank = 13
        else:
            rank = int(short[0])

        # Determine the suit.
        if short[1] == 'C':
            suit = CLUBS
        elif short[1] == 'D':
            suit = DIAMONDS
        elif short[1] == 'H':
            suit = HEARTS
        elif short[1] == 'S':
            suit = SPADES

        return cls(rank, suit)

    @classmethod
    def from_value(cls, value):
        rank = value // 4 + 1
        suit = value % 4

        return cls(rank, suit)


def score_hand(hand, cut):
    hand.sort()

    hand_with_cut = hand + [cut]
    hand_with_cut.sort()

    return {'totals': score_hand_total(hand_with_cut),
            'pairs': score_hand_pairs(hand_with_cut),
            'runs': score_hand_runs(hand_with_cut),
            'flush': score_hand_flush(hand, cut),
            'jack': score_hand_jack(hand, cut)}


def score_hand_total(hand):
    score = 0

    for r in range(2, 6):
        score += len([cards for cards in combinations(hand, r) if sum([c.get_rank(True) for c in cards]) == 15])

    return score * 2


def score_hand_pairs(hand):
    score = 0
    ranks = [0 for _ in range(13)]

    for c in hand:
        ranks[c.get_rank() - 1] += 1

    for count in ranks:
        if count >= 2:
            score += int(ceil(comb(count, 2)))

    return score * 2


def score_hand_runs(hand):
    score, streak, multiplier = 0, 1, 1
    ranks = [0 for _ in range(13)]

    for c in hand:
        ranks[c.get_rank() - 1] += 1

    multiplier *= 1 if ranks[0] == 0 else ranks[0]

    for i in range(1, 13):
        if ranks[i] > 0 and ranks[i - 1] > 0:
            streak += 1
        else:
            if streak >= 3:
                score += streak * multiplier

            streak = 1

        # Update multiplier value.
        multiplier = 1 if ranks[i] == 0 else ranks[i] if streak == 1 else multiplier * ranks[i]

    if streak >= 3:
        score += streak * multiplier

    return score


def score_hand_flush(hand, cut):
    for i in range(1, 4):
        if hand[i].get_suit() != hand[i - 1].get_suit():
            return 0

    if hand[0].get_suit() == cut.get_suit():
        return 5
    else:
        return 4


def score_hand_jack(hand, cut):
    for c in hand:
        if c.get_rank() == 11 and c.get_suit() == cut.get_suit():
            return 1

    return 0


while True:
    my_hand = input('Enter hand cards: ').strip().upper()
    my_hand = [Card.from_short(card) for card in my_hand.split(' ')]

    my_cut = Card.from_short(input('Enter cut card: ').strip().upper())

    my_score = score_hand(my_hand, my_cut)

    print('Score for %s (%s) is %d.' % (
        ', '.join([card.get_short_string(True) for card in my_hand]), my_cut.get_short_string(True),
        sum(my_score.values())))

    print('Score breakdown:')
    for key, value in my_score.items():
        print('{0:>15}: {1}'.format(key, value))

    print()

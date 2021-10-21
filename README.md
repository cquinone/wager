# wager
Continuous form of the game Wits &amp; Wagers

Requires: Pygame, Pygame_gui (see https://github.com/MyreMylar/pygame_gui), and numpy

To play:
 - download all the files into one directory
 - run from a terminal: python3 wager_gui.py NAME1 NAME2 NAME3 ...

 where NAME1, NAME2, etc. are two character strings that are players' initials, and "python3" may be just "python", as long as that is a call to python 3.5+.

Once the game has loaded, each player guesses in turn, and then plots their "bet",
each "bet" is scored as 
< 1/|ans-x| > (averaging based on their distribution == "bet").
Press "c" while plotting to clear all points.

Note: the button "Score Table" may only be pressed in-between rounds.

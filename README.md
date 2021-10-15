# wager
Continuous form of the game Wits &amp; Wagers

Requires: Pygame, Pygame_gui (see https://github.com/MyreMylar/pygame_gui), and numpy

To play:
 - download all the files in the directory
 - run from a terminal: python3 wager_gui.py NAME1 NAME2 NAME3 ...

 where NAME1, NAME2, etc. are two character strings that are players' initials, and "python3" may be just "python".

Once the game has loaded, each player guesses in turn, and then plots their "bet",
each "bet" is scored as 
< 1/|ans-x| > (averaging based on their distribution == "bet")
Press "c" while plotting to clear all points.

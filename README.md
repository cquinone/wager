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

CONTROLS / INPUT:
On the first screen, click on the blue entry box and enter a range in the form "a,b",
then press enter. You may (before pressing enter) pick a player color from the box on th right.
Once plotting, click the  plot box once to begin, move the mouse, and then click again to finish.
Press "c" while plotting to clear all points if you make a mistake. Once done plotting,
click "DONE". To plot a flat line across the board, click the "FLAT" button. To plot a gaussian 
with a chosen mean / std dev, click the "BELL"  button. After everyone has plotted and the score 
animation completed, click "NEXT" to go to the next question, or click "SCORE TABLE" to see the current scores. 

Note: the button "Score Table" may only be pressed in-between rounds.

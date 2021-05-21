import pygame as pg
import random as rand
import sys

WIDTH = 1000
HEIGHT = 680
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 237, 250)
GREEN = (34,139,34)


class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.avg = -1
        self.points = []
        self.old_points = []
        self.done = False


def trapezoid(points,mode):
    integral = 0
    for i in range(len(points)):
        if i <= len(points)-2:
            addition = .5*(points[i][1]+points[i+1][1])*(points[i+1][0]-points[i][0])
            if mode  == "avg":
                # the value this trapezoid adds is the mean x it covers
                addition = addition*(points[i+1][0]+points[i][0])/2
            integral = integral + addition
    return integral


def averagex(points, min_guess, max_guess):
    avg_x = 0
    real_points = []
    for point in points:
        # for x: subtract the start, divide by width, mult by guess width
        real_x = (max_guess - min_guess)*(point[0]-plot_box.x)/(plot_box.w)
        real_y = abs((plot_box.y+plot_box.h)-point[1])
        real_points.append([real_x,real_y])
    # do trapezoidal rule to get integral
    norm = trapezoid(real_points, "norm")
    # norm to make actual prob distro, then get avg x
    for point in real_points:
        point[1] = point[1]/norm
    return trapezoid(real_points, "avg")


def wait(curr_player):
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if pg.mouse.get_pressed()[0]:
                pg.draw.rect(screen, WHITE, plot_small)
                if done_box.collidepoint(event.pos):
                    done_color = GREEN
                    curr_player.done = True
                    return done_color


def interpolate(points, old_points):
    add_points = []
    for i in range(len(points)):
        if points[i] in old_points:
            continue
        if i != len(points) - 1:
            if points[i] in add_points or points[i + 1] in add_points:
                continue
            mid_x = (points[i + 1][0] + points[i][0]) / 2.0
            mid_y = (points[i + 1][1] + points[i][1]) / 2.0
            add_points.append((mid_x, mid_y))
            points.append((mid_x, mid_y))


pg.init()
pg.display.set_caption('Pick a Distro!')
screen = pg.display.set_mode((WIDTH, HEIGHT))
overall_count = 0

# coordinates of box to drawn in, 600 by 280 (last args are w,h)

plot_box = pg.Rect(60, 135, 600, 280)
plot_small = pg.Rect(62, 137, 597, 277)

# coordinates of input box to enter names and guesses into

input_box = pg.Rect(60, 455, 140, 50)
input_small = pg.Rect(65 , 460, 133, 43)
done_box = pg.Rect(220, 460, 50,50)
done_color = BLACK

# variable initialization

active = False
text = ""
curr_input = ""
check = False
players = []
names = []  # purely for directing guessing
done = False
x_indexes = {}
click = False
guesses = {}

# fonts

font = pg.font.SysFont('couriernew', 20, bold=True)
smallfont  = pg.font.SysFont('couriernew', 16, bold=True)
tinyfont = pg.font.SysFont('couriernew', 12, bold=False)

# read in wager data

questions = {}
file1 = open('question_data/UK_wager_data', 'r')
file2 = open('question_data/canada_wager_data', 'r')
lines = []
for line in file1.readlines():
    if line != '\n':
        lines.append(line)
for line in file2.readlines():
    if line != '\n':
        lines.append(line)
count = 0
for i in range(len(lines)):
    # data in frorm: question, next line is ans
    if i != len(lines) - 1 and count % 2 == 0:
        # strip the newline character
        lines[i] = lines[i][:-1]
        questions[lines[i]] = float(lines[i + 1])
    count = count + 1
file1.close()
file2.close()

gamestart = False
ques = rand.choice(list(questions.keys()))
ans = questions[ques]

while not done:
    enter = False
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
        if event.type == pg.KEYDOWN:
            if not active:
                if event.key == pg.K_RETURN:
                    enter = True
                if event.key == pg.K_c:
                    points = []
            if active:
                if event.key == pg.K_RETURN:
                    curr_input = text
                    text = ""
                    active = False
                else:
                    if event.key == pg.K_BACKSPACE:
                        text = text[:-1]
                    text += event.unicode
                    pg.draw.rect(screen, WHITE, input_small)
                    text_surface = font.render(text, True, BLACK)
                    screen.blit(text_surface, (input_box.x+10, input_box.y+10))
                    pg.display.update(input_box)

        if pg.mouse.get_pressed()[0]:
            click = True
            if event.type == pg.MOUSEMOTION:
                if plot_box.collidepoint(event.pos) and gamestart:
                    points.append(event.pos)
            if input_box.collidepoint(event.pos):
                active = True
            if not input_box.collidepoint(event.pos):
                active = False
            if done_box.collidepoint(event.pos):
                check = True

    if gamestart:
        # check if done getting averages!
        avg_tot = 0
        for player in players:
            if player.avg != -1:
                avg_tot = avg_tot + 1
            else:
                continue
        if avg_tot == len(players):
            break
        # if first time starting distro drawing part of game
        if overall_count == 0:
            screen.fill(WHITE)
            pg.display.update()
            turn_count = 0
        # if guesses exist, then instead for first player without point set, get
        while turn_count <= num_players-1:
            curr_player = players[turn_count]
            if curr_player.done and len(curr_player.points) != 0:
                turn_count = turn_count + 1
            else:
                turn_count = 0
                break
        # draw box for min,max and plot so far here
        # but first interpolate between plotted points to get better curve
        if turn_count != num_players: # so if you havent done below for all the players
            points = curr_player.points
            old_points = curr_player.old_points
            # below is if not clicking but had been, meaning stopped doing points
            if not pg.mouse.get_pressed()[0] and click == True:
                click = False
                for i in range(3):
                    interpolate(points, old_points)
                old_points = points.copy()
    
            pg.draw.rect(screen, BLACK, plot_box, 3)  # last arg is width to make it outline
            pg.draw.rect(screen, done_color, done_box)
            for point in points:
                # screen.fill(BLACK, (point, (1, 1)))
                pg.draw.line(screen, BLACK, point, point, 3)
            pg.display.update([plot_box, done_box])
            
            # also display guesses !
            up_down = 0
            for player in players:
                if up_down%2 != 0:
                    guess_y_shift = -18
                    tick_shift = 10
                if up_down%2 == 0:
                    guess_y_shift = 0
                    tick_shift = -10
                # blit above or below alternating, commensurately in x based on max / min guesses
                # special min/max_guess printing to make it look nice
                if guesses[player.name] != max_guess and guesses[player.name] != min_guess:
                    surface = tinyfont.render(str(guesses[player.name]), True, BLACK)
                    text_w , text_h = tinyfont.size(str(guesses[player.name]))
                    guess_x = plot_box.x + float( plot_box.width*(guesses[player.name]/(min_guess+max_guess)) )
                    guess_y = plot_box.y + guess_y_shift
                    screen.blit(surface, (guess_x, guess_y))
                    # draw a tick mark for these middle guesses
                    pg.draw.line(screen, BLACK, (guess_x, plot_box.y), (guess_x, plot_box.y+tick_shift), 2)
                    # update the guess AND the tick
                    pg.display.update(pg.Rect(plot_box.x+float( plot_box.width*(guesses[player.name]/(min_guess+max_guess)) ), plot_box.y+guess_y_shift, text_w, text_h+10))                    
                    
                else:
                    surface = smallfont.render(str(guesses[player.name]), True, BLACK)
                    text_w , text_h = smallfont.size(str(guesses[player.name]))
                    if guesses[player.name] == max_guess:
                        screen.blit(surface, (plot_box.x+plot_box.width+2, plot_box.y))
                    if guesses[player.name] == min_guess:
                        screen.blit(surface, (plot_box.x-text_w, plot_box.y))
                up_down = up_down + 1
    
            # use enter or done box click as "done drawing"
            if check:
                if len(points) != 0:
                    filter_points = []
                    for i in range(len(points)):
                        point = points[i]
                        if point[0] in x_indexes.keys():
                            x_indexes[point[0]].append(i)
                        else:
                            x_indexes[point[0]] = []
                    for key in x_indexes.keys():
                        # add last instance or just add if empty (i.e. singular)
                        if len(x_indexes[key]) == 0:
                            for point in points:
                                if point[0] == key:
                                    index = points.index(point)
                            filter_points.append(points[index])
                        else:
                            filter_points.append(points[x_indexes[key][-1]])
                    points = []
                    for point in filter_points:
                        points.append(point)
    
                    # now reset x_indexes
                    x_indexes = {}

                    # draw between points to show final function, first sort them!
                    points.sort(key=lambda x: x[0])
                    for i in range(len(points)):
                        if i != len(points) - 1:
                            pg.draw.line(screen, BLACK, points[i], points[i+ 1], 1)
                    
                    curr_player.points = points.copy()
                    # makes done box go green once double clicked, single click blits above lines
                    pg.display.update(plot_box)
                    done_color = wait(curr_player)
                    pg.draw.rect(screen, done_color, done_box)
                    pg.display.update([plot_box,done_box])
                    pg.time.wait(200)
                    check = False
                    done_color = BLACK

            pg.draw.rect(screen, done_color, done_box)
            pg.display.update([plot_box,done_box])

        # now if all distros drawn, integrate and score!
        if turn_count == num_players:
            for player in players:
                player.avg = averagex(player.points, min_guess, max_guess)
                # now score eahc player, max of 100 alloted for perfect avg, otherwise scale with abs(error)
                round_score = 0
                if player.avg == ans:
                    round_score = 100
                else:
                    # only keep three decimal places for ease of reading
                    round_score = min(100,round(1/abs(ans-player.avg),3))
                player.score = player.score + round_score
                print("NAME: ", player.name)
                print("SCORE, AVG, ANS: ", player.score, player.avg, ans)

        overall_count = overall_count + 1

    if not gamestart:
        if overall_count == 0:
            screen.fill(WHITE)
            num_drawn = False
            name_drawn = False
            ques_drawn = False

        # choose players, ask for names, print first question
        if 'num_players' not in globals() and "num_players" not in locals():
            if num_drawn == False:
                surface = smallfont.render("Enter number of players", True, BLACK)
                text_w , text_h = smallfont.size("Enter number of players")
                screen.blit(surface, (input_box.x+10, input_box.y-20))
                pg.display.update(pg.Rect(input_box.x+10, input_box.y-20, text_w, text_h))
                num_drawn = True

            # ask for num players
            if not active:    # possibly covering after enter has been pressed?
                if curr_input != "":
                    # so once text input
                    num_players = int(float(curr_input))  #cover case of someone putting in decimal
                    curr_input = ""
                    pg.draw.rect(screen, WHITE, input_small)
        else:
            if len(players) != num_players:
                if name_drawn == False:
                    screen.fill(WHITE)
                    surface = smallfont.render("Enter a name", True, BLACK)
                    text_w , text_h = smallfont.size("Enter a name")
                    screen.blit(surface, (input_box.x+10, input_box.y-20))
                    pg.display.update(pg.Rect(input_box.x+10, input_box.y-20, text_w, text_h))
                    name_drawn = True
               
                # ask for player name, append
                if not active:
                    if curr_input != "":
                        # so once text input
                        players.append(Player(curr_input))
                        curr_input = ""
                        pg.draw.rect(screen, WHITE, input_small)
            
            if len(players) == num_players:
                # print (really, draw) the question to be answered (guessing!)
                if ques_drawn == False:
                    screen.fill(WHITE)
                    # wrap the text! split and do two surfaces
                    if len(ques) > 70:
                        ques1 = ques[:55]
                        ques2 = ques[55:]
                        surf1 = smallfont.render(ques1, True, BLACK)
                        surf2 = smallfont.render(ques2, True, BLACK)
                        text_w1 , text_h1 = smallfont.size(ques1)
                        screen.blit(surf1, (input_box.x+10, input_box.y-50))
                        text_w2 , text_h2 = smallfont.size(ques2)
                        screen.blit(surf2, (input_box.x+10, input_box.y-20))
                        if text_w1 > text_w2:
                            text_w1 = text_w
                        elif text_w2 >= text_w1:
                            text_w2 = text_w
                        pg.display.update(pg.Rect(input_box.x, input_box.y-80, text_w, text_h1))
                        ques_drawn = True
                    else:
                        surface = smallfont.render(ques, True, BLACK)
                        text_w , text_h = smallfont.size(ques)
                        screen.blit(surface, (input_box.x+10, input_box.y-20))
                        pg.display.update(pg.Rect(input_box.x, input_box.y-50, text_w, text_h))
                        ques_drawn = True

                if len(guesses.keys()) == num_players:
                    gamestart = True
                    active = False
                    overall_count = -1
                    # calculate these once (so here), for guess blitting above distro draw box
                    min_guess = min(guesses.values())
                    max_guess = max(guesses.values())

                elif len(guesses.keys()) != num_players:
                    # if no guesses yet, build list of names to prod
                    if len(guesses.keys()) == 0:
                        for player in players:
                            names.append(player.name)
                    
                    old_guess_count = len(guesses.keys())
                    # ask first to guess        
                    name = names[0]
                    name_surface = smallfont.render("["+name+" please guess]", True, BLACK)
                    text_w , text_h = smallfont.size("["+name+" please guess]")
                    screen.blit(name_surface, (input_box.x+10, input_box.y+55))
                    pg.display.update(pg.Rect(input_box.x+10, input_box.y+55, text_w, text_h))
                    #now that theyve guessed is below
                    if not active:
                        if curr_input != "":
                            guesses[name] = int(curr_input)
                            curr_input = ""
                            pg.draw.rect(screen, WHITE, input_small)
                            names.pop(0)
                   	# if a new guess has been recorded, blank out old guess prod
                    if len(guesses.keys()) != old_guess_count:
                        screen.blit(name_surface, (input_box.x+10, input_box.y+55))
                        pg.draw.rect(screen, WHITE, pg.Rect(input_box.x+10, input_box.y+55, text_w+10,text_h))

        # general drawing each time
        if not active:
            pg.draw.rect(screen, BLACK, input_box, 3)
        if active:
            pg.draw.rect(screen, BLUE, input_box, 3)
        pg.display.update()

    overall_count = overall_count +  1
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


class Button:
    def __init__(self,box_type,color,x,y,w,h):
        self.type = box_type
        self.clicked = False
        self.rect = pg.Rect(x,y,w,h)
        self.color = color
        self.text = ""
        self.enter = False
        self.push_count = 0

    def handle(self,event):
        if pg.mouse.get_pressed()[0]:
            self.clicked = True
        if event.type == pg.MOUSEBUTTONUP and self.type == "draw":
            self.clicked = False
            # remove duplicate x axis points (make it a function!)
            curr_player.points = filter_duplicate(points)
            # beef up the points a bit (fill in between!)
            curr_player.points = interpolate(points, old_points)
            curr_player.points.sort(key=lambda x: x[0])
            screen.fill(WHITE)

        if self.clicked:
            if self.type == "text":
                self.color = BLUE
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        self.enter = True
                        self.clicked = False
                        self.cover()
                    if event.key == pg.K_BACKSPACE:
                        self.text = self.text[:-1]
                    self.text += event.unicode
                    self.cover()
            
            if self.type == "button":
                # cover done box, new game, etc.
                if pg.mouse.get_pressed()[0]:
                    self.push_count = self.push_count + 1
            
            if self.type == "draw":
                if event.type == pg.MOUSEMOTION and gamestart:
                    points.append(event.pos)

        if not self.clicked:
            if self.type == "text":
                self.color = BLACK
            if event.type == pg.KEYDOWN and self.type == "draw":
                if event.key == pg.K_c:
                    curr_player.points.clear()
                    screen.fill(WHITE)

    # more text stuff? maybe cursor blinking!
    def cover(self):
        #cover up box, by overlaying smalller white box
        pg.draw.rect(screen, WHITE, pg.Rect(self.rect.x+5 , self.rect.y+5, self.rect.w-7, self.rect.h-7))
        if not self.enter:
            text_surface = font.render(self.text, True, BLACK)
            screen.blit(text_surface, (self.rect.x+10, self.rect.y+10))
        pg.display.update(self.rect)

    def title(self,title_text,color,h):
        surface = smallfont.render(title_text, True, color)
        text_w , text_h = smallfont.size(title_text)
        screen.blit(surface, (self.rect.x+10, self.rect.y-20+h))
        pg.display.update(pg.Rect(self.rect.x+10, self.rect.y-20+h, text_w, text_h))


# checks for largest list index element with given first value, removes lower index copies
def filter_duplicate(points):
    x_indexes = {}
    filter_points = []
    for i in range(len(points)):
        point = points[i]
        if point[0] in x_indexes:
            if i > x_indexes[point[0]][0]:
                filter_points.remove(x_indexes[point[0]][1])
                filter_points.append(point)
                x_indexes[point[0]] = [i,point]
        if point[0] not in x_indexes:
            x_indexes[point[0]] = [i,point]
            filter_points.append(point)
        #print("x_indexes: ", x_indexes)
        #print("filter_points: ", filter_points)
    return filter_points


# performs numerical integration via trapezoidal rule
# normalization, < guess >, or <1/abs(ans-guess)>
def trapezoid(points,mode):
    integral = 0
    for i in range(len(points)):
        if i <= len(points)-2:
            # skip where obviously intended to be discontinuous!
            if abs(points[i+1][0]-points[i][0]) >= 2:
                continue
            addition = .5*(points[i][1]+points[i+1][1])*(points[i+1][0]-points[i][0])
            mid_x = (points[i+1][0]+points[i][0])/2
            if mode  == "score":
                # the value this trapezoid adds is the mean x it covers
                #addition = addition*(points[i+1][0]+points[i][0])/2
                if ans != mid_x:
                    if 1/abs(ans-mid_x) <= 1000:
                        addition = addition*(1/(abs(ans-mid_x)))
                    else:
                        print("1000 weight")
                        addition = addition*1000
                else:
                    print("1000 weight")
                    addition = addition*1000
            if mode == "avg":
                # the value this trapezoid adds is the mean x it covers
                addition = addition*mid_x
            integral = integral + addition
    return integral


# projects drawn points into guess space, converts to probability distribution
# then calls trapezoid to return <1/abs(ans-guess)>, < guess > 
def guess_integral(points, min_guess, max_guess):
    avg_x = 0
    real_points = []
    for point in points:
        # for x: subtract the start, divide by width, mult by guess width
        real_x = (max_guess - min_guess)*(point[0]-plot_box.rect.x)/(plot_box.rect.w)
        real_y = abs((plot_box.rect.y+plot_box.rect.h)-point[1])
        real_points.append([real_x,real_y])
    # do trapezoidal rule to get integral
    norm = trapezoid(real_points, "norm")
    # norm to make actual prob distro, then get avg x
    for point in real_points:
        point[1] = point[1]/norm
    return trapezoid(real_points, "score"), trapezoid(real_points, "avg")


# stops game when to let distribution be reviewed
# returns new color for done plotting button once pressed
def wait():
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if pg.mouse.get_pressed()[0]:
                screen.fill(WHITE)
                if done_box.rect.collidepoint(event.pos):
                    return True


# interpolates between drawn points, 
# to make up for great mouse speed
def interpolate(curr_points, old_points):
    curr_points.sort(key=lambda x: x[0])
    add_points = []
    for i in range(len(points)):
        if curr_points[i] in old_points:
            continue
        if i != len(curr_points) - 1:
            if curr_points[i] in add_points or curr_points[i + 1] in add_points:
                continue
            # dont interpolate between points that arent "next" to each other
            if abs(curr_points[i+1][0]- curr_points[i][0]) >= 30:  # MIGHT NEED ADJUSTING!!
                continue
            mid_x = (curr_points[i + 1][0] + curr_points[i][0]) / 2.0
            mid_y = (curr_points[i + 1][1] + curr_points[i][1]) / 2.0
            add_points.append((mid_x, mid_y))
            curr_points.append((mid_x, mid_y))
    return curr_points


pg.init()
pg.display.set_caption('Pick a Distro!')
screen = pg.display.set_mode((WIDTH, HEIGHT))
clock = pg.time.Clock()
overall_count = 0   # will track game progression


# coordinates of box to drawn in, 600 by 280 (last args are w,h)

plot_box = Button("draw", BLACK, 60, 135, 600, 280)

# coordinates of input box to enter names and guesses into

input_box = Button("text", BLACK, 60, 455, 140, 50)
done_box = Button("button", BLACK, 730, 310, 200, 50)

boxes = [input_box,done_box,plot_box]

# variable initialization

players = []
names = []  # purely for directing guessing
quit = False
guesses = {}

# fonts

font = pg.font.SysFont('couriernew', 20, bold=True)
smallfont  = pg.font.SysFont('couriernew', 18, bold=False)
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
    if i != len(lines) - 1 and count % 2 == 0:
        lines[i] = lines[i][:-1]
        questions[lines[i]] = float(lines[i + 1])
    count = count + 1
file1.close()
file2.close()

gamestart = False
ques = rand.choice(list(questions.keys()))
ans = questions[ques]

while not quit:
    enter = False
    # have flag for mous click, unclick, pressed return, backspace, quitting...
    mouse_pos = pg.mouse.get_pos()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            quit = True
        #if pg.mouse.get_pressed()[0]:
        #    click = True
        for box in boxes:
            if box.rect.collidepoint(mouse_pos):
                box.handle(event)

    if not gamestart:
        # continue set up for this round
        if overall_count == 0:
            screen.fill(WHITE)
            num_drawn = False
            name_drawn = False
            ques_drawn = False

        # choose players, ask for names, print first question
        if 'num_players' not in globals() and "num_players" not in locals():
            if num_drawn == False:
                input_box.title("Enter number of players", BLACK, -10)
                num_drawn = True

            # ask for num players
            if input_box.text != "" and input_box.enter == True:    # so if some text has been entered
                    num_players = int(float(input_box.text))  #cover case of someone putting in decimal
                    input_box.enter = False
                    input_box.text = ""
                    #  DONT NEED: fill with white once have num! pg.draw.rect(screen, WHITE, pg.Rect(input_box.x+5 , input_box.y+5, input_box.w-7, input_box.h-7))
                    screen.fill(WHITE)

        else:
            if len(players) != num_players:
                if name_drawn == False:
                    input_box.title("Enter a name", BLACK, -10)
                    name_drawn = True
               
                # ask for player name, append
                if input_box.text != "" and input_box.enter == True:
                    players.append(Player(input_box.text))
                    input_box.enter = False
                    input_box.text = ""

            if len(players) == num_players:
                # print (really, draw) the question to be answered (guessing!)
                if ques_drawn == False:
                    screen.fill(WHITE)
                    char_count = 0
                    cut_count = 0
                    cutoff = 70
                    # wrap the text! split per cutoff characters or so
                    for i in range(len(ques),-1,-1):
                        if char_count >= cutoff:
                            input_box.title(ques[i-1:(i-1+cutoff)],BLACK,-30*(cut_count))
                            char_count = 0
                            cut_count = cut_count + 1
                        char_count = char_count + 1
                    
                     # if didnt finish, blit rest
                    if char_count != 0:
                        input_box.title(ques[:char_count],BLACK,-30*(cut_count))
                    ques_drawn = True

                if len(guesses.keys()) == num_players:
                    gamestart = True
                    overall_count = 0
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
                    input_box.title("["+name+" please guess]",BLACK,75)
                    #now that theyve guessed is below
                    if input_box.text != "" and input_box.enter == True:
                        guesses[name] = int(input_box.text)
                        input_box.cover()
                        input_box.enter = False
                        input_box.text = ""
                        names.pop(0)
                    
                    # if a new guess has been recorded, blank out old guess prod
                    if len(guesses.keys()) != old_guess_count:
                        text_w , text_h = smallfont.size("["+name+" please guess]")
                        pg.draw.rect(screen, WHITE, pg.Rect(input_box.rect.x+10, input_box.rect.y+54, text_w+10,text_h))
                        pg.display.update(pg.Rect(input_box.rect.x+10, input_box.rect.y+54, text_w+10,text_h))
                        # show what has been guessed so far
                        guess_str = ""
                        for guess in guesses.values():
                            guess_str = guess_str + " "+str(guess)
                        input_box.title("guessed so far:"+guess_str,BLACK,105)

    if gamestart:
        # if first time starting distro drawing part of game
        if overall_count == 0:
            points = []
            guess_pos = {}
            # build out dict just once for guess tick positions
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
                    guess_x = plot_box.rect.x + float( plot_box.rect.w*(guesses[player.name]/(min_guess+max_guess)) )
                    guess_y = plot_box.rect.y + guess_y_shift
                    guess_pos[(guess_x, guess_y)] = [surface, tick_shift]                                       
                else:
                    surface = smallfont.render(str(guesses[player.name]), True, BLACK)
                    text_w , text_h = smallfont.size(str(guesses[player.name]))
                    if guesses[player.name] == max_guess:
                        guess_pos[(plot_box.rect.x+plot_box.rect.w+2, plot_box.rect.y)] = [surface, 0]  # use 0 for no tick! 
                    if guesses[player.name] == min_guess:
                        guess_pos[(plot_box.rect.x-text_w-5, plot_box.rect.y)] = [surface, 0]
                up_down = up_down + 1
            
            plot_box.clicked = False
            screen.fill(WHITE)
            pg.display.update()
        
        # who's turn is it? if completely done, break (or new round setup thing!)
        turn_count = 0
        for player in players:
            if len(player.points) == 0:
                curr_player = player
                break
            else:
                if player.done != True:
                    curr_player = player
                    break
            turn_count = turn_count + 1
        if turn_count == len(players):
            for player in players:
                player.score, player.avg = guess_integral(player.points, min_guess, max_guess)
                print("NAME: ", player.name)
                print("SCORE, AVG, ANS: ", player.score, player.avg, ans)
            break
        #elif turn_count

        # tell them its their turn, that they can clear, how to finish plot
        plot_box.title("["+player.name+" please plot]", BLACK, 310)
        plot_box.title("Hover over plotting and press c to clear all points", BLACK, 340)
        done_box.title("CLICK HERE TWICE", BLACK, -60)
        done_box.title("TO FINISH PLOTTING", BLACK, -30)

        points = curr_player.points
        old_points = curr_player.old_points

        if done_box.push_count == 1:
            print("PRESSED!!!")
            if len(curr_player.points) != 0:
                done_box.color = GREEN
                pg.draw.rect(screen, done_box.color,done_box.rect)
                pg.display.update(done_box.rect)
                for i in range(len(points)):
                    if i != len(points) - 1:
                        # skip where obviously intended to be discontinuous!
                        if abs(points[i+1][0]-points[i][0]) >= 30:
                            continue
                        pg.draw.line(screen, BLACK, points[i], points[i+1], 1)
                pg.display.update(plot_box.rect)
                curr_player.done = wait()
                done_box.color = BLACK
                done_box.push_count = 0
                screen.fill(WHITE)
                if turn_count != len(players) - 1:
                    turn_count = turn_count + 1
                    curr_player = players[turn_count]

    # general drawing calls
    if not gamestart:
        pg.draw.rect(screen, input_box.color, input_box, 3)
    if gamestart:
        pg.draw.rect(screen, done_box.color, done_box.rect)
        pg.draw.rect(screen, plot_box.color, plot_box.rect, 3)
        for point in curr_player.points:
            pg.draw.circle(screen, BLACK, point, 1, 0)
        # draw guesses AND ticks
        for position in guess_pos.keys():
            screen.blit(guess_pos[position][0], position)
            if guess_pos[position][1] != 0:  # if there's also a tick!
                pg.draw.line(screen, BLACK, (position[0], plot_box.rect.y), (position[0], plot_box.rect.y+guess_pos[position][1]), 2)

    pg.display.update()
    clock.tick(120)
    overall_count = overall_count +  1

# TO CONSIDER: slowness of draw, right skipping distances... in lines, TRAPezoid, interpolate (all important) ..> interp can make points where there shouldn't be!

# black with white text? color of font for eahc bit?
# maybe make plot buttton better
# plot color ... choose?? would be button
# press "f" for flatline distro
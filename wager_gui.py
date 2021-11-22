import pygame as pg
import pygame_gui as pg_gui
import numpy as np
import copy
import random as rand
import sys
import math
from string import printable


BRIGHTBLUE = (0, 237, 250)
YELLOW = (250, 215, 42)
DARKGREEN = (87,151,26)
PURPLE = (122,129,255)
BLACK = (0,0,0)
WHITE = (255, 255, 255)
LIGHTGRAY = (220,220,220)

WIDTH = 1200
HEIGHT = 800


class Player:
	def __init__(self, name):
	    self.name = name
	    self.score = []
	    self.points = []
	    self.range = None
	    self.done = False
	    self.color = BLACK
	    self.bell = False


def get_range_winner(players):
	# now need those who won range challenge
	win_p = []
	within = {}
	for p in players:
		ord_range = sorted(p.range)
		if (ans >= ord_range[0] and ans <= ord_range[1]):
			within[p] = abs(p.range[1]-p.range[0])
	key_list = list(within.keys())
	# if somebody covered correct answer!
	if len(key_list) > 0:
		# make extra long example
		best_range = abs(key_list[0].range[1] - key_list[0].range[0])+100
		for p in key_list:
			if abs(p.range[1]-p.range[0]) <= best_range:
				if len(win_p) > 0:
					win_p.pop()
				win_p.append(p)
				best_range = abs(p.range[1]-p.range[0])
	
	return win_p


# complicated procedure to get the ticks to blit on the plot window, which are players' guesses
def get_ticks():
	guesses = []
	ticks = []
	values = []
	# get max / min rage ends
	min_guess = players[0].range[0] + 1
	max_guess = -1
	for p in players:
		if p.range[0] < min_guess:
			min_guess = p.range[0]
		if p.range[1] > max_guess:
			max_guess = p.range[1]

	up_down = 0
	max_covered = False   	# vars to track egde of plot box ticks
	min_covered = False		# only want one name in each spot!

	# construct list of ends
	end_list = []
	end_name = {}
	for p in players:
		for end in p.range:
			end_list.append(end)
			if end not in end_name:
				end_name[end] = [p.name, p.color]
			else:
				if end != min_guess and end != max_guess:
					end_name[end][0] = end_name[end][0] + "," + p.name

	# remove double ticks
	end_list = list(set(end_list))
	
	# sort so tick alternating works
	end_list = sorted(end_list)
	
	for end in end_list:
		scaled_guess = plot_box.rect.w*end/(max_guess + min_guess)
		# with the above, then all guesses become 0->1 * coord scale of box, plot with this val in x!
		if up_down%2 != 0:
			guess_y_shift = -24
			tick_shift = 12
		if up_down%2 == 0:
			guess_y_shift = 4
			tick_shift = -12
		
		# blit above or below alternating, commensurately in x based on max / min guesses
		# special min/max_guess printing to make it look nice
		# blit both range[0] and range[1], with initals... so for each player, do both ends
		# ^ now check the ends, if max or min, treat as so..
		if (end != max_guess and end != min_guess):
			surface = smallfont.render(str(end)+", "+end_name[end][0], True, end_name[end][1])
			text_w , text_h = smallfont.size(str(end)+","+end_name[end][0])
			guess_x = plot_box.rect.x + float(scaled_guess)+4
			if up_down%2 != 0:
				guess_y = plot_box.rect.y + guess_y_shift
				# draw a tick mark for these middle guesses
				ticks.append([(guess_x, plot_box.rect.y),(guess_x, plot_box.rect.y+tick_shift)])
			if up_down%2 == 0:
				guess_y = plot_box.rect.y + plot_box.rect.h + guess_y_shift
				# now tick up from bottom!
				ticks.append([(guess_x, plot_box.rect.y+plot_box.rect.h-4),(guess_x, plot_box.rect.y+(plot_box.rect.h-4)+tick_shift)])
			values.append([surface, guess_x, guess_y])
		else:
			surface = smallfont.render(str(end)+", "+end_name[end][0], True, end_name[end][1])
			text_w , text_h = smallfont.size(str(end)+","+end_name[end][0])
			if end == max_guess and not max_covered:
				values.append([surface,plot_box.rect.x+plot_box.rect.w+3, plot_box.rect.y])
				max_covered = True
			if end == min_guess and not min_covered:
				values.append([surface, plot_box.rect.x-(text_w+10),plot_box.rect.y])
				min_covered = True

		up_down = up_down + 1

	win_p = get_range_winner(players)

	return ticks, values, min_guess, max_guess, win_p


# draw the small lines that are the guess ticks on the plot window
def draw_ticks(ticks, values):
	for val in values:
		screen.blit(val[0],(val[1],val[2]))
	for tick in ticks:
		# draw guess guiding lines on plot box
		pg.draw.line(screen, PURPLE, (tick[0][0],plot_box.rect.y+5), (tick[1][0],plot_box.rect.y+plot_box.rect.h-8), width=2)
		pg.draw.line(screen, BLACK, tick[0], tick[1], width=4)


# look through players and return both the top score and if there are ties
def top_score(players):
	max_score = -1
	top_p = players[0]
	doubles = []
	for p in players:
		if round(p.score[-1],3) == round(max_score,3):
			# now we have a double (or close one), have to say so!
			doubles.append(p.name)
		# new highest found
		if p.score[-1] > max_score:
			max_score = p.score[-1]
			top_p = p
	return top_p, doubles


# draw bar graph, sampling points semi-sparesly from real
# match width with sampling, color by proximity to guess
# animate one bar per tiime, for "calculating" effect
def score_animate(top_p, min_guess, max_guess, ans):
	# order them first... so bars are drawn left to right
	top_p.points.sort(key=lambda s:s[0])
	num_p = int(.5*len(top_p.points))
	less_points = []
	jump = 2
	index = 0
	# filter points a bit
	while len(less_points) < num_p:
		if index >= len(top_p.points):
			break
		less_points.append(top_p.points[index])
		index = index + jump

	# if they did bell, below can break, do something else
	if not top_p.bell:		
		# first construct bar locations / vals
		bars = []
		for i in range(len(less_points)):
			point = less_points[i]
			bar_w = 4
			if i != len(less_points) - 1:
				bar_w = abs(less_points[i+1][0]-point[0])
	
			# rect to blit at the left real x
			bar = pg.Rect(point[0],point[1],bar_w,plot_box.rect.y+(plot_box.rect.h-point[1])-6)
			# need guess space value
			real_x = min_guess + ((max_guess - min_guess)*(point[0]-plot_box.rect.x)/(plot_box.rect.w))
			if abs(real_x - ans) > .001:
				# if not infinite for our scaling!
				bars.append([bar,(abs(real_x-ans))**(-.3)] )
			else:
				bars.append([bar,1000])

		# then draw them with color gradient
		max_real_x = max([bar_data[1] for bar_data in bars])
		min_real_x = min([bar_data[1] for bar_data in bars])
		# when at min -> black, when at max -> red
		for bar in bars:
			curr_x = bar[1]
			red = 1.3*255*(curr_x - min_real_x)/(max_real_x - min_real_x)
			# let it max out, and just slice back when needed
			if red > 255:
				red = 255
			color = [red,0,0]
			pg.draw.rect(screen, color, bar[0])
			pg.time.delay(65)
			pg.display.update()
	
	if top_p.bell:
		# just draw circles at points based on relative scoring...
		max_val = -1
		for point in less_points:
			real_x = min_guess + ((max_guess - min_guess)*(point[0]-plot_box.rect.x)/(plot_box.rect.w))
			if abs(real_x - ans) > .001:
				# if not infinite for our scaling!
				red = 255*(1/abs(real_x-ans))/1000
			else:
				red = 255

			pg.draw.circle(screen, [red,0,0], (point[0],plot_box.rect.h+plot_box.rect.y-4), 10, width=4)
			pg.time.delay(65)
			pg.display.update()
	
	return None


# for either guessing or plotting, pick first player who hasnt gone yet
def pick_player(cond):
	curr_player = players[-1]
	count = 0
	for i in range(len(players)):
		p = players[i]
		if cond == "guess":
			if p.range == None:
			    curr_player = p
			    break
		
		if cond == "plot":
			if p.done == False:
			    curr_player = p
			    break

		count = count + 1

	return curr_player, count


# pick a random question, return the split up surfs and answer
def get_ques_surfs(ques, ans, round_count, size):
	quesfont = pg.font.SysFont("aotffolkpro", size, bold=True)
	y_ques_surfs = []
	p_ques_surfs = []
	# make SURE has a question mark
	if "?" not in ques:
		ques = ques + "?"
	words = ques.split(" ")
	for word in words:
		y_ques_surfs.append(quesfont.render(word, True, YELLOW))
		p_ques_surfs.append(quesfont.render(word, True, PURPLE))

	ques_num = bigfont.render(str(round_count), True, DARKGREEN)
	
	return y_ques_surfs, p_ques_surfs, ques_num


# blit text, but wrap it based on max_width and where it starts on the screen
def blit_wrap(surf_set, start_x, start_y, max_width):
	# adjust these to adjust possible drop shadow
	drop_x = -2
	drop_y = 2
	total_width = 0  # track for wrapping!
	y_offset = 0
	num_words = 0
	for i in range(len(surf_set[0])):
		print_width = start_x+total_width+num_words*10
		# if we have a drop shadow for this wrap
		if len(surf_set) > 1:
			shadow_word = surf_set[1][i]
			screen.blit(shadow_word,[print_width+10+drop_x,start_y+y_offset*40 + drop_y])  # 40 is avg height of words
		# always blit word, this is the general text
		word = surf_set[0][i]
		screen.blit(word,[print_width+10,start_y+y_offset*40])
		curr_width = word.get_width()
		total_width = total_width + curr_width
		num_words = num_words + 1
		if total_width > max_width:
			total_width = 0
			num_words = 0
			y_offset = y_offset + 1


# function to collect code for displaying intro screen
def show_intro(intro, intro_length):
	intro_timer = 0
	screen.fill(WHITE)
	screen.blit(intro, [0,0])
	pg.display.update()
	while intro_timer < intro_length:
	    # adds clock time until "intro_length" reached
	    dt = clock.tick()
	    intro_timer = intro_timer + dt
	    for event in pg.event.get():
	        if event.type == pg.QUIT:
	            pg.quit()
	            sys.exit()


# when called, present current table of scores (meaning up to that point)
def show_score(table, players):
	x_offset = 120
	y_offset = 20
	# blit table background
	screen.blit(table, [plot_box.rect.x + x_offset, plot_box.rect.y + y_offset])
	# then blit lines of table
	count = 0
	for p in players:
		line = font.render(p.name+": "+str(round(sum(p.score),4)), True, BLACK)
		screen.blit(line, [plot_box.rect.x + x_offset + 30, plot_box.rect.y + y_offset + 124 + count*40])
		count = count + 1


# performs numerical integration via trapezoidal rule
# normalization, < guess >, or <1/abs(ans-guess)>
def trapezoid(points,mode):
	integral = 0
	for i in range(len(points)):
	    if i <= len(points)-2:
	        # skip where obviously intended to be discontinuous ?
	        #if abs(points[i+1][0]-points[i][0]) >= 5:
	        #    continue
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
	    real_x = min_guess + ((max_guess - min_guess)*(point[0]-plot_box.rect.x)/(plot_box.rect.w))
	    real_y = abs((plot_box.rect.y+plot_box.rect.h)-point[1])
	    real_points.append([real_x,real_y])
	# do trapezoidal rule to get integral
	norm = trapezoid(real_points, "norm")
	# norm to make actual prob distro, then get avg x
	for point in real_points:
	    point[1] = point[1]/norm
	return trapezoid(real_points, "score"), trapezoid(real_points, "avg")


# helper func for construct_norm
def gauss(x,m,s_dev):
	const = 1/(math.sqrt(2*math.pi*(s_dev)**2))
	return const*math.exp( (-(x-m)**2)/(2*(s_dev)**2) )


# return a list of points that form a gaussian in guess space;
# the actual coordinates are in plot space, though!
# center on mean, +- std dev on each side if possible
def construct_norm(mean, std_dev):
	num_points = 200
	norm_points = []
	used_xs = []
	# add one point that is exactly the mean
	x = mean
	plot_x = (x-min_guess)*(plot_box.rect.w)/(max_guess-min_guess) + plot_box.rect.x
	plot_y = plot_box.rect.h - plot_box.rect.h*gauss(x, mean, std_dev)  # minus to draw curve from below!
	norm_points.append([plot_x,plot_y])
	# now fill the list until sizeable
	while len(norm_points) < num_points:
		x = rand.uniform(mean-5*(std_dev), mean+5*(std_dev))
		if x > max_guess or x < min_guess:
			continue
		if x in used_xs:
			# should essentially never happen...
			continue
		used_xs.append(x)
		# translating guess space to plot space! (-4 here to account for border width)
		plot_y = (plot_box.rect.h - plot_box.rect.h*gauss(x,mean,std_dev)) + (plot_box.rect.y-8)
		plot_x = (x-min_guess)*(plot_box.rect.w)/(max_guess-min_guess) + plot_box.rect.x
		norm_points.append([plot_x,plot_y])

	# sort, as we will draw lines with these
	norm_points.sort(key=lambda s:s[0])
	return norm_points


pg.init()

# courier_new = pg.font.SysFont('couriernew', 20, bold=True)
# /System/Library/Fonts/Supplemental/Courier\ New.ttf

pg.display.set_caption('Pick a Distro!')
screen = pg.display.set_mode((WIDTH, HEIGHT))
background = pg.Surface((WIDTH, HEIGHT))
background.fill(pg.Color('#FFFFFF'))
clock = pg.time.Clock()
manager = pg_gui.UIManager((WIDTH, HEIGHT), theme_path='theme.json')
manager_plot = pg_gui.UIManager((WIDTH, HEIGHT), theme_path='theme_plot.json')
manager_score = pg_gui.UIManager((WIDTH, HEIGHT), theme_path='theme_score.json')
manager_color = pg_gui.UIManager((WIDTH, HEIGHT), theme_path='theme_color.json')

# inital settings

players = []
curr_color = pg.Color(0,0,0)
new = True
new_ques = True
plotting = False
plot_click = False
next_check = False
score_check = False
norm_pick = False
flat_plot = False
mean = None
std_dev = None
points = []
response = ""
win_names  = ""   # names only of best ranges
ticks = []
round_count = 1
num_rounds = 4
range_boost  = 10  # how much  socre increased by range win

# get vals from args
num_players = len(sys.argv)
for i in range(1,num_players):
	players.append(Player(sys.argv[i]))

# fonts

#font = pg.font.SysFont('verdana', 14, bold=True)
font = pg.font.Font("ProFolk.otf",28, bold=True)
bigfont = pg.font.Font("ProFolk.otf",140, bold=True)
smallfont = pg.font.Font("ProFolk.otf",22, bold=True)
tinyfont = pg.font.SysFont('couriernew', 12, bold=False)

# images

cursor = pg.image.load('curs_pic.png').convert_alpha()
cursor = pg.transform.scale(cursor, (int(25), int(25)) )
cursor_dim = cursor.get_rect().size
ques_base = pg.image.load('ques_base.png').convert_alpha()
plot_base = pg.image.load('plot_base.png').convert_alpha()
intro = pg.image.load("intro.png").convert_alpha()
score_descr = pg.image.load('score_descr.png').convert_alpha()
table = pg.image.load('table.png').convert_alpha()

# read in wager data

questions = {}
file1 = open('question_data/UK_wager_data', 'r')
file2 = open('question_data/canada_wager_data', 'r')
lines = [] 
for line in file1.readlines():
	if line != '\n':
	    line_list = list(filter(lambda x: x in printable, line))
	    line = "".join(line_list)
	    lines.append(line)
for line in file2.readlines():
	if line != '\n':
	    line_list = list(filter(lambda x: x in printable, line))
	    line = "".join(line_list)
	    lines.append(line)
count = 0
for i in range(len(lines)):
	if i != len(lines) - 1 and count % 2 == 0:
	    questions[lines[i]] = lines[i + 1]
	count = count + 1

# get first question, and corresponding surfs
ques = rand.choice(list(questions.keys()))
ans  = float(questions[ques])
y_ques_surfs, p_ques_surfs, ques_num = get_ques_surfs(ques, ans, round_count, 36)

# set up recurring labels and boxes for game
input_box = pg_gui.elements.UITextEntryLine(pg.Rect((42,670), (400, 200)), manager=manager, object_id="#main_text_entry")

label_box = pg_gui.elements.UILabel(pg.Rect(42, 610, 400, 50), 'poop', manager=manager, object_id='#label_box')

plot_box = pg_gui.elements.UIButton(pg.Rect(100, 82, 920, 490), "", manager=manager_plot, object_id='#plot_box')

done_box = pg_gui.elements.UIButton(pg.Rect(460, 603, 200, 50), "DONE", manager=manager, object_id='#done_box')

score_box = pg_gui.elements.UIButton(pg.Rect(680, 603, 250, 50), "SCORE TABLE", manager=manager_score, object_id='#score_box')

norm_box = pg_gui.elements.UIButton(pg.Rect(720, 685, 100, 40), "BELL", manager=manager, object_id='#norm_box')

flat_box = pg_gui.elements.UIButton(pg.Rect(860, 685, 100, 40), "FLAT", manager=manager, object_id='#flat_box')

next_box = pg_gui.elements.UIButton(pg.Rect(1000, 635, 150, 100), "NEXT", manager=manager, object_id='#next_box')

label_score = pg_gui.elements.UILabel(pg.Rect(42, 650, 400, 50), "", manager=manager, object_id='#label_score')

label_correct = pg_gui.elements.UILabel(pg.Rect(42, 690, 400, 50), "", manager=manager, object_id='#label_correct')

color_pick = pg_gui.windows.UIColourPickerDialog(pg.Rect(580, 383, 580, 391), manager=manager_color, window_title = "Pick a color!", object_id="#color_picker")

range_win = pg_gui.elements.UILabel(pg.Rect(24,  742, 400,  30), "", manager=manager_score, object_id="#range_win")

# show the intro image for a little bit first!
show_intro(intro, 400)

screen.fill(WHITE)
is_running = True

while is_running:
	if not new_ques and not plotting:
		if next_check:
			# need to hide stuff once next button pressed
			# and reset some initial game settings
			next_box.hide()
			label_score.hide()
			label_correct.hide()
			range_win.hide()
			input_box.show()
			ques = rand.choice(list(questions.keys()))
			ans  = float(questions[ques])
			y_ques_surfs, p_ques_surfs, ques_num = get_ques_surfs(ques, ans, round_count, 36)
			for p in players:
				p.points = []
				p.done = False
				p.range = None
			new_ques = True
			screen.blit(background, (0, 0))
			next_check = False
			win_names = ""
			# best move is to actually rebuild this
			color_pick = pg_gui.windows.UIColourPickerDialog(pg.Rect(580, 383, 580, 391), manager=manager_color, window_title = "Pick a color!", object_id="#color_picker")
	# when not waiting for next button
	else:
		screen.blit(background, (0, 0))
	delay = 0
	time_delta = clock.tick(60) / 1000.0

	# deal with all user input
	for event in pg.event.get():
	    if event.type == pg.QUIT:
	        is_running = False
	    
	    # these are pygame GUI specific events
	    if event.type == pg.USEREVENT:
	    	if event.user_type == pg_gui.UI_COLOUR_PICKER_COLOUR_PICKED:
	    		if event.ui_element == color_pick:
	    			curr_color = event.colour
	    			# to make this not disappear, rebuild  it
	    			color_pick = pg_gui.windows.UIColourPickerDialog(pg.Rect(580, 383, 580, 391), manager=manager_color, window_title = "Pick a color!", object_id="#color_picker")

	    	if event.user_type == pg_gui.UI_TEXT_ENTRY_FINISHED:
	    		if event.ui_object_id != "#color_picker.colour_channel_editor.text_entry_line":
	    			response = event.text
	    			input_box.set_text("")
	    		if event.ui_object_id == "#main_text_entry":
	    			if new_ques:
	    				curr_player.color = copy.deepcopy(curr_color)
	    				curr_color = pg.Color(0,0,0)
	    	
	    	if event.user_type == pg_gui.UI_BUTTON_PRESSED:
	    		# cover buttons available only while plotting
	    		if plotting:
	    			if event.ui_element == plot_box:
	    				if plot_click == False:
	    					plot_click = True
	    					pg.mouse.set_visible(False)
	    				else:
	    					plot_click = False
	    					pg.mouse.set_visible(True)
	    			if event.ui_element == done_box:
	    				if len(curr_player.points) > 1:
	    					curr_player.done = True
	    					points = []
	    					score, avg = guess_integral(curr_player.points, min_guess, max_guess)
	    					print("name, score, avg: ", curr_player.name, score, avg)
	    					curr_player.score.append(100*score)	    		
	    			# includes check for flat box, cant do both!
	    			if event.ui_element == norm_box and not flat_plot and not score_check:
	    				input_box.show()
	    				plot_click = False
	    				norm_pick = True
	    				mean = None
	    				std_dev = None
	    				curr_player.points = []
	    			# includes check for bell curve, cant do both!
	    			if event.ui_element == flat_box and not norm_pick and not score_check:
	    				plot_click = False
	    				curr_player.points = []
	    				flat_plot = True

	    		if event.ui_element == next_box:
	    			next_check = True

	    		if event.ui_element == score_box and not plotting:
	    			score_check = True
	    
	    if event.type == pg.MOUSEMOTION:
	    	# if we are currently drawing a plot!
	    	if plot_click:
	    		if plot_box.rect.collidepoint(event.pos):
	    			accept = True
	    			for i in range(len(points)):
	    				dist = event.pos[0] - points[i][0]
	    				# if its the same point as before
	    				if dist == 0:
	    					accept = False
	    					break
	    				if dist < 0:
	    					# if negative, and too close to old point
	    					if dist > -5:
	    						accept = False
	    						break
	    			if accept:
	    				points.append(event.pos)
	    				curr_player.points = points
	    				curr_player.points.sort(key=lambda s:s[0])
	    		# cover case of drawing outside plot box
	    		if not plot_box.rect.collidepoint(event.pos):
	    			plot_click = False
	    			pg.mouse.set_visible(True)

	    if event.type == pg.KEYDOWN:
	            # clear all points on plot option
	            if event.key == pg.K_c:
	            	points = []
	            	curr_player.points = []
	            	curr_player.points_count = 0

	    manager.process_events(event)
	    manager_plot.process_events(event)
	    manager_score.process_events(event)
	    manager_color.process_events(event)

	if new_ques:
		# hide main game boxes/labels before guesses all input
		range_win.hide()
		plot_box.hide()
		done_box.hide()
		flat_box.hide()
		norm_box.hide()
		next_box.hide()
		score_box.hide()
		label_score.hide()
		label_correct.hide()
		# show the question
		screen.blit(ques_base, (0,0))
		# blit the question, with text wrapping! (also question number)
		blit_wrap([y_ques_surfs, p_ques_surfs], WIDTH/20, 240, 480)
		screen.blit(ques_num, (930,20))

		# also blit the score table too?
		# screen.blit()

		# get the guessing player and say so
		curr_player,count = pick_player("guess")
		label_box.set_text("- "+curr_player.name+" guess a range like a,b -")
		
		# if all guesses now recorded
		if count == len(players):
			color_pick.kill()
			new_ques = False
			plotting = True
			ticks, values, min_guess, max_guess, win_p = get_ticks()
			# grab small version of question
			ques_size = len(ques.split())
			size = 24
			if ques_size >= 15:
				size = 18
				if ques_size >= 21:
					size = 15
				if ques_size >= 25:
					size = 13

			y_ques_surfs, p_ques_surfs, ques_num = get_ques_surfs(ques, ans, round_count, size)
			label_box.set_text("Now to plot!")
			plot_box.show()
			done_box.show()
			score_box.show()
			norm_box.show()
			flat_box.show()
			input_box.hide()

		# something was input!
		if response != "":
			try:
				# range form is a,b, so sep on comma
				curr_player.range = [float(response.split(",")[0]),float(response.split(",")[1])]
				# if only zeroes after decimal point, convert
				for i in range(len(curr_player.range)):
					if curr_player.range[i].is_integer():
						curr_player.range[i] = int(curr_player.range[i])

			except Exception as e:
				# throws out strings and such
				label_box.set_text("Enter a number/range!")
				delay = 2000
			# no doubled guesses
			for p in players:
				if p.range != None and p.name != curr_player.name:
					if p.range == curr_player.range:
						label_box.set_text("Exact range already guessed!")
						delay = 2000
						curr_player.range = None
			# finally, make sure > 0
			if curr_player.range != None and min(curr_player.range) < 0:
				label_box.set_text("Positives only!")
				delay = 2000
				curr_player.range = None

	# now  for each player, get points to plot!
	if not new_ques and plotting:
		# background, then manage now visible plot box
		screen.blit(plot_base, (0,0))
		manager_plot.update(time_delta)
		manager_plot.draw_ui(screen)

		# blit the question again, now as top line
		blit_wrap([p_ques_surfs], 10, 25,1000)
		# blit the ticks and the gueeses on the top / bottom
		draw_ticks(ticks, values)

		curr_player, count = pick_player("plot")
		# if not doing bell set up
		if not norm_pick and not flat_plot:
			label_box.set_text("- "+curr_player.name + " please plot your guess - ")
		
		# the player has pressed "BELL"
		if norm_pick:
			curr_player.bell = True
			if mean == None:
				label_box.set_text("Pick a mean")
				if response != "":
					# check that is a float, in the range
					try:
						mean = float(response)
					except:
						label_box.set_text("Enter a number!")
						delay = 2000
					# if we pass the above...  
					if mean != None:
						if mean < min_guess or mean > max_guess:
							label_box.set_text("pick within guess range!")
							mean = None
							delay = 2000
					response = ""

			if mean != None and std_dev == None:
				label_box.set_text("Pick a std dev")
				if response != "":
					# check st dev here, float and not too small / large
					try:
						std_dev = float(response)
					except:
						label_box.set_text("Enter a number!")
						delay = 2000
					if std_dev != None:
						if std_dev < 1:
							std_dev = .5 # small enough so essentially 0

			if mean != None and std_dev != None:
				input_box.hide()
				# now use these to construct points
				curr_player.points = construct_norm(mean, std_dev)
				# set p to done, and set delay!
				norm_pick = False
				curr_player.done = True
				delay = 4000
				label_box.set_text("Bell plotted")
				
				# also draw lines for curve, for ~ confidence ~
				# boost appearance, otherwise looks small
				line_points = copy.deepcopy(curr_player.points)   # need copy to preserve score calc, bars, etc

#				EXPERIMENTAL BELL APPEARANCE BOOSTER...
#				for point in line_points:
#					zero_dist = (plot_box.rect.h+plot_box.rect.y-8)-point[1]
#					scale = min(.26, (math.exp(zero_dist/5) - 1) )
#					if scale != 0:
#						if point[1]/scale > plot_box.rect.y:
#							print("zero_dist, scale: ", round(zero_dist,5), (1+scale))
#							print("updating ",point[1]," to ", point[1]/(1+scale))
#							point[1] = point[1]/(1+scale)
				
				# make sure we dont plot on top of box borders, adjust purely for visuals
				if mean < min_guess + 3:
					for point in line_points:
						point[0] = point[0] + 5
				if mean > max_guess - 3:
					for point in line_points:
						point[0] = point[0] - 5

				for i in range(len(line_points)):
					curr_point = line_points[i]
					# only draw to next if it exists!
					if i != len(line_points) - 1:
						next_point = line_points[i+1]
						pg.draw.line(screen, BLACK, curr_point, next_point, 3)
				
				# finally, automaticaly socre the player, since theyre done
				score, avg = guess_integral(curr_player.points, min_guess, max_guess)
				print("name, score, avg: ", curr_player.name, score, avg)
				curr_player.score.append(100*score)

		# the player has pressed "FLAT"
		if flat_plot:
			xs = np.linspace(plot_box.rect.x, plot_box.rect.x + plot_box.rect.w, 100)
			for i in range(len(xs)):
				curr_player.points.append([xs[i], plot_box.rect.y + plot_box.rect.h/2])
			# only need to draw one line!
			pg.draw.line(screen, BLACK, [plot_box.rect.x, plot_box.rect.y + plot_box.rect.h/2], 
						[plot_box.rect.x+plot_box.rect.w,plot_box.rect.y + plot_box.rect.h/2], 3)
			
			flat_plot = False
			curr_player.done = True
			delay = 4000
			label_box.set_text("Flat plotted")
			# finally, automatically score the player, since theyre done
			score, avg = guess_integral(curr_player.points, min_guess, max_guess)
			print("name, score, avg: ", curr_player.name, score, avg)
			curr_player.score.append(100*score)

		# below, blit special cursor when drawing starts
		if plot_click:
			pg.draw.circle(screen, PURPLE, (pg.mouse.get_pos()[0], pg.mouse.get_pos()[1]),15, width=2)
		
		# blit current points on plot
		if count != len(players):
			# dont do points if we did lines!
			if not(mean != None and std_dev != None):
				for i in range(len(curr_player.points)):
					curr_point = curr_player.points[i]
					pg.draw.circle(screen, BLACK, curr_point, 2)
			else:
				# now reset, since lines drawn
				mean = None
				std_dev = None

		# check if all players done plotting
		if count == len(players):
			# now we're done plotting, should have scores
			# but add to scores who won the range question
			if len(win_p) > 0:
				for p in win_p:
					print("someone won!")
					p.score[-1]  =  p.score[-1] + range_boost
					if win_names  == "":
						win_names = win_names + p.name
					else:
						win_names = win_names + "," + p.name
				range_win.set_text(win_names+" has the best range(s)! +"+str(range_boost))
			plotting = False
			top_p, doubles = top_score(players)
			name_str = top_p.name
			for name in doubles:
				if len(name_str) < 10:  # if too many doubles, just show some
					name_str = name_str+", "+name
			# show winner, their score, ans; need new labels for this (to be removed subsequently!)
			label_box.set_text("Best: "+name_str)
			label_score.set_text("Score: "+str(round(top_p.score[-1],2)))
			label_correct.set_text("Correct Answer: "+str(ans))
			label_score.show()
			label_correct.show()

			screen.blit(score_descr,[plot_box.rect.x+30, plot_box.rect.y+30])
			# blit the score surf and the animation
			# update screen first to show background
			done_box.hide()
			score_box.hide()
			norm_box.hide()
			flat_box.hide()
			manager.update(time_delta)
			manager.draw_ui(screen)
			manager_score.update(time_delta)
			manager_score.draw_ui(screen)
			pg.display.update()
			score_animate(top_p,min_guess, max_guess, ans)
			pg.time.delay(100)
			# here place win message... after animate,  before resetting?
			# or as well, while waiting for next
			if len(win_p) > 0:
				range_win.show()
			done_box.show()
			score_box.show()
			norm_box.show()
			flat_box.show()
			round_count = round_count + 1
			# show box to check whether we do next round!
			next_box.show()
			
	manager.update(time_delta)
	manager.draw_ui(screen)
	manager_score.update(time_delta)
	manager_score.draw_ui(screen)
	manager_color.update(time_delta)
	manager_color.draw_ui(screen)

	# if we're done, show scores last time
	if round_count > num_rounds:
		score_check = True
	# show score image, super long delay if end of game
	if score_check:
		show_score(table, players)
		score_check = False
		if round_count > num_rounds:
			delay = 5000
			is_running = False
		else:
			delay = 3000

	pg.display.update()
	pg.time.delay(delay)
	response = ""
# the default is the observational version (set condition to s to get the strategic version)
# the default is the dots version (set task to s to get the squircles version)

# IMPORT EXTERNAL PACKAGES
from __future__ import absolute_import, division
import random
import os
import math
import numpy as np  # whole numpy lib is available, prepend 'np.'
from psychopy import gui, visual, core, data, event, logging, misc, clock
from psychopy.hardware import keyboard

# SET UP EEG TRIGGERS
from daq import (setup_triggers, send_trigger_fast,
                 send_trigger_slow, send_trigger)
from triggers import triggers

task = setup_triggers()

print('Reminder: Press Q to quit.')

# SESSION INFORMATION
# Pop up asking for participant number, session, age, and gender
expInfo = {'participant nr': '', 'session (1/2)': '', 'condition (s/ns)': '', 'task (s/d)': '', 'age': '',
           'gender (f/m/o)': ''}
expName = 'Confidence Matching EEG'
dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
if not dlg.OK:
    core.quit()  # pressed cancel

# SET EXPERIMENT VARIABLES
# variables in gv are just fixed
gv = dict(
    n_practice_trials=5,  # MAKE TRIAL COUNT 100 HERE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    n_confidence_practice_trials=5,  # make trial count 5 here
    n_blocks_per_partner=5,  # make block count 5 here
    n_trials_per_block=5,  # MAKE TRIAL COUNT 25 HERE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    dot_period=0.3,
    squircle_period=0.5,
    fixation_period=1,
    wait_period=0.5,  # wait time after response before next fixation cross
    dot_difference_limits=[1, 100],  # minimum and maximum dots difference
    squircles_n_circles=8,  # number of circles for the squircles stimuli
    squircles_color_sd=0.1,  # colour variance for the squircles stimuli
    staircase_breaks=[5, 10],
    # number of trials after which staircasing values change (takes only two values at the moment)
    staircase_step_sizes=[0.4, 0.2, 0.1],
    # staircase step sizes in log space (takes only 3 values at the moment in accordance with the 2 staircase_breaks values)  
)

# variables in info will be saved as participant data
info = dict(
    expName=expName,
    curec_ID='R67369/RE001',
    session=expInfo['session (1/2)'],
    condition=expInfo['condition (s/ns)'],
    task=expInfo['task (s/d)'],
    date=data.getDateStr(),
    end_date=None,

    participant=expInfo['participant nr'],
    age=expInfo['age'],
    gender=expInfo['gender (f/m/o)'],

    confidence_slider_on=None,
    staircasing_on=None,
    partner=None,
    partner_colour=None,

    trial_count=0,
    block_count=0,
    block_with_partner=0,
    trial_in_block=0,
    dot_count_low=None,
    dot_count_high=None,
    stair_value=None,
    correct_response=None,
    participant_response=None,
    participant_correct=None,
    participant_confidence=None,
    partner_response=None,
    partner_correct=None,
    partner_confidence=None,
    joint_correct=None,
    participant_chosen=None,
    partner_chosen=None,

    trial_score=None,
    final_score=None,
    reward=None,
    p1_likeability=None,
    p1_confidence=None,
    p1_accuracy=None,
    p1_team_work=None,
    p2_likeability=None,
    p2_confidence=None,
    p2_accuracy=None,
    p2_team_work=None,

    # variables for staircasing
    next_dot_count_low=200,  # fixed low dot count
    next_stair_value=4.2,
    # initial staircasing value is 4.2 (as in Rouault, M., Seow, T. Gillan, C. M., & Fleming, S. M. (2018))
    next_dot_count_high=200 + int(round((math.e ** 4.2), 0)),
    next_squircle_difference=0.25,  # initial squircle colour difference
    previous_trial_correct=False
)

# LOGGING
log_vars = list(info.keys())
if not os.path.exists('data'):
    os.mkdir('data')
filename = os.path.join('data', '%s_%s' % (info['participant'], info['date']))
## Save a log file for detail verbose info
logFile = logging.LogFile(filename + '.log', level=logging.EXP)
logging.console.setLevel(0)  # this outputs to the screen, not a file

datafile = open(filename + '.csv', 'w')
datafile.write(','.join(log_vars) + '\n')
datafile.flush()

# SET UP WINDOW
win = visual.Window(
    gammaErrorPolicy='ignore',
    fullscr=True, screen=1,  # PROBABLY MAKE SCREEN = 1 HERE
    allowGUI=True, allowStencil=False,
    monitor='testMonitor', color='black',
    blendMode='avg', useFBO=True, units='pix')  # pix is ca 1200 by 1000

# INSTRUCTIONS
th = 35

button = visual.Rect(
    win=win,
    units="pix",
    width=160,
    height=60,
    pos=(0, -400),
    fillColor=[-1, 1, -1],
    lineColor=[-1, .8, -1]
)
button_txt = visual.TextStim(win=win, text='NEXT', height=th, pos=button.pos, color=[-1, -1, -1], bold=True)

choice_txt = visual.TextStim(win=win, text='Which box contained more dots?', height=30, pos=[0, -80], color='white')

confidence_txt = visual.TextStim(win=win, text='Indicate your confidence with the slider below', height=30,
                                 pos=[0, -80], color='white')

welcome_txt = visual.TextStim(win=win, text='Welcome to this experiment!', height=70, pos=[0, 0], color='white')

welcome2_txt = visual.TextStim(win=win, text='In this experiment, you will be playing a game with dots!', height=50,
                               pos=[0, 0], color='white')

welcome2_squircles_txt = visual.TextStim(win=win, text='In this experiment, you will be playing a game of comparing colours!', height=50,
                               pos=[0, 0], color='white')

practice_instructions_txt = visual.TextStim(win=win,
                                            text='During this game, you will see two boxes containing dots briefly '
                                                 'flash on either side of the centre of the screen (marked with a "+" sign). '
                                                 'Your task is to decide whether the left or right box contains more dots. '
                                                 'If you think the left box contained more dots, you respond with a '
                                                 'left mouse-click. If you think the right box contained more dots, you '
                                                 'respond with a right mouse-click. The task will start off quite '
                                                 'easy but will become harder as you progress. \n \n Press the "next" '
                                                 'button to start the game. The first phase of the game can take up to 8 '
                                                 'minutes. You should reach a stable performance level to continue to the '
                                                 'next phase.', height=th, pos=[0, 0], wrapWidth=1000, color='white')

practice_instructions_squircles_txt = visual.TextStim(win=win,
                                            text='During this game, you will see 2 circles of coloured patches that will'
                                                 ' briefly flash on either side of the centre of the screen (marked '
                                                 'with a "+" sign). The patches will have colours ranging from red to '
                                                 'blue. Your task is to decide which of the two circles of coloured '
                                                 'patches is more red on average, compared to the other one. If you '
                                                 'think the left circle was more red , you respond with a left '
                                                 'mouse-click. If you think the right circle was more red , you respond '
                                                 'with a right mouse-click. The task will start off quite easy but will '
                                                 'become harder as you progress \n \n Press the "next" button to start '
                                                 'the game. The first phase of the game can take up to 8 '
                                                 'minutes. You should reach a stable performance level to continue to the '
                                                 'next phase.', height=th, pos=[0, 0], wrapWidth=1000, color='white')

continue_txt = visual.TextStim(win=win, text='Great, you are now ready to continue!', height=60, pos=[0, 0],
                               wrapWidth=1000,
                               color='white')

halfway_txt = visual.TextStim(win=win,
                              text='Great! You are half-way through. \n \n For the second half you will be paired with a different partner.',
                              height=60, pos=[0, 0], wrapWidth=1000,
                              color='white')

confidence_instructions_txt = visual.TextStim(win=win,
                                              text='From now on, you will indicate your confidence in your decisions. \n \n'
                                                   'After responding with a left or right click, you will now '
                                                   'indicate your confidence in the decision on a sliding '
                                                   'scale. Hover over the slider bar to change the slider '
                                                   'position - towards the middle f you aren\'t sure of your '
                                                   'answer, and towards the left/right side if you\'re confident '
                                                   'that the respective side is the correct answer - then click'
                                                   ' on the slider bar to register your confidence rating. '
                                                   '\n \n Press the "next" button to do a few trials with the confidence '
                                                   'slider.', height=th, pos=[0, 0], wrapWidth=1000,
                                              color='white')

confidence_feedback_instructions_txt = visual.TextStim(win=win,
                                                       text='From now on, you will indicate your confidence in '
                                                            'your decisions and get feedback if your choice was correct or incorrect. \n \n'
                                                            'After responding with a left or right click, you '
                                                            'will now indicate your confidence in the decision '
                                                            'on a sliding scale. Hover over the slider bar to '
                                                            'change the slider position - towards the middle '
                                                            'if you aren\'t sure of your answer, and towards '
                                                            'the left/right side if you\'re confident that the '
                                                            'respective side is the correct answer - then '
                                                            'click on the slider bar to register your confidence '
                                                            'rating. After you respond, you will get feedback '
                                                            'about whether the side you picked was correct or '
                                                            'incorrect \n \n '
                                                            'Press the "next" button to do a few trials with '
                                                            'the confidence slider.', height=th, pos=[0, 0],
                                                       wrapWidth=1000,
                                                       color='white')

partner1_observe_instructions_txt = visual.TextStim(win=win,
                                                    text='For the rest of the experiment, you\'ll be doing the task you '
                                                         'just practiced. However, from now on you will see the response'
                                                         ' of another past participant for the stimulus. Your '
                                                         'partner did about as well as you did in the practice trials. \n \n'
                                                         'You will earn points depending on whether your response is '
                                                         'correct and how accurate your confidence judgment was. At the '
                                                         'end of the game, we will take all trials where you indicated, '
                                                         'for example, a confidence of 70-80%% and check if in fact '
                                                         '70-80%% of those trials were correct. The closer your confidence '
                                                         'judgements align with your actual accuracy, the higher your '
                                                         'cash bonus (up to £5) will be at the end of the experiment.'
                                                         '\n \nThere will be %i blocks of %i trials, which should take '
                                                         'approximately 30 minutes to complete altogether. Press "next" '
                                                         'to continue to the first block.'
                                                         % (
                                                             gv['n_blocks_per_partner'] * 2,
                                                             gv['n_trials_per_block']),
                                                    height=th, pos=[0, 0],
                                                    wrapWidth=1000, color='white')

partner2_observe_instructions_txt = visual.TextStim(win=win,
                                                    text='Based on your responses, we will select another participant '
                                                         'who did about as well as you did on the task. Different '
                                                         'partner, same rules: After responding with a left or right '
                                                         'click and indicating your confidence on the slider, you will '
                                                         'see the your partner\'s response for the same stimulus. \n \n You '
                                                         'will earn points depending on whether your response is correct'
                                                         ' and how accurate your confidence judgment was. At the end of '
                                                         'the game, we will take all trials where you indicated, for '
                                                         'example, a confidence of 70-80%% and check if in fact 70-80%% '
                                                         'of those trials were correct. The closer your confidence '
                                                         'judgements align with your actual accuracy, the higher your '
                                                         'cash bonus (up to £5) will be at the end of the experiment. '
                                                         '\n \nPress the "next" button to do %i more blocks of the dot task.'
                                                         % (gv['n_blocks_per_partner']), height=th, pos=[0, 0],
                                                    wrapWidth=1000, color='white')

partner1_strategic_instructions_txt = visual.TextStim(win=win,
                                                      text='For the rest of the experiment, you\'ll be doing the task you '
                                                           'just practiced. However, from now on you will see the response '
                                                           'of another past participant for the same stimulus. Your partner '
                                                           'did about as well as you did in the practice trials. The '
                                                           'decision that is reported with higher confidence will be selected '
                                                           'as your joint decision. \n \nCritically, your feedback and cash bonus '
                                                           'will be based on the joint decision. Every correct joint decision '
                                                           'will earn you 2p. Therefore, if you are sure you got it right, '
                                                           'report high confidence such that your decision counts. '
                                                           'However, if you are not very sure, it might be best to report '
                                                           'low confidence and thus let your partner\'s decision be chosen.'
                                                           '\n \nThere will be %i blocks of %i trials, which should take '
                                                           'approximately 30 minutes to complete altogether. Press "next" '
                                                           'to continue to the first block.'
                                                           % (gv['n_blocks_per_partner'] * 2,
                                                              gv['n_trials_per_block']),
                                                      height=th, pos=[0, 0],
                                                      wrapWidth=1000, color='white')

partner2_strategic_instructions_txt = visual.TextStim(win=win,
                                                      text='Based on your responses, we will select another participant '
                                                           'who did about as well as you did on the task. Different '
                                                           'partner, same rules: After responding with a left or right '
                                                           'click and indicating your confidence on the slider, you will '
                                                           'see the your partner\'s response for the same stimulus. '
                                                           'Your partner did about as well as you did in the practice trials. '
                                                           'The decision that is reported with higher confidence will be selected '
                                                           'as your joint decision. \n \n Critically, your feedback and cash bonus '
                                                           'will be based on the joint decision. Therefore, if you are sure '
                                                           'you got it right, report high confidence such that your decision '
                                                           'counts. However, if you are not very sure, it might be best to '
                                                           'report low confidence and thus let your partner\'s decision be chosen. '
                                                           '\n \nPress the "next" button to do %i more blocks of the dot task.'
                                                           % (gv['n_blocks_per_partner']), height=th, pos=[0, 0],
                                                      wrapWidth=1000, color='white')

thanks_txt = visual.TextStim(win=win, text='Thank you for completing the study!', height=70, pos=[0, 0], color='white')

qtxt1 = visual.TextStim(win=win, text='What did you think about your partner\n .', height=55, pos=[0, 0], color='white')
qtxt2 = visual.TextStim(win=win, text='What did you think about your partner\n . .', height=55, pos=[0, 0],
                        color='white')
qtxt3 = visual.TextStim(win=win, text='What did you think about your partner\n . . .', height=55, pos=[0, 0],
                        color='white')
qtxt4 = visual.TextStim(win=win, text='What did you think about your partner\n . . . ?', height=55, pos=[0, 0],
                        color='white')


######################################################################################################################################################
#############################################################    FUNCTIONS     #######################################################################
######################################################################################################################################################

# HELPER FUNCTIONS

# 20x20 matrix with 0s (no dots) and 1s (dots) in random locations. number of 1s = number of dots
def dots_matrix(shape, ones):
    o = np.ones(ones, dtype=int)
    z = np.zeros(np.product(shape) - ones, dtype=int)
    board = np.concatenate([o, z])
    np.random.shuffle(board)
    return board.reshape(shape)


# generate colour samples for the squircles
def generate_colour_samples(colour_mean, colour_sd, n_circles):
    # create a list of n numbers between a and b
    def random_list(n, a, b):
        list = []
        for i in range(n):
            list.append(random.random() * (b - a) + a)
        return list

    # create a list of random numbers between 1 and 10
    list = random_list(n_circles, 1, 10)

    # compute mean, sd and the interval range [min, max] of list
    def descriptives_list(list):
        leng = len(list)
        a = float('inf')
        b = float('-inf')
        sum = 0
        for i in range(leng):
            sum += float(list[i])
            a = min(a, list[i])
            b = max(b, list[i])
        mean = sum / leng
        sum = 0
        for i in range(leng):
            sum += (list[i] - mean) * (list[i] - mean)
        sd = math.sqrt(sum / (leng - 1))
        return {
            'mean': mean,
            'sd': sd,
            'range': [a, b]
        }

    # transform list to have an exact mean and sd
    def force_descriptives(list, mean, sd):
        old_descriptives = descriptives_list(list)
        old_mean = old_descriptives['mean']
        old_sd = old_descriptives['sd']
        new_list = []
        leng = len(list)
        for i in range(leng):
            new_list.append(sd * (list[i] - old_mean) / old_sd + mean)
        return new_list

    new_list = force_descriptives(list, colour_mean, colour_sd)
    print(descriptives_list(new_list))
    random.shuffle(new_list)
    return new_list


# turn colour sample values into RGB values from blue to red
def generate_rgb_values(value):
    colour_value = [value*255, 0, (1 - value) * 255]
    return colour_value


# add this in to allow exiting the experiment when we are in full screen mode
def exit_q(key_list=None):
    # this just checks if anything has been pressed - it doesn't wait
    if key_list is None:
        key_list = ['q']
    keys = event.getKeys(keyList=key_list)
    res = len(keys) > 0
    if res:
        if 'q' in keys:
            win.close()
            core.quit()
    return res


# returns 0 if incorrect and certain, and 1 if correct and certain
def reverse_brier_score(confidence, outcome):
    if outcome:
        o = 0
    else:
        o = 1
    f = confidence / 100
    return (f - o) ** 2


# function for sampling from normal distribution with given min, max, and skew
# standard Normal variate using Box-Muller transform
def randn_bm(min, max, skew):
    u = 0
    v = 0
    while u == 0:
        u = random.random()
    while v == 0:
        v = random.random()
    num = math.sqrt(-2.0 * math.log(u)) * math.cos(2.0 * math.pi * v)
    num = num / 10.0 + 0.5
    if num > 1 or num < 0:
        num = randn_bm(min, max, skew)
    num = math.pow(num, skew)
    num *= max - min
    num += min
    return num


# loading partner
def load_partner():
    visual.TextStim(win=win, text='selecting your partner \n \n .', height=55, pos=[0, 0], color='white').draw()
    core.wait(0.7)
    win.flip()
    visual.TextStim(win=win, text='selecting your partner \n \n . .', height=55, pos=[0, 0], color='white').draw()
    core.wait(0.7)
    win.flip()
    visual.TextStim(win=win, text='selecting your partner \n \n . . .', height=55, pos=[0, 0], color='white').draw()
    core.wait(0.7)
    win.flip()
    visual.TextStim(win=win, text='checking for similar performance levels \n \n .', height=55, pos=[0, 0],
                    color='white').draw()
    core.wait(0.7)
    win.flip()
    visual.TextStim(win=win, text='checking for similar performance levels \n \n . .', height=55, pos=[0, 0],
                    color='white').draw()
    core.wait(0.7)
    win.flip()
    visual.TextStim(win=win, text='checking for similar performance levels \n \n . . .', height=55, pos=[0, 0],
                    color='white').draw()
    core.wait(0.7)
    win.flip()
    visual.TextStim(win=win, text='loading the game \n \n .', height=55, pos=[0, 0], color='white').draw()
    core.wait(0.7)
    win.flip()
    visual.TextStim(win=win, text='loading the game \n \n . .', height=55, pos=[0, 0], color='white').draw()
    core.wait(0.7)
    win.flip()
    visual.TextStim(win=win, text='loading the game \n \n . . .', height=55, pos=[0, 0], color='white').draw()
    core.wait(0.7)
    win.flip()


# questionnaire items
def questionnaire_item(item_text='item text', tick1='\n1\n not at all', tick10='\n10\n very much'):
    rating = visual.RatingScale(win=win, pos=(0, -100), low=1, high=10, stretch=1.4,
                                marker='circle', markerColor=(0, 0.8, 0.8), showAccept=False, singleClick=True,
                                tickMarks=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                                labels=[tick1, '2', '3', '4', '5', '6', '7', '8', '9', tick10])
    item = visual.TextStim(win, text=item_text, pos=(0, 150), height=th + 10, color='white')
    while rating.noResponse:
        item.draw()
        rating.draw()
        win.flip()
    curr_rating = rating.getRating()
    win.flip()
    # return results
    return curr_rating


# DRAW DOTS FUNCTION
def do_trial(win, mouse, gv, info):
    # STIMULI
    fixation = visual.ShapeStim(
        win,
        vertices=((0, -2), (0, 2), (0, 0), (-2, 0), (2, 0)),
        lineWidth=50,
        pos=(0, 100),
        closeShape=False,
        lineColor="white"
    )

    circle_radius_pix = [1, 1]
    dot = visual.Circle(
        win=win,
        radius=circle_radius_pix,
        units="pix",
        edges=300,
        fillColor="white",
    )

    rect_right = visual.Rect(
        win=win,
        units="pix",
        width=20 * 12,
        height=20 * 12,
        pos=(210, 105),  # check which variables should correspond to the correct position
        fillColor=None,
        lineColor="white"
    )

    rect_left = visual.Rect(
        win=win,
        units="pix",
        width=20 * 12,
        height=20 * 12,
        pos=(-210, 105),  # check which variables should correspond to the correct position
        fillColor=None,
        lineColor="white"
    )

    slider_marker = visual.ShapeStim(
        win=win,
        vertices=((0, -25), (0, 25)),
        lineWidth=8,
        pos=(0, 0),
        closeShape=False,
        lineColor=(0, 0.8, 0.8),
    )

    partner_marker = visual.ShapeStim(
        win=win,
        vertices=((0, -25), (0, 25)),
        lineWidth=8,
        pos=(0, 0),
        closeShape=False,
        lineColor=info['partner_colour'],
    )

    higher_conf_box = visual.Rect(
        win=win,
        units="pix",
        width=20,
        height=60,
        pos=(0, 0),
        lineWidth=4,
        fillColor=None,
        lineColor="white"
    )

    slider_cover = visual.Rect(
        win=win,
        units="pix",
        width=400,
        height=60,
        pos=(0, 0),
        opacity=0.6,
        fillColor='white',
        lineColor='white'
    )

    # HIDE THE MOUSE
    win.mouseVisible = False

    # DRAW THE FIXATION CROSS
    fixation.draw()
    win.flip()
    exit_q()
    core.wait(gv['fixation_period'])

    # determine the correct response and draw the left/right stimulus correspondingly
    response_options = ["left", "right"]
    correct_response = random.choice(response_options)
    info['correct_response'] = correct_response

    # SQUIRCLES TASK
    if info['task'] == 's':
        # CREATE AND DRAW THE SQUIRCLE STIMULI
        difference = info['next_squircle_difference']

        # determine squircle parameters
        colour_mean_low = round(random.uniform(0, (0.9 - difference)),
                                2)  # 0.9 instead of 1.0 because of the variance around the mean
        colour_mean_high = round(colour_mean_low + difference,
                                 2)  # this will be max. .09 (i.e. even with sd won't go above 1)

        print(colour_mean_low)
        print(colour_mean_high)
        print(difference)

        if correct_response == "left":
            left_squircle_colours = generate_colour_samples(colour_mean_high, gv['squircles_color_sd'], gv[
                'squircles_n_circles'])  # one number for each circle with defined mean and sd for the numbers
            right_squircle_colours = generate_colour_samples(colour_mean_low, float(gv['squircles_color_sd']),
                                                             int(gv['squircles_n_circles']))
            print(right_squircle_colours)
        else:
            left_squircle_colours = generate_colour_samples(colour_mean_low, gv['squircles_color_sd'],
                                                            gv['squircles_n_circles'])
            right_squircle_colours = generate_colour_samples(colour_mean_high, gv['squircles_color_sd'],
                                                             gv['squircles_n_circles'])

        circle = visual.Circle(
            win=win,
            units="pix",
            colorSpace='rgb255',
            fillColor=(255, 255, 255),
            lineColor=(0, 0, 0),
            edges=128,
            radius=22
        )
        f = 360 / gv['squircles_n_circles']
        thetas = [x * f for x in range(360)]

        # right stimulus
        for i in range(gv['squircles_n_circles']):
            [pos_x, pos_y] = misc.pol2cart(
                thetas[i],
                80
            )
            circle.pos = [pos_x + rect_right.pos[0], pos_y + rect_right.pos[1]]
            fill_colour = generate_rgb_values(right_squircle_colours[i])
            circle.fillColor = (fill_colour[0], fill_colour[1], fill_colour[2])
            circle.draw()

        # left stimulus
        for i in range(gv['squircles_n_circles']):
            [pos_x, pos_y] = misc.pol2cart(
                thetas[i],
                75
            )
            circle.pos = [pos_x + rect_left.pos[0], pos_y + rect_left.pos[1]]
            fill_colour = generate_rgb_values(left_squircle_colours[i])
            circle.fillColor = (fill_colour[0], fill_colour[1], fill_colour[2])
            circle.draw()

        # show squircles for stimulus period
        win.flip()
        exit_q()
        core.wait(gv['squircle_period'])


    # DOTS TASK
    else:
        # CREATE AND DRAW THE DOTS GRID
        dot_count_high = info['next_dot_count_high']
        dot_count_low = info['next_dot_count_low']
        if correct_response == "left":
            dots_matrix_left = dots_matrix([20, 20], dot_count_high)
            dots_matrix_right = dots_matrix([20, 20], dot_count_low)
        else:
            dots_matrix_right = dots_matrix([20, 20], dot_count_high)
            dots_matrix_left = dots_matrix([20, 20], dot_count_low)

        info['dot_count_low'] = dot_count_low
        info['dot_count_high'] = dot_count_high

        # draw the dots grids based on the matrices
        offsets = range(0, 19, 1)
        row_count = 0

        # right stimulus
        for y_offset in offsets:
            for x_offset in offsets:
                if dots_matrix_right[y_offset, x_offset] == 1:
                    for stimulus in [dot]:
                        stimulus.pos = [x_offset * 12 + 100, y_offset * 12]
                        stimulus.draw()
            row_count = row_count + 1

        # left stimulus
        for y_offset in offsets:
            for x_offset in offsets:
                if dots_matrix_left[y_offset, x_offset] == 1:
                    for stimulus in [dot]:
                        stimulus.pos = [x_offset * (-12) - 100, y_offset * 12]
                        stimulus.draw()
            row_count = row_count + 1

        # show dots for stimulus period
        rect_right.draw()
        rect_left.draw()
        win.flip()
        exit_q()
        core.wait(gv['dot_period'])

    # remove stimulus but keep the rectangles
    rect_right.draw()
    rect_left.draw()
    choice_txt.draw()
    win.flip()
    exit_q()

    # PARTICIPANT CHOICE LEFT/RIGHT
    choice = None
    # wait for mouse click
    buttons = mouse.getPressed()
    while buttons == [0, 0, 0]:
        buttons = mouse.getPressed()
        # left click
        if buttons == [1, 0, 0]:
            # save participant choice
            choice = "left"
            rect_left.lineColor = (0, 0.8, 0.8)
            rect_left.lineWidth = 6
            slider_cover.pos = (200, -300)
        # right click
        if buttons == [0, 0, 1]:
            # save participant choice
            choice = "right"
            rect_right.lineColor = (0, 0.8, 0.8)
            rect_right.lineWidth = 6
            slider_cover.pos = (-200, -300)
    info['participant_response'] = choice

    if choice == correct_response:
        participant_correct = True
    else:
        participant_correct = False
    info['participant_correct'] = participant_correct

    rect_right.draw()
    rect_left.draw()
    win.flip()
    exit_q()

    # STAIRCASING
    # two-down one-up staircase procedure with equal step-sizes for steps up and down
    stair_value = info['next_stair_value']
    info['stair_value'] = stair_value

    if info['staircasing_on']:

        if not participant_correct:  # incorrect, make it easier
            if info['trial_in_block'] <= gv['staircase_breaks'][0]:
                stair_value = stair_value + gv['staircase_step_sizes'][
                    0]  # changing by + 0.4 in log space for the first 5 trials
            elif gv['staircase_breaks'][0] < info['trial_in_block'] <= gv['staircase_breaks'][1]:
                stair_value = stair_value + gv['staircase_step_sizes'][
                    1]  # changing by + 0.2 in log space for the next 5 trials
            else:
                stair_value = stair_value + gv['staircase_step_sizes'][
                    2]  # changing by + 0.1 in log space for the rest of the task

        elif participant_correct & info['previous_trial_correct']:  # correct two times in a row, make it harder
            if info['trial_in_block'] <= gv['staircase_breaks'][0]:
                stair_value = stair_value - gv['staircase_step_sizes'][
                    0]  # changing by - 0.4 in log space for the first 5 trials
            elif gv['staircase_breaks'][0] < info['trial_in_block'] <= gv['staircase_breaks'][1]:
                stair_value = stair_value - gv['staircase_step_sizes'][
                    1]  # changing by - 0.2 in log space for the next 5 trials
            else:
                stair_value = stair_value - gv['staircase_step_sizes'][
                    2]  # changing by- 0.1 in log space for the rest of the task

        else:  # correct only once in a row, keep it the same
            stair_value = stair_value

    info['next_stair_value'] = stair_value
    info['previous_trial_correct'] = participant_correct  # only update this variable after we have used it!

    # SQUIRCLES TASK
    if info['task'] == 's':
        info['next_squircle_difference'] = int(round((math.e ** stair_value), 0)) / 1000

    # DOTS TASK
    else:
        next_dot_count_low = info['dot_count_low']  # stays the same
        next_dot_count_high = next_dot_count_low + int(round((math.e ** stair_value), 0))
        # limits for dots difference at 1 and 100
        if next_dot_count_high < (next_dot_count_low + gv['dot_difference_limits'][0]):
            next_dot_count_high = next_dot_count_low + gv['dot_difference_limits'][0]
        elif next_dot_count_high > (next_dot_count_low + gv['dot_difference_limits'][1]):
            next_dot_count_high = next_dot_count_low + gv['dot_difference_limits'][1]

        info['next_dot_count_low'] = next_dot_count_low
        info['next_dot_count_high'] = next_dot_count_high


    # CONFIDENCE SLIDER
    if info['confidence_slider_on']:
        # ENABLE MOUSE
        win.mouseVisible = True

        slider = visual.Slider(win, ticks=(1, 2, 3, 4, 5, 6, 7),
                               labels=["certainly\nLEFT", "probably\nLEFT", "maybe\nLEFT", "",
                                       "maybe\nRIGHT", "probably\nRIGHT", "certainly\nRIGHT"],
                               pos=(0, -300),
                               size=(800, 50), units="pix", flip=True, style='slider', granularity=0, labelHeight=20)
        slider.tickLines.sizes = (1, 30)

        slider.draw()
        slider_cover.draw()
        rect_left.draw()
        rect_right.draw()
        confidence_txt.draw()
        win.flip()
        exit_q()

        # ANIMATE THE CONFIDENCE SLIDER MARKER
        slider_rating_txt = visual.TextStim(win=win, text='%', height=18,
                                            pos=(0, 0), color='white')
        while not slider.rating:
            # restrict slider marker to the range of slider
            if mouse.getPos()[0] > (slider.size[0] / 2):
                slider_marker.pos = ((slider.size[0] / 2), slider.pos[1])
                slider_rating_txt.pos = ((slider.size[0] / 2), slider.pos[1] - 40)
            elif mouse.getPos()[0] < -(slider.size[0] / 2):
                slider_marker.pos = (-(slider.size[0] / 2), slider.pos[1])
                slider_rating_txt.pos = (-(slider.size[0] / 2), slider.pos[1] - 40)
            else:
                slider_marker.pos = (mouse.getPos()[0], slider.pos[1])
                slider_rating_txt.pos = (mouse.getPos()[0], slider.pos[1] - 40)

            if choice == 'right':
                participant_confidence = 100 - (slider.size[0] / 2 - slider_marker.pos[0]) / slider.size[0] * 100
            else:
                participant_confidence = (slider.size[0] / 2 - slider_marker.pos[0]) / slider.size[0] * 100

            # don't allow clicks on confidence slider on the side that was not chosen initially
            if participant_confidence < 50:
                slider.readOnly = True
            else:
                slider.readOnly = False

            participant_confidence = round(participant_confidence, 2)
            slider_rating_txt.text = ' %i %%' % round(participant_confidence, 0)

            slider.draw()
            slider_cover.draw()
            rect_left.draw()
            rect_right.draw()
            slider_marker.draw()
            slider_rating_txt.draw()
            confidence_txt.draw()
            win.flip()
            exit_q()

        info['participant_confidence'] = participant_confidence
        print(participant_confidence)

        # PARTNER CHOICE AND CONFIDENCE RATING
        if info['partner'] is not None:
            info['trial_score'] = reverse_brier_score(participant_confidence, participant_correct)
            partner_confidence = 999
            while partner_confidence > 100:
                # p correct from normal distribution between 0.6 and 1 (mean 0.8)
                pCorrect = randn_bm(0.6, 1, 1)

                # pick correct response with p correct
                random_v = random.random()
                if random_v < pCorrect:
                    partner_choice = correct_response
                    info['partner_correct'] = True
                else:
                    if correct_response == 'left':
                        partner_choice = 'right'
                    else:
                        partner_choice = 'left'
                    info['partner_correct'] = False

                info['partner_response'] = partner_choice

                # given p(correct), determine partner's confidence according to c + (x - .5) * s + e
                # c is a constant do differentiate over- and under-confident partners (overconfident set to 0.6, underconfident set to 0.1)
                # s is the slope which I set to 0.8
                # e is random noise which I will sample from a normal distribution with m=0 and sd=.05
                error = randn_bm(-0.05 * 3, 0.05 * 3, 1)
                if info['partner'] == 'underconfident':
                    partner_confidence = 0.1 + (pCorrect - 0.5) * 0.8 + error
                    partner_confidence = partner_confidence * 50 + 50
                elif info['partner'] == 'overconfident':
                    partner_confidence = 0.6 + (pCorrect - 0.5) * 0.8 + error
                    partner_confidence = partner_confidence * 50 + 50
                else:
                    partner_confidence = None

            if partner_choice == 'right':
                partner_marker_position = -slider.size[0] / 2 + partner_confidence / 100 * slider.size[0]
            else:
                partner_marker_position = slider.size[0] / 2 - partner_confidence / 100 * slider.size[0]

            partner_marker.pos = (partner_marker_position, slider.pos[1])

            partner_confidence = round(partner_confidence, 2)
            info['partner_confidence'] = partner_confidence

            print(partner_confidence)

            core.wait(0.5)
            slider.draw()
            slider_cover.draw()
            rect_left.draw()
            rect_right.draw()
            slider_marker.draw()
            slider_rating_txt.draw()
            partner_marker.draw()
            win.flip()
            exit_q()
            core.wait(1)

            # STRATEGIC CONDITION
            if info['condition'] == 's':
                # highlight higher confidence decision
                if partner_confidence > participant_confidence:  # partner's decision is chosen
                    higher_conf_box.pos = (partner_marker_position, slider.pos[1])
                    higher_conf_box.lineColor = info['partner_colour']
                    info['participant_chosen'] = False
                    info['partner_chosen'] = True
                    info['joint_correct'] = info['partner_correct']
                else:  # participant's decision is chosen
                    higher_conf_box.pos = (slider_marker.pos[0], slider.pos[1])
                    higher_conf_box.lineColor = (0, 0.8, 0.8)
                    info['participant_chosen'] = True
                    info['partner_chosen'] = False
                    info['joint_correct'] = info['participant_correct']
                slider.draw()
                slider_cover.draw()
                rect_left.draw()
                rect_right.draw()
                slider_marker.draw()
                slider_rating_txt.draw()
                partner_marker.draw()
                higher_conf_box.draw()
                win.flip()
                exit_q()
                core.wait(1)

                # give feedback on joint decision
                if info['joint_correct']:
                    info['trial_score'] = 1
                    higher_conf_box.lineColor = 'lawngreen'
                    feedback_txt = visual.TextStim(win=win, text='JOINT DECISION: CORRECT', height=35, pos=[0, -90],
                                                   color='lawngreen')
                else:
                    info['trial_score'] = 0
                    higher_conf_box.lineColor = 'red'
                    feedback_txt = visual.TextStim(win=win, text='JOINT DECISION: INCORRECT', height=35, pos=[0, -90],
                                                   color='red')
                slider.draw()
                slider_cover.draw()
                rect_left.draw()
                rect_right.draw()
                slider_marker.draw()
                slider_rating_txt.draw()
                partner_marker.draw()
                higher_conf_box.draw()
                feedback_txt.draw()
                win.flip()
                exit_q()
                core.wait(1)

        # confidence slider is on but partner is none (ie confidence slider practice trials)
        else:
            # give feedback if we are in the strategic condition
            higher_conf_box.pos = (slider_marker.pos[0], slider.pos[1])
            if info['condition'] == 's':
                if info['participant_correct']:
                    higher_conf_box.lineColor = 'lawngreen'
                    feedback_txt = visual.TextStim(win=win, text='CORRECT', height=35, pos=[0, -90],
                                                   color='lawngreen')
                else:
                    higher_conf_box.lineColor = 'red'
                    feedback_txt = visual.TextStim(win=win, text='INCORRECT', height=35, pos=[0, -90],
                                                   color='red')
                slider.draw()
                slider_cover.draw()
                rect_left.draw()
                rect_right.draw()
                slider_marker.draw()
                slider_rating_txt.draw()
                higher_conf_box.draw()
                feedback_txt.draw()
                core.wait(0.5)
                win.flip()
                exit_q()
                core.wait(1)

            else:
                pass

    core.wait(gv['wait_period'])
    return info


######################################################################################################################################################
######################################################################################################################################################
######################################################################################################################################################


# INITIALIZE CLOCK & MOUSE
globalClock = core.Clock()
mouse = event.Mouse()
win.mouseVisible = True


# RUN EXPERIMENT
# welcome
welcome_txt.draw()
button.draw()
button_txt.draw()
win.flip()
exit_q()
core.wait(1)
while not mouse.isPressedIn(button):
    pass
if info['task'] == 's':
    welcome2_squircles_txt.draw()
else:
    welcome2_txt.draw()
button.draw()
button_txt.draw()
win.flip()
exit_q()
core.wait(1)
while not mouse.isPressedIn(button):
    pass

# practice instructions
if info['task'] == 's':
    practice_instructions_squircles_txt.draw()
else:
    practice_instructions_txt.draw()
button.draw()
button_txt.draw()
win.flip()
exit_q()
core.wait(1)
while not mouse.isPressedIn(button):
    pass

# practice block
info['staircasing_on'] = True
info['confidence_slider_on'] = False
info['partner'] = None
info['block_count'] = int(info['block_count']) + 1
for trial in range(gv['n_practice_trials']):
    info['trial_in_block'] = trial + 1
    info['trial_count'] = int(info['trial_count']) + 1
    info = do_trial(win, mouse, gv, info)
    dataline = ','.join([str(info[v]) for v in log_vars])
    datafile.write(dataline + '\n')
    datafile.flush()

# confidence slider instructions
win.mouseVisible = True
continue_txt.draw()
button.draw()
button_txt.draw()
win.flip()
exit_q()
core.wait(1)
while not mouse.isPressedIn(button):
    pass
if info['condition'] == 's':
    confidence_feedback_instructions_txt.draw()
else:
    confidence_instructions_txt.draw()
button.draw()
button_txt.draw()
win.flip()
exit_q()
core.wait(1)
while not mouse.isPressedIn(button):
    pass

# confidence slider practice block
info['staircasing_on'] = False
info['confidence_slider_on'] = True
info['partner'] = None
info['block_count'] = int(info['block_count']) + 1
for trial in range(gv['n_confidence_practice_trials']):
    info['trial_in_block'] = trial + 1
    info['trial_count'] = int(info['trial_count']) + 1
    info = do_trial(win, mouse, gv, info)
    dataline = ','.join([str(info[v]) for v in log_vars])
    datafile.write(dataline + '\n')
    datafile.flush()

# experiment start instructions
win.mouseVisible = True
continue_txt.draw()
button.draw()
button_txt.draw()
win.flip()
exit_q()
core.wait(1)
while not mouse.isPressedIn(button):
    pass
if info['condition'] == 's':
    partner1_strategic_instructions_txt.draw()
else:
    partner1_observe_instructions_txt.draw()
button.draw()
button_txt.draw()
win.flip()
exit_q()
core.wait(1)
while not mouse.isPressedIn(button):
    pass

# loading first partner
load_partner()
partner_colours = ["yellow", "magenta"]
info['partner_colour'] = random.choice(partner_colours)
partner_types = ['underconfident', 'overconfident']
info['partner'] = random.choice(partner_types)
partner_image = visual.ImageStim(win=win, image="imgs/partner.png", pos=[0, -100])
partner_oval = visual.Circle(win=win, radius=(120, 160), lineColor=info['partner_colour'], pos=(0, -100))
loading_partner_txt = visual.TextStim(win=win,
                                      text='We have selected your first partner! \n \n Their decision and confidence'
                                           ' rating will be indicated with a %s bar.' % (
                                               info['partner_colour']),
                                      height=th + 10, pos=[0, 180], wrapWidth=1000, color='white')
partner_image.draw()
partner_oval.draw()
loading_partner_txt.draw()
button.draw()
button_txt.draw()
win.flip()
exit_q()
core.wait(1)
while not mouse.isPressedIn(button):
    pass

# first partner
overall_score = 0
info['staircasing_on'] = False
info['confidence_slider_on'] = True
for block in range(gv['n_blocks_per_partner']):
    info['block_with_partner'] = block + 1
    info['block_count'] = int(info['block_count']) + 1

    participant_accuracy_counter = 0
    partner_accuracy_counter = 0
    joint_accuracy_counter = 0
    participant_chosen_counter = 0
    partner_chosen_counter = 0

    for trial in range(gv['n_trials_per_block']):
        info['trial_in_block'] = trial + 1
        info['trial_count'] = int(info['trial_count']) + 1
        info = do_trial(win, mouse, gv, info)
        trial_score = float(info['trial_score'])
        overall_score += trial_score
        dataline = ','.join([str(info[v]) for v in log_vars])
        datafile.write(dataline + '\n')
        datafile.flush()

        if info['condition'] == 's':
            if info['participant_correct']:
                participant_accuracy_counter += 1
            if info['partner_correct']:
                partner_accuracy_counter += 1
            if info['joint_correct']:
                joint_accuracy_counter += 1
            if info['participant_chosen']:
                participant_chosen_counter += 1
            if info['partner_chosen']:
                partner_chosen_counter += 1

    # break between blocks
    break_txt = visual.TextStim(win=win,
                                text='Well done on finishing block %i of %i blocks. \n \n You may take a short break if '
                                     'you like.' % (info['block_count'] - 2, gv['n_blocks_per_partner'] * 2),
                                height=th + 10, pos=[0, 40], wrapWidth=1000, color='white')
    if info['condition'] == 's':
        break_txt = visual.TextStim(win=win,
                                    text='Well done on finishing block %i of %i blocks. You may take a short break if you like. \n \n \n'
                                         'For joint decisions on this last block, \n \n '
                                         'your own accuracy was %i%% \n '
                                         'your partner\'s accuracy was %i%% \n '
                                         'your joint accuracy was %i%% \n \n'
                                         'Your response was chosen on %i trials. Your partner\'s response was chosen on %i trials.'
                                         % (info['block_count'] - 2, gv['n_blocks_per_partner'] * 2,
                                            participant_accuracy_counter / gv['n_trials_per_block'] * 100,
                                            partner_accuracy_counter / gv['n_trials_per_block'] * 100,
                                            joint_accuracy_counter / gv['n_trials_per_block'] * 100,
                                            participant_chosen_counter, partner_chosen_counter),
                                    height=th + 10, pos=[0, 0], wrapWidth=1000, color='white')
    break_txt.draw()
    button.draw()
    button_txt.draw()
    win.flip()
    exit_q()
    core.wait(1)
    while not mouse.isPressedIn(button):
        pass

# questionnaire first partner
win.mouseVisible = True
# questionnaire partner 1
qtxt1.draw()
win.flip()
core.wait(0.7)
qtxt2.draw()
win.flip()
core.wait(0.7)
qtxt3.draw()
win.flip()
core.wait(0.7)
qtxt4.draw()
win.flip()
core.wait(1.4)
p1_likeability = questionnaire_item('How much did you like your partner?')
p1_accuracy = questionnaire_item('How accurate do you think your partner was compared to yourself?',
                                 '\n1\n much less accurate', '\n10\n much more accurate')
p1_confidence = questionnaire_item('How confident do you think your partner was compared to yourself?',
                                   '\n1\n much less confident', '\n10\n much more confident')
p1_partner_work = questionnaire_item('How well do you think you and your partner worked together in the game?',
                                     '\n1\n not at all', '\n10\n very well')

# second partner instructions
win.mouseVisible = True
halfway_txt.draw()
button.draw()
button_txt.draw()
win.flip()
exit_q()
core.wait(1)
while not mouse.isPressedIn(button):
    pass
if info['condition'] == 's':
    partner2_strategic_instructions_txt.draw()
else:
    partner2_observe_instructions_txt.draw()
button.draw()
button_txt.draw()
win.flip()
exit_q()
core.wait(1)
while not mouse.isPressedIn(button):
    pass

# loading second partner
load_partner()
if info['partner_colour'] == partner_colours[0]:
    info['partner_colour'] = partner_colours[1]
else:
    info['partner_colour'] = partner_colours[0]

if info['partner'] == partner_types[0]:
    info['partner'] = partner_types[1]
else:
    info['partner'] = partner_types[0]

partner_image = visual.ImageStim(win=win, image="imgs/partner.png", pos=[0, -100])
partner_oval = visual.Circle(win=win, radius=(120, 160), lineColor=info['partner_colour'], pos=(0, -100))
loading_partner_txt = visual.TextStim(win=win,
                                      text='We have selected your second partner! \n \n Their decision and confidence'
                                           ' rating will be indicated with a %s bar.' % (
                                               info['partner_colour']),
                                      height=th + 10, pos=[0, 180], wrapWidth=1000, color='white')
partner_image.draw()
partner_oval.draw()
loading_partner_txt.draw()
button.draw()
button_txt.draw()
win.flip()
exit_q()
core.wait(1)
while not mouse.isPressedIn(button):
    pass

# second partner
info['staircasing_on'] = False
info['confidence_slider_on'] = True
for block in range(gv['n_blocks_per_partner']):
    info['block_with_partner'] = block + 1
    info['block_count'] = int(info['block_count']) + 1

    participant_accuracy_counter = 0
    partner_accuracy_counter = 0
    joint_accuracy_counter = 0
    participant_chosen_counter = 0
    partner_chosen_counter = 0

    for trial in range(gv['n_trials_per_block']):
        info['trial_in_block'] = trial + 1
        info['trial_count'] = int(info['trial_count']) + 1
        info = do_trial(win, mouse, gv, info)
        trial_score = trial_score = float(info['trial_score'])
        overall_score += trial_score
        dataline = ','.join([str(info[v]) for v in log_vars])
        datafile.write(dataline + '\n')
        datafile.flush()

        if info['condition'] == 's':
            if info['participant_correct']:
                participant_accuracy_counter += 1
            if info['partner_correct']:
                partner_accuracy_counter += 1
            if info['joint_correct']:
                joint_accuracy_counter += 1
            if info['participant_chosen']:
                participant_chosen_counter += 1
            if info['partner_chosen']:
                partner_chosen_counter += 1

    # break between blocks
    break_txt = visual.TextStim(win=win,
                                text='Well done on finishing block %i of %i blocks. \n \n You may take a short break if '
                                     'you like.' % (info['block_count'] - 2, gv['n_blocks_per_partner'] * 2),
                                height=th + 10, pos=[0, 40], wrapWidth=1000, color='white')
    if info['condition'] == 's':
        break_txt = visual.TextStim(win=win,
                                    text='Well done on finishing block %i of %i blocks. You may take a short break if you like. \n \n \n'
                                         'For joint decisions on this last block, \n \n '
                                         'your own accuracy was %i%% \n '
                                         'your partner\'s accuracy was %i%% \n '
                                         'your joint accuracy was %i%% \n \n '
                                         'Your response was chosen on %i trials. Your partner\'s response was chosen on %i trials.'
                                         % (info['block_count'] - 2, gv['n_blocks_per_partner'] * 2,
                                            participant_accuracy_counter / gv['n_trials_per_block'] * 100,
                                            partner_accuracy_counter / gv['n_trials_per_block'] * 100,
                                            joint_accuracy_counter / gv['n_trials_per_block'] * 100,
                                            participant_chosen_counter, partner_chosen_counter),
                                    height=th + 10, pos=[0, 0], wrapWidth=1000, color='white')
    break_txt.draw()
    button.draw()
    button_txt.draw()
    win.flip()
    exit_q()
    core.wait(1)
    while not mouse.isPressedIn(button):
        pass

# questionnaire partner 2
win.mouseVisible = True
qtxt1.draw()
win.flip()
core.wait(0.7)
qtxt2.draw()
win.flip()
core.wait(0.7)
qtxt3.draw()
win.flip()
core.wait(0.7)
qtxt4.draw()
win.flip()
core.wait(1.4)
p2_likeability = questionnaire_item('How much did you like your partner?')
p2_accuracy = questionnaire_item('How accurate do you think your partner was compared to yourself?',
                                 '\n1\n much less accurate', '\n10\n much more accurate')
p2_confidence = questionnaire_item('How confident do you think your partner was compared to yourself?',
                                   '\n1\n much less confident', '\n10\n much more confident')
p2_partner_work = questionnaire_item('How well do you think you and your partner worked together in the game?',
                                     '\n1\n not at all', '\n10\n very well')

# score reveal
overall_score = round(overall_score, 0)
reward = overall_score * 2 / 100

if info['condition'] == 's':
    score_txt = visual.TextStim(win=win,
                                text='Congratulations, you have made %i correct joint decisions in this experiment! \n \n This '
                                     'equates to a cash bonus of £ %.2f for you :)' % (overall_score, reward),
                                height=th + 10, pos=[0, 40], wrapWidth=1000, color='white')
else:
    score_txt = visual.TextStim(win=win,
                                text='Congratulations, you have reached a score of %i in this experiment! \n \n This '
                                     'equates to a cash bonus of £ %.2f for you :)' % (overall_score, reward),
                                height=th + 10, pos=[0, 40], wrapWidth=1000, color='white')
score_txt.draw()
button.draw()
button_txt.draw()
win.flip()
exit_q()
core.wait(1)
while not mouse.isPressedIn(button):
    pass

# save partner ratings and score and payment in a last dataline
info = {key: None for key in info}

info['final_score'] = overall_score
info['reward'] = reward

info['p1_likeability'] = p1_likeability
info['p1_accuracy'] = p1_accuracy
info['p1_confidence'] = p1_confidence
info['p1_team_work'] = p1_partner_work
info['p2_likeability'] = p2_likeability
info['p2_accuracy'] = p2_accuracy
info['p2_confidence'] = p2_confidence
info['p2_team_work'] = p2_partner_work
info['p2_team_work'] = p2_partner_work
info['end_date'] = data.getDateStr()

dataline = ','.join([str(info[v]) for v in log_vars])
datafile.write(dataline + '\n')
datafile.flush()

# thank you
thanks_txt.draw()
win.flip()
core.wait(5)

# CLOSE WINDOW
win.close()
core.quit()

import os
import random
from psychopy import visual, core, data, event, logging
import numpy as np  # whole numpy lib is available, prepend 'np.'

# Set up triggers
from daq import (setup_triggers, send_trigger_fast,
                 send_trigger_slow, send_trigger)
from triggers import triggers
task = setup_triggers()

print('Reminder: Press Q to quit.')
fullscreen = 0


# Session information
dummy = 0  # Set to 1 to skip subject details while developing
if dummy == 1:
    participant = 901
else:
    # Both must be numeric!
    participant = eval(input('Participant number?\n'))

# Hard coded stuff
block_duration = 3 * 60
nblocks = 5
nreps = 2
colours = list(range(1, 19))

gv = dict(
    block_duration=block_duration,
    nblocks=nblocks,
    nblocks_total=nblocks * nreps,
    oven_dim=.25,
    souffle_size=.25,
    secs_to_ready=.5,
    secs_per_wobble=1,
    wobble_angle=30,
    late_reward=1,
    early_reward=1,
    planting_time=1,
    feedback_time=2,
    mu_ready=6,
    start_score=0,
    break_every=2,
    max_wait=120,
    oven_colors=random.sample(colours, nblocks * nreps),
    oven_color=None,
    block_order=np.ravel([random.sample(list(range(nblocks)), nblocks)
                          for i in range(nreps)])
)

info = dict(
    participant=participant,
    condition=None,
    date=data.getDateStr(),
    expName='souffles1',
    block_duration=block_duration,
    nblocks=nblocks,
    practice=0,
    block_nr=0,
    trial_nr=None,
    souffle=None,
    reward=None,
    t_start=None,
    t_start_task=None,
    t_start_block=None,
    t_ready=None,
    t_action=None,
    outcome=None,
    focus=1,
    elapsed=0,
    block_elapsed=0,
    score=gv['start_score'],
)
del block_duration, nblocks


def generate_wait_frames(condition):
    '''
    Conditions: 0 = N(3, 1.5);
    Conditions: 1 = N(5, 1.5);
    Conditions: 2 = N(7, 1.5);
    Conditions: 3 = N(9, 1.5);
    Conditions: 4 = N(11, 1.5);
    '''
    means = [3, 5, 7, 9, 11]
    sds = [1, 1, 1, 1, 1]
    mean, sd = means[condition], sds[condition]
    w_seconds = np.random.normal(mean, sd)
    w_frames = np.round(w_seconds * 60, 0)
    # print 'Condition = %i, M = %i, SD = %i, w = %.2f' % (
    #     condition, mean, sd, w_frames)
    return w_frames


# Useful constants
black = (-1, -1, -1)
green = (0, 1., 0)
red = (1, -1, -1)
grey = (.3, .3, .3)

# Logging
log_vars = list(info.keys())
if not os.path.exists('data'):
    os.mkdir('data')
filename = os.path.join('data', '%s_%s' % (info['participant'], info['date']))
## Save a log file for detail verbose info
# logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(0)  # this outputs to the screen, not a file

datafile = open(filename + '.csv', 'w')
datafile.write(','.join(log_vars) + '\n')
datafile.flush()

# Setup the Window
if fullscreen:
    size = [1600, 1200]
else:
    size = [800, 600]

win = visual.Window(
    # winType='pygame',
    gammaErrorPolicy='ignore',
    size=size, fullscr=fullscreen, screen=0,
    allowGUI=True, allowStencil=False,
    monitor='testMonitor', color=[1., 1., 1.], colorSpace='rgb',
    blendMode='avg', useFBO=True, units='height')

#############
## Stimuli ##
#############
th = .05
planting_text = visual.TextStim(win=win, text='Putting dough in the oven...', height=.04, pos=[0, 0], color=black)

reward_text = visual.TextStim(win=win, text='+X', height=th, pos=[0, 0], color=black)
score_textA = visual.TextStim(win=win, text='Score:', height=th, pos=[0, -2 * th], color=black)
score_textB = visual.TextStim(win=win, text='X', height=th, pos=[0, 6 * th], color=black)
time_textA = visual.TextStim(win=win, text='Time elapsed:', height=th, pos=[0, -5 * th], color=black)
time_textB = visual.TextStim(win=win, text='X', height=th, pos=[0, -6 * th], color=black)
break_textA = visual.TextStim(win=win, text='Time for a break.', height=th, pos=[0, +3 * th], color=black)
break_textB = visual.TextStim(win=win, text='Press SPACE to continue.', height=th, pos=[0, +1 * th], color=black)
start_text = visual.TextStim(win=win, text='Press SPACE to begin.', height=.05, pos=[0, 0], color=black)
reward_text = visual.TextStim(win=win, text='A perfect bake! Have a point.', height=th, pos=[0, -6 * th], color=black)
failure_text = visual.TextStim(win=win, text="Too soon! It's ruined!", height=th, pos=[0, -6 * th], color=red)

oven = visual.ImageStim(win=win, image='imgs/oven.jpg', name='oven',
                        size=gv['oven_dim'],
                        pos=(0., 0.), colorSpace='rgb', ori=0)
souffle = visual.ImageStim(win=win, image='imgs/flat_souffle.png', name='souffle',
                           size=gv['souffle_size'],
                           pos=(0., 0.), ori=0)

## Globally used constants.
max_trial_len = 60 * gv['max_wait']
interp_ready = np.linspace(0, 1, int(gv['secs_to_ready'] * 60))  # Timing for souffle getting ready.
nsteps = 60 * gv['secs_per_wobble']
nrounds = 1 + (max_trial_len / nsteps)
wobble = np.cos(np.linspace(0, np.pi * 2 * nsteps, nsteps))
wobble = wobble * -.5 * gv['wobble_angle']


def flip_coin(p):
    return 1 * (np.random.uniform() < p)


def markov_chain(pool, length):
    '''
    Use range(5) as pool to exclude red, range(6) to include it.
    '''
    pool = np.array(pool)
    new = np.random.choice(pool)
    chain = [new]
    while len(chain) < length:
        new = np.random.choice(pool[pool != new])
        chain.append(new)
    return chain


def get_keys(keyList=['space', 'q']):
    '''This just checks if anything has been pressed - it doesn't wait'''
    keys = event.getKeys(keyList=keyList)
    res = len(keys) > 0
    if res:
        if 'q' in keys:
            win.close()
            core.quit()
    return res


def do_trial(info, trial_nr):
    ## print 'Condition', info['condition']
    info['trial_nr'] = trial_nr
    # souffle_path = np.random.choice(souffle_names)
    # info['souffle'] = souffle_path
    info['t_ready'] = info['t_action'] = -1
    # souffle.image = souffle_path
    souffle.size = 0.
    oven.size = gv['oven_dim']
    ready = False
    reward = 0
    feedback = failure_text
    souffle.image = "imgs/flat_souffle.png"
    ready_frame = generate_wait_frames(info['condition'])
    event.clearEvents()
    info['t_start'] = clock.getTime()
    ## Putting dough in the oven...
    trial_clock.reset()
    planting_text.draw()
    win.flip()
    core.wait(gv['planting_time'])
    send_trigger_slow(triggers['trial_start'], task)
    event.clearEvents()
    for fr in range(max_trial_len):
        ## Watch time
        # if fr % 60 == 0:
        #     ## print('%i seconds' % (fr / 60))
        ## Check for ready
        if fr == ready_frame:
            reward = 1
            feedback = reward_text
            ready = True
            ## print("ready")
            info["t_ready"] = clock.getTime()
            souffle.image = "imgs/souffle.png"
        ## Wobble oven
        oven.ori = wobble[fr % nsteps]
        # Update colour
        # rgb = gradient[:, fr]
        # oven.color = rgb
        pressed = get_keys()
        if pressed:
            info['t_action'] = clock.getTime()
            send_trigger_fast(triggers['response'], task)
            break
        souffle.draw()
        oven.draw()
        win.flip()
        send_trigger_fast(0, task)
    # animate souffle appearance
    for fr in range(int(gv['secs_to_ready'] * 60)):
        ib = interp_ready[fr]
        oven.size = gv['oven_dim'] * (1 - ib)
        souffle.size = gv['souffle_size'] * ib
        souffle.draw()
        oven.draw()
        win.flip()
    info['reward'] = reward
    info['score'] += reward
    score_textB.text = 'Score: %i' % info['score']
    score_textB.draw()
    # ## print(info)
    souffle.draw()
    feedback.draw()
    win.flip()
    t0 = clock.getTime()
    send_trigger_fast(0, task)
    core.wait(gv['feedback_time'])
    send_trigger_slow(triggers['trial_end'], task)
    ## print clock.getTime() - t0
    return info


def show_block_instructions(block=None):
    if block == 0:
        txt1 = 'Welcome to the task!'
    else:
        blocks_to_go = len(gv['block_order']) - info['block_nr']
        time_to_go = (info["block_duration"] * blocks_to_go) / 60
        txt1 = "Well done! %i minutes to go!" % time_to_go
    txt2 = "You've scored %i points so far." % info['score']
    txt3 = "Here's the oven you'll be\nusing for the next few minutes."
    txt = '\n'.join([txt1, txt2, txt3])
    bigbreak_text = visual.TextStim(win=win, text=txt, wrapWidth=1.5,
                                    height=th, pos=[0, +5 * th], color=black)
    oven.ori = 0
    oven.size = gv['oven_dim']
    space_text = visual.TextStim(win=win, text="Press SPACE to continue.",
                                 height=th, pos=[0, -5 * th], color=black)
    for obj in [bigbreak_text, oven, space_text]:
        obj.draw()
    win.flip()
    keys = event.waitKeys(keyList=['space'])


def take_break():
    for txt in [score_textA, score_textB, time_textA, time_textB, break_textA, break_textB]:
        txt.draw()
    win.flip()
    send_trigger(triggers['break_start'], task)
    keys = event.waitKeys(keyList=['space'])
    send_trigger(triggers['break_end'], task)


def end():
    break_textA.text = 'End of Experiment.\nYou scored %i points' % info['score']
    break_textB.text = 'Thanks!'
    for txt in [break_textA, break_textB]:
        txt.draw()
    win.flip()
    send_trigger(triggers['exp_end'], task)
    keys = event.waitKeys(keyList=['q'])


## Start the experiment

event.clearEvents()
clock = core.Clock()
trial_clock = core.Clock()
# Press SPACE to begin.
start_text.draw()
win.flip()
keys = event.waitKeys(keyList=['space', 'q'])
send_trigger(triggers['exp_start'], task)
info['start_time'] = clock.getTime()
trial_nr = 0
for block in range(gv['nblocks_total']):
    condition = gv["block_order"][block]
    gv["oven_color"] = gv["oven_colors"][block]
    oven.image = "imgs/oven%s.png" % gv["oven_color"]
    info['condition'] = condition
    info['block_nr'] = block
    ## print '--------------------------------'
    ## print 'block,condition,oven_color,'
    ## print block, condition, gv['oven_color']
    show_block_instructions(block)
    send_trigger(triggers['block_start'], task)
    info["t_start_block"] = clock.getTime()
    while True:
        info = do_trial(info, trial_nr)
        trial_nr += 1
        dataline = ','.join([str(info[v]) for v in log_vars])
        datafile.write(dataline + '\n')
        datafile.flush()
        t_elapsed = clock.getTime() - info["t_start_block"]
        ## print(t_elapsed)
        if t_elapsed > info['block_duration']:
            ## End of block
            break
    send_trigger(triggers['block_end'], task)

## Finish
send_trigger(triggers['exp_end'], task)
end()
win.close()
core.quit()

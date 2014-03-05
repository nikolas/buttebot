from util import hook
from butter import butter

import itertools
import math
import random
import time

def poissonvariate(lambd):
    x = random.random()

    # special-case i = 0
    coeff = math.exp(-lambd)
    factorial = 1.0
    x -= coeff
    if x < 0: return 0

    # i = (1, 2, ...)
    for i in itertools.count(1):
        factorial *= i
        x -= coeff * (lambd**i/factorial)
        if x < 0: return i

@hook.command
def butt(msg, me=None):
    try:
        return butter.buttify(msg, min_words=1)
    except:
        me("can't butt the unbuttable!")
        raise

@hook.command
def debutt(msg, me=None):
    sent, score = butter.score_sentence(msg)
    result = ''

    result += '{0}: '.format(score.sentence())
    for i, word in enumerate(sent):
        if score.word(i) == 0:
            result += '-'.join(word) + '(0) '
        else:
            result += '-'.join(word) + '({0}: {1}) '.format(
                score.word(i), score.syllable(i))
    return result

class ChannelState(object):
    def __init__(self, next_time = 0, lines_left = 0):
        self.next_time = next_time
        self.lines_left = lines_left

channel_states = {}

# TODO: don't fire this when someone ran .butt!
@hook.singlethread
@hook.event('PRIVMSG')
def autobutt(_, chan=None, msg=None, bot=None, say=None):
    butt_config = bot.config['butt'] or {}
    rate_mean  = butt_config.get('rate_mean', 300)
    rate_sigma = butt_config.get('rate_sigma', 60)
    lines_mean = butt_config.get('lines_mean', 20)
    now = time.time()

    if chan[0] == '#': # public channel
        if chan in channel_states:
            state = channel_states[chan]
            state.lines_left -= 1

            if state.next_time > now:
                return

            sent, score = butter.score_sentence(msg)

            if score.sentence() == 0 or score.sentence() < state.lines_left:
                return

            say(butter.buttify_sentence(sent, score))

        channel_states[chan] = ChannelState(
            random.normalvariate(rate_mean, rate_sigma) + now,
            poissonvariate(lines_mean)
        )
    else: # private message
        try:
            say(butter.buttify(msg))
        except:
            pass

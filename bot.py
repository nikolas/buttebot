#!/usr/bin/env python

import os
try:
    import Queue as queue
except ImportError:
    import queue
import sys
import time

sys.path += ['plugins']  # so 'import hook' works without duplication
sys.path += ['lib']
os.chdir(sys.path[0] or '.')  # do stuff relative to the install directory


class Bot(object):
    pass


bot = Bot()

print('Loading plugins')

# bootstrap the reloader
eval(compile(open(os.path.join('core', 'reload.py'), 'U').read(),
    os.path.join('core', 'reload.py'), 'exec'))
reload(init=True)

config()
if not hasattr(bot, 'config'):
    exit()

print('Connecting to IRC')

bot.conns = {}

try:
    for name, conf in bot.config['connections'].items():
        if conf.get('ssl'):
            bot.conns[name] = SSLIRC(conf['server'], conf['nick'], conf=conf,
                    port=conf.get('port', 6667), channels=conf['channels'],
                    ignore_certificate_errors=conf.get('ignore_cert', True))
        else:
            bot.conns[name] = IRC(conf['server'], conf['nick'], conf=conf,
                    port=conf.get('port', 6667), channels=conf['channels'])
except (Exception, e):
    print('ERROR: malformed config file', e)
    sys.exit()

bot.persist_dir = os.path.abspath('persist')
if not os.path.exists(bot.persist_dir):
    os.mkdir(bot.persist_dir)

print('Running main loop')

while True:
    reload()  # these functions only do things
    config()  # if changes have occured

    for conn in bot.conns.values():
        try:
            out = conn.out.get_nowait()
            main(conn, out)
        except queue.Empty:
            pass
    while all(conn.out.empty() for conn in bot.conns.values()):
        time.sleep(.1)

#!/usr/bin/env python3
import sleekxmpp
import subprocess
import config
import os

def run_script(message):
    parts = message.strip().split(' ')
    command = parts[0].lower()
    args = parts[1:]

    try:
        p = subprocess.run(['scripts/{}'.format(command)] + args, stdout=subprocess.PIPE, timeout=10)
        return p.stdout.decode('utf-8')
    except Exception as e:
        p = subprocess.run(['scripts/unknown'] + parts, stdout=subprocess.PIPE)
        return p.stdout.decode('utf-8')

class LeoBot(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid, password)

        self.add_event_handler('session_start', self.start)
        self.add_event_handler('message', self.message)

    def start(self, event):
        self.send_presence()
        self.get_roster()

        if config.values['should-use-redis']:
            print('Using Redis')
            import threading
            threading.Thread(target=self.redis_thread).start()

        print('Session started')

    def message(self, msg):
        if msg['type'] in ('chat', 'normal'):
            message = msg['body']
            reply = run_script(message)
            msg.reply(reply).send()

    def redis_thread(self):
        import redis
        import time
        
        r = redis.Redis()
        p = r.pubsub()
        p.subscribe('xmpp-message')

        while True:
            m = p.get_message()
            if m:
                try:
                    self.send_message(mto=config.values['redis-msg-target'], mbody=m['data'].decode('utf-8'))
                except Exception as e:
                    print(e)
            time.sleep(1)

if __name__ == '__main__':
    config.read_config()
    
    xmpp = LeoBot(os.environ['username'], os.environ['password'])
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0060') # PubSub
    xmpp.register_plugin('xep_0199') # XMPP Ping

    if xmpp.connect(config.values['server']):
        xmpp.process(block=True)
        print("Done")
    else:
        print("Unable to connect.")

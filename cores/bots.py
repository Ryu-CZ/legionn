'''!
@brief Holds various bots in form of Cores of Legionn.
@date Created on 11 Jan 2016
@author: [Ryu-CZ](https://github.com/Ryu-CZ)
'''

import cleverbot
import logging
import re
from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout
from interfaces import Core, Unit
from copy import copy
from collections import deque


class CleverBotMind(Unit):
    '''!
    @brief Represents state of Cleverbot mind.
    '''
    
    def __init__(self, core):
        '''!
        @brief Construct new clear mind with no conversation history
        @param core: core with AI of this mind
        '''
        self.core = core
        self.data = {
            'stimulus': '',
            'start': 'y',  # Never modified
            'sessionid': '',
            'vText8': '',
            'vText7': '',
            'vText6': '',
            'vText5': '',
            'vText4': '',
            'vText3': '',
            'vText2': '',
            'icognoid': 'wsf',  # Never modified
            'icognocheck': '',
            'fno': 0,  # Never modified
            'prevref': '',
            'emotionaloutput': '',  # Never modified
            'emotionalhistory': '',  # Never modified
            'asbotname': '',  # Never modified
            'ttsvoice': '',  # Never modified
            'typing': '',  # Never modified
            'lineref': '',
            'sub': 'Say',  # Never modified
            'islearning': 1,  # Never modified
            'cleanslate': False,  # Never modified
            }
        self.conversation = []
         
    def write(self, ai):
        '''!
        @brief Upload this CleverBotMind into given AI
        @param ai: cleverbot#Cleverbot instance
        '''
        if isinstance(ai, cleverbot.Cleverbot):
            ai.data = self.data
            ai.conversation = self.conversation
        else:
            raise TypeError("'ai' object is not an instance of 'Cleverbot'")
        
    def read(self, ai):
        '''!
        @brief Download mind from given AI into this CleverBotMind
        @param ai: cleverbot#Cleverbot instance
        '''
        if isinstance(ai, cleverbot.Cleverbot):
            self.data = copy(ai.data)
            self.conversation = copy(ai.conversation)
        else:
            raise TypeError("'ai' object is not an instance of 'Cleverbot'")


class CleverJabberBot(ClientXMPP, Core):
    '''!
    @brief It enables users to communicate on jabber with cleverbot service.
    Combination of Cleverbot with Jabber client. 
    '''
    help = '''This bot supports commands:
    
    \thelp
    \t  shows this help.
    
    \thistory
    \t  prints list if used commands (oldest command as first line, most recent as last line).
    
    \tjoin <roomName>
    \t  bot enters the given room.
    \t  roomName .. there are two possible formats 'name@domain' | 'name', when you use only name botappends @conference.domain, composed from jid with '@conference.'<jidDomain> prefix.

    \tleave <roomName>
    \t  bot leaves the given room.
    \t  roomName .. there are two possible formats 'name@domain' | 'name', when you use only name botappends @conference.domain, composed from jid with '@conference.'<jidDomain> prefix.
    
    \tnick
    \t  returns currently set nick of bot in jabber.
    
    \tsetnick <nickValue>
    \t  sets nick of bot in jabber.
    '''

    def __init__(self, jid, password, name='cleverbot', description='API for www.cleverbot.com', historylen=255):
        self._nick = jid.split('@')[0]
        if name is None:
            name = self._nick
        ClientXMPP.__init__(self, jid, password)
        Core.__init__(self, name=name, description=description) 
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0060') # PubSub
        self.register_plugin('xep_0199') # XMPP Ping
        self.register_plugin('xep_0045') # MUC
        self.ai = cleverbot.Cleverbot()
        self.is_connected = False
        self.conference_server = 'conference.{0}'.format(jid.split('@')[1])
        self.commands_history = deque(maxlen=historylen)
    
    def session_start(self, event):
        self.send_presence()
        try:
            self.get_roster()
            self.is_connected =  True
        except IqError as err:
            logging.error('There was an error getting the roster')
            logging.error(err.iq['error']['condition'])
            self.disconnect()
            self.is_connected = False
        except IqTimeout:
            logging.error('Server is taking too long to respond')
            self.disconnect()
            self.is_connected = False
    
    def parseRoom(self, jid):
        if '@' in jid:
            return jid
        return '{0}@{1}'.format(jid, self.conference_server) 
    
    def dispatch(self, command):
        if command.startswith('join'):
            words = command.split()
            if len(words) != 2:
                return "ERROR: invalid number of arguments"
            self.plugin['xep_0045'].joinMUC(room=self.parseRoom(words[1]),
                                            nick=self._nick,
                                            wait=False)
            return "done"
        elif command.startswith('leave'):
            words = command.split()
            if len(words) != 2:
                return "ERROR: invalid number of arguments"
            self.plugin['xep_0045'].leaveMUC(room=self.parseRoom(words[1]),
                                             nick=self._name,
                                             msg='bye')
            return "done"
        elif command.startswith('setnick'):
            words = command.split()
            if len(words) != 2:
                return "ERROR: invalid number of arguments"
            self._nick = words[2]
            return "done"
        elif command.startswith('nick'):
            return self._nick
        elif command.startswith('history'):
            return '\n'.join(self.commands_history)
        elif command.startswith('help'):
            return self.help
        else:
            logging.ERROR('not valid command: {0}'.format(command))
            return "ERROR: not valid command"
        
    def message(self, msg):
        #ecample msg:
        #<message to="gs2_bot@jabber.kajot.cz" from="trval@jabber.kajot.cz/9c5d4bc8" id="5a8c684f-dae7-4b60-aaae-a2a3ec116d9d" type="chat"><body>hi there</body><active xmlns="http://jabber.org/protocol/chatstates" /></message>
        if msg['type'] in ('chat', 'normal'):
            if len(re.sub(r'\s', '', msg['body'])):
                if msg['body'].startswith('#'):
                    command = msg['body'][1:]
                    logging.info('command {0}'.format(command))
                    self.commands_history.append(command)
                    msg.reply(self.dispatch(command=command)).send()
                else:
                    logging.info('asking {0}'.format(msg))
                    msg.reply(self.ai.ask(question=msg['body'])).send()
            else:
                msg.reply(msg['body']).send()
    
    def room_message(self, msg):
        if msg['type'] == 'groupchat' and msg['mucnick'] != self._nick:
            logging.info('groupchat: {0}'.format(msg))
            if msg['body'].startswith('#'):
                command = msg['body'][1:]
                logging.info('command {0}'.format(command))
                self.commands_history.append(command)
                msg.reply(self.dispatch(command=command)).send()
            elif self._nick in msg['body']:
                logging.info('asking {0}'.format(msg))
                msg.reply('to {0}: {1}'.format(msg['mucnick'], self.ai.ask(question=msg['body'].replace(self._nick, '')))).send()
    
    
    def activate(self, context=None):
        logging.info('\nactivating')
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)
        self.add_event_handler("groupchat_message", self.room_message)
        self.is_connected = (self.connect() is not None)
        if self.is_connected:
            self.process(block=False)
            logging.info('\n..activated\n')
        else:
            logging.error('activation failed - Unable to connect')
        
    def deactivate(self, context=None):
        logging.info('\ndeactivating')
        self.remove_handler("session_start")
        self.remove_handler("message")
        self.remove_handler("groupchat_message")
        self.disconnect(wait=True)
        self.is_connected = False
        logging.info('\n..deactivated\n')


if __name__ == '__main__':
    import config
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')
    core = CleverJabberBot(config.jabber['id'], config.jabber['password'])
    core.activate()
    raw_input("\nPress Enter to close...\n")
    core.deactivate()
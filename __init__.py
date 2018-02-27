import requests
import commands
from os.path import dirname, join

from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger

__author__ = 'noahgreenstein'

LOGGER = getLogger(__name__)


class PingSkill(MycroftSkill):

    def __init__(self):
        super(PingSkill, self).__init__(name="PingSkill")

    def initialize(self):
        self.load_data_files(dirname(__file__))

        ping_intent = IntentBuilder("PingIntent")\
            .require("PingKeyword").require("key").build()
        self.register_intent(ping_intent, self.handle_ping_intent)

        monitor_intent = IntentBuilder("MonitorIntent")\
            .require("MonitorKeyword").require("monitorkey").build()
        self.register_intent(monitor_intent, self.handle_monitor_intent)

        # TODO terminate_mointor_intent # deschedule the event name='monitor_ping_status')

    def handle_ping_intent(self, message):       
#        import subprocess as sp
        hosts = dict()
        f = open(join(dirname(__file__), "hosts.txt"), 'r')
        for line in f.readlines():
            if line.startswith("#") or "," not in line:
                continue
            l = line.split(",")
            hosts[l[0].strip()] = [l[1].strip(), l[2].strip()]
        f.close()
        
        k = message.data.get("key").lower()
        if k in hosts:
            if hosts[k][0] == '1':
                response = requests.get(hosts[k][1])
                data = {"response": response.reason + " " +
                        str(response.status_code)}
                self.speak_dialog("ServerResponse", data)
            else:
                status,result = commands.getstatusoutput("ping -c1 -w2 "
                                + hosts[k][1][(hosts[k][1]).find("//")+2:])
                if status == 0:
                    data = {"response": result.split('/')[5]}
                    self.speak_dialog("PingResponse", data)
                else:
                    self.speak_dialog("PingFailure")
                    LOGGER.debug(result)
                    result_message = result.lower().strip()
                    if result_message.startswith('ping:'):
                        result_message = result_message[5:]
                    if ('name' in result_message or
                            'dns' in result_message or
                            'source' in result_message or
                            'destination' in result_message or
                            'network' in result_message or
                            'host' in result_message):
                        self.speak(result_message)
        else:
            # way too complex to parse spoken full URLs, 
            # just exit if keyword not found. 
            self.speak_dialog("KeywordFailure")
            LOGGER.info('Requested network node alias not found '
                        'in hosts.txt registry.')
            # Possible TODO: add spoken URL to ping
            # Parse URL Libraries? Just google it and ping first result?
            #  if any item in array is 'dot', replace with '.'?
            #    ... so, `slashdot.com` is impossible to parse.
            #  replace: calm, come, cum, etc., with `com`, if last?

    def handle_monitor_event(self,data):
        pass
        # TODO: implement this stub
        # data will be hostname, maybe previous/current/initial status
        # if http fails, it might still be interesting to fall back to the ping part anyway

    def handle_monitor_intent(self, message):
        # TODO: also get to this point via conversational context
        # https://mycroft.ai/documentation/skills/conversational-context/
        hosts = dict()
        f = open(join(dirname(__file__), "hosts.txt"), 'r')
        for line in f.readlines():
            if line.startswith("#") or "," not in line:
                continue
            l = line.split(",")
            hosts[l[0].strip()] = [l[1].strip(), l[2].strip()]
        f.close()
        
        #https://community.mycroft.ai/t/running-background-processes-with-skills/2986/4?u=jrwarwick
        k = message.data.get("key").lower()
        if k in hosts:
            #establish initial state, announce that, then declare intent to notify of CHANGE/TOGGLE
            if hosts[k][0] == '1':                
                response = requests.get(hosts[k][1])
                data = {"response": response.reason + " " +
                        str(response.status_code)}
                self.speak_dialog("ServerResponse", data)
                self.schedule_repeating_event(handle_monitor_event, 
                                              datetime.datetime.now() + datetime.timedelta(0,4), 20, 
                                              data={host:hosts[k][1],
                                                    connect_type:'http',
                                                    initstate:response.status_code},
                                              name='monitor_ping_status')
            else:
                status,result = commands.getstatusoutput("ping -c1 -w2 "
                                + hosts[k][1][(hosts[k][1]).find("//")+2:])
                if status == 0:
                    data = {"response": result.split('/')[5]}
                    self.speak_dialog("PingResponse", data)
                    self.schedule_repeating_event(handle_monitor_event, 
                                                  datetime.datetime.now() + datetime.timedelta(0,4), 20, 
                                                  data={host:hosts[k][1],
                                                        connect_type:'ping',
                                                        initstate:status},
                                                  name='monitor_ping_status')
                else:
                    self.speak_dialog("PingFailure")
                    LOGGER.debug(result)
                    result_message = result.lower().strip()
                    if result_message.startswith('ping:'):
                        result_message = result_message[5:]
                    if ('name' in result_message or
                            'dns' in result_message or
                            'source' in result_message or
                            'destination' in result_message or
                            'network' in result_message or
                            'host' in result_message):
                        self.speak(result_message)
        else:
            self.speak_dialog("KeywordFailure")
            LOGGER.info('Requested network node alias not found '
                        'in hosts.txt registry.')
            

    # Ping/ Server responses usually don't take more than 1 or 2 seconds at
    # most to register so there isn't much opportunity to stop the operation.
    def stop(self):
        pass


def create_skill():
    return PingSkill()

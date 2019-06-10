import pprint

import requests
import subprocess
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
            .optionally("CommandKeyword").require("PingKeyword").require("NetworkNodeKeyword")\
            .require("key").build()
        self.register_intent(ping_intent, self.handle_ping_intent)

    def handle_ping_intent(self, message):
        hosts = dict()
        f = open(join(dirname(__file__), "hosts.txt"), 'r')
        for line in f.readlines():
            if line.startswith("#") or "," not in line:
                continue
            l = line.split(",")
            hosts[l[0].strip()] = [l[1].strip(), l[2].strip()]
        f.close()

        # this one with the key works for slightly parsable things like google.com
        k = message.data.get("key").lower()
        # but it does not work with spelled out names.
        # following seems like a bad hack, but message.data.get method
        # seems to omit the period and following.
        # k =  message.utterance_remainder().lower().strip()
        kk =  message.utterance_remainder().lower().strip()
        LOGGER.debug('==COMPARE=  k: ' + k + '  vs.  kk: ' + kk)
        # so double ugly hack: which one is longer?
        #   more likely to be the "right" content.
        #Yuck yuck yuck. TODO: FIX THIS
        if len(kk) > len(k):
            k = kk
        # more yuck: sometimes the "to " is left in...
        if k.startswith("to "):
            k = k[len("to "):]
        LOGGER.debug('k='+k)
        LOGGER.debug('   |__ from ' + str(message.data))
        LOGGER.debug('   "remainder":' + message.utterance_remainder() )
        LOGGER.debug(pprint.PrettyPrinter().pprint(message))
        LOGGER.info('Extracted network node key: ' + k)
        if len(k.strip()) < 1:
            ##hmm.. in recent testing seems like we never get here.
            ##consider modifying or dropping this.
            LOGGER.info("User either did not specify key, or we kind of missed it.")
            k = self.get_response("SpecifyNetworkNode")
        if k in hosts:
            if hosts[k][0] == '1':
                response = requests.get(hosts[k][1])
                data = {"response": response.reason.replace('OK', 'OKAY') +
                        " " + str(response.status_code)}
                self.speak_dialog("ServerResponse", data)
            else:
                status, result = subprocess.getstatusoutput("ping -c1 -w2 " +
                                hosts[k][1][(hosts[k][1]).find("//")+1:].replace('/', ''))
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
            # Internal aliasing/nicknames not matched,
            # Way too complex to parse spoken full URLs,
            # but maybe the user just uttered an "unregistered" but perfectly
            # valid DNS name so let's try normal public hierarchy resolution.
            # Just exit if keyword not found, and we don't get an easy clean
            # successful name resolution. Kind of best-effort, no guarantees.

            # When we are doing "real" ping we don't use URLs, just hostnames.
            # Mycroft normalization is pretty good already, however,
            # there will remain challenge that `slashdot.com` is difficult
            # to parse. A battle for another day.
            # Since normalization might break content a bit,
            # such as when "the" is actually part of domain name
            # we shall fall back to rough self-processing of "raw" utterance.

            LOGGER.debug(" k (key) before conditioning: " + k)
            k = k.replace("dot", ".").replace(" ", "").strip()
            # TODO: finally look for and replace close homophones for
            # for well known TLD strings$ occurring at end of utterance
            # TODO: is this a good time to set_context?

            LOGGER.debug("Trying for an ad-hoc DNS name key of " + k)
            status, result = subprocess.getstatusoutput("host " + k)
            # TODO: move ping-and-handle output into its own little function.
            if status == 0:
                status, result = subprocess.getstatusoutput("ping -c1 -w2 " + k)
                if status == 0:
                    data = {"response": result.split('/')[5]}
                    self.speak_dialog("PingResponse", data)
                else:
                    self.speak_dialog("PingFailure")
                    LOGGER.info(result)
                    result_message = result.lower().strip()
                    if result_message.startswith('ping:'):
                        result_message = result_message[5:]
                    if ('name' in result_message or 'dns' in result_message or
                            'unknown host' in result_message):
                        self.speak(result_message.replace(".", " dot "))
            else:
                self.speak_dialog("KeywordFailure")
                LOGGER.info("Requested network node alias not found "
                            "in hosts.txt registry. "
                            "Also name resolution failed: " + result)

    # Ping/ Server responses usually don't take more than 1 or 2 seconds at
    # most to register so there isn't much opportunity to stop the operation.
    def stop(self):
        pass


def create_skill():
    return PingSkill()

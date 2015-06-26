__author__ = 'MrMindImplosion'

# Ported from https://github.com/Taiiwo/IRCLinkBot/tree/master/plugins

from commands.base import Command, permissionLevels
from libs.cleverbot.cleverbot import Session

from urllib.parse import quote, unquote
import requests
import json
import re

# from shodan import WebAPI
# import socket

import random

from bs4 import BeautifulSoup

class cleverbot(Command):
    callname = "cb"
    permissionLevel = permissionLevels.NORMAL

    def __init__(self, engine):
        Command.__init__(self, engine)

        self.cleverbot = Session()

    def on_call(self, message, *args, **kwargs):
        if len(args) == 1:
            if args[0] == "START":
                return
            elif args[0] == "STOP":
                return

        query = " ".join(args)
        reply = self.cleverbot.Ask(query)
        self.bot.send_Reply(message, reply)

class findIP(Command):
    callname = "findip"
    permissionLevel = permissionLevels.NORMAL

    def on_call(self, message, *args, **kwargs):
        query = " ".join(args)

        #get link from slack wrappings
        #<http:/home.mrmindimplosion.co.uk|home.mrmindimplosion.co.uk>
        matches = re.search("(?<=//)[^\|/]*", query)
        print(matches)
        if matches:
            print(matches.group(0))
            self.on_call(message, matches.group(0))
            return

        query = quote(query)
        try:
            whois = requests.get('http://ip-api.com/json/' + query, {"fields": 65535})
            answ = json.loads(whois.text)
        except NotImplementedError: # Don't know which error to catch here
            self.bot.send_Reply(message, "API Error.")
            return

        try:
            if answ == False: # Closest I could find to checking for null
                self.bot.send_Reply(message, 'General JSON failure.')
                return
        except NotImplementedError: # don't know which error to catch here.
            pass        
        
        output = ""
        if answ['status']  == 'success':
                
            # prepare output     
            output += 'Lookup for IP: ' + answ['query'] + ' (' + answ['reverse'] + ')\n'
            output += 'ISP: ' + answ['isp'] + '(' + answ['org'] + ') - ' + answ['as'] + '\n'
            output += 'Country: ' + answ['country'] + ' (' + answ['countryCode'] + '); Time zone: ' + answ['timezone'] + '\n'
            output += 'Region: ' + answ['regionName'] + '(' + answ['region'] + ')' + '; City: ' + answ['city'] + '; zipcode: ' + answ['zip'] + '\n'
            output += 'Approx. location: ' + str(answ['lat']) + ' ' + str(answ['lon']) + '\n'
        else:
            output += 'Query "' + answ['query'] + '" has failed with errmsg: ' + answ['message']
        
        # output
        self.bot.send_Reply(message, output)

class FindPhone(Command):
    callname = "findphone"
    permissionLevel = permissionLevels.NORMAL
    
    def on_call(self, message, *args, **kwargs):
        try:
            number = args[0]
            if re.match('\d{9,11}', number):
                res = requests.get('https://api.opencnam.com/v2/phone/+' + str(number),
                                   {"format": "json",
                                    "account_sid": "ACe3213058aed64072b21c1aad690d10f5",
                                    "auth_token": "AU8d8f41d2a4ae42b09cd9356dc71db3b4"}
                                   )
                if res.text == "":
                    self.bot.send_Reply(message, "Phone number could not be found.\n \
                                                  (This command only seems to work with american numbers)")
                parsedjson = json.loads(res.text)

                tosend  = str(parsedjson['name']) + "\n"
                tosend += str(parsedjson['updated']) + "\n"
                tosend += str(parsedjson['price']) + "\n"
                tosend += str(parsedjson['created'])

                self.bot.send_Reply(message, tosend)
        except ValueError as a:
            print(a)

# shodan api is broken so this is disabled
# class LocateIP(Command):
#     callname = "locateip"
#     permissionLevel = permissionLevels.NORMAL
#
#     def on_call(self, message, *args, **kwargs):
#         try:#if shodan is installed (sudo pip install shodan)
#             api = WebAPI("KpYC07EoGBtGarTFXCpjsspMVQ0a5Aus")#don look
#             query = args[0]
#             socket.inet_aton(query)
#         except socket.error:
#             return None
#         results = api.host(query)
#         output = list()
#         output.append('OS: ' + str(results['os']))
#         output.append('City: ' + str(results['city']) + '\tPostal code: ' + str(results['postal_code']))
#         output.append('Area code: ' + str(results['area_code']) + '\t\tCountry code: ' + str(results['country_code']))
#         output.append('Region name: ' + str(results['region_name']) + '\tCountry name: ' + str(results['country_name']))
#         output.append('Latitude: ' + str(results['latitude']) + '\tLongitude: ' + str(results['longitude']))
#         ports = []
#         for data in results['data']:
#             port = data['port']
#             if not str(port) in ports:
#                 ports.append(str(port))
#         output.append('Open ports: ' + ', '.join(ports))
#
#         self.bot.send_Reply(message, "\n".join(output))

class Love(Command):
    callname = "love"
    permissionLevel = permissionLevels.NORMAL

    def on_call(self, message, *args, **kwargs):
        self.bot.send_Reply(message, 'I love ' + str(" ".join(args)))


class Moustache(Command):
    callname = "moustache"
    permissionLevel = permissionLevels.NORMAL

    def on_call(self, message, *args, **kwargs):

        res = requests.get("http://ajax.googleapis.com/ajax/services/search/images",
                           {
                               "v": "1.0",
                               "q": " ".join(args),
                               "start": 0
                           })
        images = json.loads(res.text)
        n = random.randint(0, len(images["responseData"]["results"]) - 1)
        image = images["responseData"]["results"][n]["url"]
        print(image)

        url = "https://mustachify.me/?src="+quote(image)
        self.bot.send_Reply(message, url)

class WolframAlpha(Command):
    callname = "wa"
    permissionLevel = permissionLevels.NORMAL

    def on_call(self, message, *args, **kwargs):
        query = {
                 'input': " ".join(args),
                 'appid': 'QPEPAR-TKWEJ3W7VA'
                }

        res = requests.get("http://api.wolframalpha.com/v2/query", query)
        soup = BeautifulSoup(res.text)
        pods = soup.find_all("pod")

        if pods and len(pods) >= 2:
            interp = pods[0].subpod.img["src"]
            answer = pods[1].subpod.img["src"]

            self.bot.send_Reply(message, "Interpretation: " + interp)
            self.bot.send_Reply(message, "Answer: " + answer)


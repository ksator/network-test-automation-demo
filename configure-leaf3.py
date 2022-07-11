"""
This scripts configure the leaf3 device
"""

import ssl
from argparse import ArgumentParser
from getpass import getpass
from jsonrpclib import Server

ssl._create_default_https_context = ssl._create_unverified_context

parser = ArgumentParser(description='Configure leaf3')
args = parser.parse_args()
args.password = getpass(prompt='Device password: ')

USERNAME = "arista"
# use the password of your ATD instance
PASSWORD = args.password
IP = "192.168.0.14"

print ('Configuring leaf3')
URL = "https://" + USERNAME + ":" + PASSWORD + "@" + IP + "/command-api"
switch = Server(URL)

with open('leaf3.conf','r', encoding='utf8') as f:
    conf_list = f.read().splitlines()

conf = switch.runCmds(version=1,cmds=conf_list, autoComplete=True)
print ('Done')

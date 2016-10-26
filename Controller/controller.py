# Basic wrapper to start process with any game that has proper interface.

from __future__ import print_function
from __future__ import division

import os
from subprocess import call


__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
prefix = os.path.join(__location__, "../../")

MARIO = "java -cp \"" + prefix + "MarioAI/MarioAI4J/bin;" + prefix + "MarioAI/MarioAI4J-Playground/bin;" + prefix + "MarioAI/MarioAI4J-Playground/lib/*\" mario.GeneralAgent"
GAME2048 = prefix + "2048/2048/bin/Debug/2048.exe"
ALHAMBRA = prefix + "general-ai/Game-interfaces/Alhambra/AlhambraInterface/AlhambraInterface/bin/Debug/AlhambraInterface.exe"

# TODO: Relative path
TORCS = "cmd.exe \"/C cd \"C:/Program Files (x86)/torcs\" & wtorcs.exe -r "
TORCS_XML = "\"" + prefix + "general-ai/Game-interfaces/TORCS/race_config.xml\""
TORCS_TIMEOUT = " & timeout 2 /nobreak"
TORCS_CLIENT = " & java -cp \"" + prefix + "general-ai/Game-interfaces/TORCS/scr-client/classes\" scr.Client scr.SimpleDriver port:3002\""


def start_torcs():
    command = TORCS + TORCS_XML + TORCS_TIMEOUT + TORCS_CLIENT
    print(command)
    call(command)

def start_mario():
    call(MARIO)

def start_2048():
    call(GAME2048)

def start_alhambra():
    call(ALHAMBRA)

#start_mario()
#start_2048()
#start_alhambra()
start_torcs()

print("Finished")

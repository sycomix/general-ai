"""
Some miscellaneous and useful functions that not belongs to some specific class.
"""
import json
import constants
import tensorflow as tf
import time
from games.alhambra import Alhambra
from games.torcs import Torcs
from games.mario import Mario
from games.game2048 import Game2048


def get_game_config(game_name):
    game_config_file = None
    if game_name == "2048":
        game_config_file = constants.GAME2048_CONFIG_FILE
    elif game_name == "alhambra":
        game_config_file = constants.ALHAMBRA_CONFIG_FILE
    elif game_name == "mario":
        game_config_file = constants.MARIO_CONFIG_FILE
    elif game_name == "torcs":
        game_config_file = constants.TORCS_CONFIG_FILE
    with open(game_config_file, "r") as f:
        game_config = json.load(f)
    return game_config


def get_game_instance(game_name, params, test=False):
    game_instance = None
    if game_name == "alhambra":
        game_instance = Alhambra(*params)
    if game_name == "2048":
        game_instance = Game2048(*params)
    if game_name == "torcs":
        game_instance = Torcs(*params, test=test)
    if game_name == "mario":
        game_instance = Mario(*params)
    return game_instance


def get_game_class(game_name):
    game_class = None
    if game_name == "alhambra":
        game_class = Alhambra
    if game_name == "2048":
        game_class = Game2048
    if game_name == "torcs":
        game_class = Torcs
    if game_name == "mario":
        game_class = Mario
    return game_class


def get_rnn_cell(cell_type):
    if cell_type == "lstm":
        return tf.nn.rnn_cell.BasicLSTMCell
    if cell_type == "gru":
        return tf.nn.rnn_cell.GRUCell


def get_elapsed_time(start):
    now = time.time()
    t = now - start
    h = t // 3600
    m = (t % 3600) // 60
    s = t - (h * 3600) - (m * 60)
    return f"{int(h)}h {int(m)}m {s}s"


def get_pretty_time():
    current = time.localtime()
    return f"{str(current.tm_year).zfill(2)}-{str(current.tm_mon).zfill(2)}-{str(current.tm_mday).zfill(2)}_{str(current.tm_hour).zfill(2)}-{str(current.tm_min).zfill(2)}-{str(current.tm_sec).zfill(2)}"

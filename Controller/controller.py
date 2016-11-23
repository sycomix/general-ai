# Basic wrapper to start process with any game that has proper interface.

from __future__ import print_function
from __future__ import division

import os
import time
import json
import numpy as np
import matplotlib.pyplot as plt
import concurrent.futures

from threading import Lock
from deap import creator, base, tools, algorithms

from games.alhambra import Alhambra
from games.torcs import Torcs
from games.mario import Mario
from games.game2048 import Game2048

np.random.seed(42)
loc = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
# prefix = Master directory
prefix = os.path.dirname(os.path.dirname(loc)) + "\\"  # cut two last directories

PYTHON_EXE = " \"C:\\Anaconda2\\envs\\py3k\\python.exe\""
PYTHON_SCRIPT = " \"" + prefix + "general-ai\\Controller\\script.py\""

MARIO = "java -cp \"" + prefix + "MarioAI\\MarioAI4J\\bin;" + prefix + "MarioAI\\MarioAI4J-Playground\\bin;" + prefix + "MarioAI\\MarioAI4J-Playground\\lib\\*\" mario.GeneralAgent"
GAME2048 = prefix + "2048\\2048\\bin\\Release\\2048.exe"
ALHAMBRA = prefix + "general-ai\\Game-interfaces\\Alhambra\\AlhambraInterface\\AlhambraInterface\\bin\\Release\\AlhambraInterface.exe"

TORCS = "\"" + prefix + "general-ai\\Game-interfaces\\TORCS\\torcs_starter.bat\""
TORCS_XML = " \"" + prefix + "general-ai\\Game-interfaces\\TORCS\\race_config.xml\""
TORCS_JAVA_CP = " \"" + prefix + "general-ai\\Game-interfaces\\TORCS\\scr-client\\classes;" + prefix + "general-ai\\Game-interfaces\\TORCS\\scr-client\\lib\\*\""
PORT = " \"3002\""
# TORCS_EXE_DIRECTORY = " \"C:\\Users\\Jan\\Desktop\\torcs\""  # TODO: Relative path via cmd parameter
TORCS_EXE_DIRECTORY = " \"C:\\Program Files (x86)\\torcs\""  # TODO: Relative path via cmd parameter

# config files for each game (contains I/O sizes)
GAME2048_CONFIG_FILE = prefix + "general-ai\\Game-interfaces\\2048\\2048_config.json"
ALHAMBRA_CONFIG_FILE = prefix + "general-ai\\Game-interfaces\\Alhambra\\Alhambra_config.json"
TORCS_CONFIG_FILE = prefix + "general-ai\\Game-interfaces\\TORCS\\TORCS_config.json"
MARIO_CONFIG_FILE = prefix + "general-ai\\Game-interfaces\\Mario\\Mario_config.json"

# commands used to run games
torcs_command = TORCS + TORCS_XML + TORCS_JAVA_CP + PORT + PYTHON_SCRIPT + TORCS_EXE_DIRECTORY + PYTHON_EXE
alhambra_command = ALHAMBRA + PYTHON_SCRIPT + PYTHON_EXE
game2048_command = GAME2048 + PYTHON_SCRIPT + PYTHON_EXE
mario_command = MARIO + PYTHON_SCRIPT + PYTHON_EXE


class IdGenerator():
    id = -1
    lock = Lock()

    @staticmethod
    def next_id():
        IdGenerator.lock.acquire()
        IdGenerator.id += 1
        to_return = IdGenerator.id
        IdGenerator.lock.release()
        return to_return


def get_number_of_weights(game_config_file, hidden_sizes):
    with open(game_config_file) as f:
        game_config = json.load(f)
        total_weights = 0
        for phase in range(game_config["game_phases"]):
            input_size = game_config["input_sizes"][phase]
            output_size = game_config["output_sizes"][phase]

            total_weights += input_size * hidden_sizes[0]
            if (len(hidden_sizes) > 1):
                for i in range(len(hidden_sizes) - 1):
                    total_weights += hidden_sizes[i] * hidden_sizes[i + 1]
            total_weights += hidden_sizes[-1] * output_size
    return total_weights


def eval_fitness(individual):
    id = IdGenerator.next_id()
    model_config_file = loc + "\\config\\feedforward" + str(id) + ".json"

    with open(model_config_file, "w") as f:
        data = {}
        data["model_name"] = "feedforward"
        data["class_name"] = "FeedForward"
        data["hidden_sizes"] = hidden_sizes
        data["weights"] = individual
        f.write(json.dumps(data))

    # game = Game2048(game2048_command + " \"" + model_config_file + "\"")
    # game = Alhambra(alhambra_command + " \"" + model_config_file + "\"")
    # game = Torcs(torcs_command + " \"" + model_config_file + "\"")
    game = Mario(mario_command + " \"" + model_config_file + "\"")
    result = game.run()
    os.remove(model_config_file)
    return result,


def mutRandom(individual, mutpb):
    for i in range(len(individual)):
        if (np.random.random() < mutpb):
            individual[i] = np.random.random()
    return individual,


def evolution_init(individual_len):
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()

    toolbox.register("attr_float", np.random.random)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=individual_len)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", eval_fitness)
    toolbox.register("mate", tools.cxUniform, indpb=0.5)
    toolbox.register("mutate", tools.mutGaussian, mu=0.5, sigma=0.05, indpb=0.05)
    # toolbox.register("mutate", mutRandom, mutpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=3)

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=16)
    toolbox.register("map", executor.map)
    return toolbox


if __name__ == '__main__':
    # game_config_file = GAME2048_CONFIG_FILE
    # game_config_file = ALHAMBRA_CONFIG_FILE
    # game_config_file = TORCS_CONFIG_FILE
    game_config_file = MARIO_CONFIG_FILE

    hidden_sizes = [16, 16]
    individual_len = get_number_of_weights(game_config_file, hidden_sizes)
    toolbox = evolution_init(individual_len)

    pop = toolbox.population(n=10)
    hof = tools.HallOfFame(4)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("min", np.min)
    stats.register("max", np.max)

    start = time.time()

    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.1, mutpb=0.3, ngen=150, stats=stats, halloffame=hof,
                                   verbose=True)

    end = time.time()
    print("Time: ", end - start)
    print("Best individual fitness: {}".format(hof[0].fitness.getValues()[0]))

    gen, avg, min_, max_ = log.select("gen", "avg", "min", "max")
    plt.plot(gen, avg, label="average")
    plt.plot(gen, min_, label="minimum")
    plt.plot(gen, max_, label="maximum")
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.legend(loc="lower right")
    plt.show()

"""
xml1 = " \"" + prefix + "general-ai\\Game-interfaces\\TORCS\\race_config_0.xml\""
xml2 = " \"" + prefix + "general-ai\\Game-interfaces\\TORCS\\race_config_1.xml\""
port1 = " \"3001\""
port2 = " \"3002\""

data = [(xml1, port1), (xml2, port2)]
import concurrent.futures
results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
    for i in range(100):
        game = Game2048(game2048_command + " \"" + model_config_file + "\"")
        future = executor.submit(game.run)
        results.append(future)

    for (xml, port) in data:
        torcs_command = TORCS + xml + TORCS_JAVA_CP + port + PYTHON_SCRIPT + TORCS_EXE_DIRECTORY + PYTHON_EXE
        print(torcs_command)
        game = Torcs(torcs_command + " \"" + model_config_file + "\"")
        future = executor.submit(game.run)
        results.append(future)

for i in range(len(results)):
    while not results[i].done():
        time.sleep(100)
    print(results[i].result())
"""

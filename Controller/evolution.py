from __future__ import print_function
from __future__ import division

import os
import json
from builtins import property

import numpy as np
import random
import concurrent.futures

import constants
import uuid
import time
import matplotlib.pyplot as plt

from deap import creator, base, tools, cma

from games.alhambra import Alhambra
from games.torcs import Torcs
from games.mario import Mario
from games.game2048 import Game2048


class Evolution():
    all_time_best = []

    def __init__(self, game, evolution_params, model_params, max_workers, logs_every=50):
        self.current_game = game
        self.evolution_params = evolution_params
        self.model_params = model_params
        self.max_workers = max_workers
        self.logs_every = logs_every

    def get_number_of_weights(self):
        """
        Evaluates number of parameters of neural networks (e.q. weights of network).
        :param hidden_sizes: Sizes of hidden fully-connected layers.
        :return: Numbre of parameters of neural network.
        """
        game_config_file = ""
        if self.current_game == "alhambra":
            game_config_file = constants.ALHAMBRA_CONFIG_FILE
        if self.current_game == "2048":
            game_config_file = constants.GAME2048_CONFIG_FILE
        if self.current_game == "mario":
            game_config_file = constants.MARIO_CONFIG_FILE
        if self.current_game == "torcs":
            game_config_file = constants.TORCS_CONFIG_FILE

        with open(game_config_file) as f:
            game_config = json.load(f)
            total_weights = 0
            h_sizes = self.model_params.hidden_layers
            for phase in range(game_config["game_phases"]):
                input_size = game_config["input_sizes"][phase] + 1
                output_size = game_config["output_sizes"][phase]
                total_weights += input_size * h_sizes[0]
                if (len(h_sizes) > 1):
                    for i in range(len(h_sizes) - 1):
                        total_weights += (h_sizes[i] + 1) * h_sizes[i + 1]
                total_weights += (h_sizes[-1] + 1) * output_size
        return total_weights

    def write_to_file(self, individual, filename):
        """
        Writes individual to file for logging purposes.
        :param individual: Individual to log.
        :param filename: Filename where to write.
        """
        with open(filename, "w") as f:
            data = {}
            data["model_name"] = "feedforward"
            data["class_name"] = "FeedForward"
            data["hidden_sizes"] = self.model_params.hidden_layers
            data["weights"] = individual
            data["activation"] = self.model_params.activation
            f.write(json.dumps(data))

    def eval_fitness(self, individual, seed):
        """
        Evaluates a fitness of the specified individual.
        :param individual: Individual whose fitness will be evaluated.
        :param seed: Seed for the game instance.
        :return: Fitness of the individual (must be tuple for Deap library).
        """
        id = uuid.uuid4()
        model_config_file = self.dir + "\\tmp\\feedforward_" + str(id) + ".json"
        self.write_to_file(individual, model_config_file)

        game = ""
        params = [model_config_file, self.evolution_params._game_batch_size, seed]

        if self.current_game == "alhambra":
            game = Alhambra(*params)
        if self.current_game == "2048":
            game = Game2048(*params)
        if self.current_game == "mario":
            game = Mario(*params)
        if self.current_game == "torcs":
            game = Torcs(*params)

        result = game.run()
        try:
            os.remove(model_config_file)
        except IOError:
            print("Failed attempt to delete config file (leaving file non-deleted).")

        return result,

    def mut_random(self, individual, mutindpb):
        """
        Provides random mutation of a individual.
        :param individual: Individual to mutate.
        :param mutindpb: Probability of mutation for single "bit" of individual.
        :return: New mutated individual.
        """
        for i in range(len(individual)):
            if (np.random.random() < mutindpb):
                individual[i] = np.random.random()
        return individual,

    def init_individual(self, icls, length, content=None):
        if content == None:
            return icls([np.random.random() for _ in range(length)])
        return icls(content)

    def init_population(self, pop_size, container, ind_init, file_name=None):
        if file_name == None:
            return container(ind_init() for _ in range(pop_size))

        with open(file_name) as f:
            content = json.load(f)
            return container(ind_init(content=x) for x in content["population"])

    def deap_toolbox_init(self):
        """
        Initializes the current instance of evolution.
        :returns: Deap toolbox.
        """
        individual_len = self.get_number_of_weights()

        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        toolbox = base.Toolbox()
        toolbox.register("attr_float", np.random.random)
        toolbox.register("individual", self.init_individual, length=individual_len, icls=creator.Individual)
        toolbox.register("population", self.init_population, container=list, ind_init=toolbox.individual)

        toolbox.register("evaluate", self.eval_fitness)
        toolbox.register("mate", tools.cxUniform, indpb=self.evolution_params.cxindpb)

        mut_name = self.evolution_params.mut[0]
        if mut_name == "uniform":
            toolbox.register("mutate", self.mut_random, mutindpb=self.evolution_params.mut[2])
        else:
            raise NotImplementedError
            # toolbox.register("mutate", tools.mutGaussian, mu=0.5, sigma=0.05, indpb=0.05)

        sel = self.evolution_params.selection[0]
        if sel == "tournament":
            toolbox.register("select", tools.selTournament, tournsize=self.evolution_params.selection[1])
        elif sel == "selbest":
            toolbox.register("select", tools.selBest)
        else:
            raise NotImplementedError

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        toolbox.register("map", executor.map)
        return toolbox

    def create_log_files(self, dir, pop, log, elapsed_time):
        if not os.path.exists(dir):
            os.makedirs(dir)

        with open((dir + "\\pop.json"), "w") as f:
            data = {}
            data["population"] = pop
            f.write(json.dumps(data))

        with open((dir + "\\logbook.txt"), "w") as f:
            f.write(str(log))

        with open((dir + "\\settings.json"), "w") as f:
            data = {}
            data["evolution_params"] = self.evolution_params.to_dict()
            data["model_params"] = self.model_params.to_dict()
            f.write(json.dumps(data))

        with open((dir + "\\runtime.txt"), "w") as f:
            f.write("{}".format(elapsed_time))

        gen, avg, min_, max_ = log.select("gen", "avg", "min", "max")
        plt.figure()
        plt.plot(gen, avg, label="avg")
        plt.plot(gen, min_, label="min")
        plt.plot(gen, max_, label="max")
        i = np.argmax(avg)
        plt.scatter(gen[i], avg[i])
        plt.text(gen[i], avg[i], "{}".format(round(max(avg), 2)))
        plt.xlabel("Generation")
        plt.ylabel("Fitness")
        plt.xlim([0, len(gen)])
        plt.legend(loc="lower right")
        plt.title("GAME: {}\n{}\n{}".format(self.current_game, self.evolution_params.to_string(),
                                            self.model_params.to_string()), fontsize=10)
        plt.savefig(dir + "\\plot.jpg")

    def init_directories(self):
        self.dir = constants.loc + "\\config\\" + self.current_game + "\\" + self.model_params.name
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
        if not os.path.exists(self.dir + "\\tmp"):
            os.makedirs(self.dir + "\\tmp")

        # create name for directory to store logs
        current = time.localtime()
        t_string = str(current.tm_year).zfill(2) + "-" + \
                   str(current.tm_mon).zfill(2) + "-" + \
                   str(current.tm_mday).zfill(2) + "_" + \
                   str(current.tm_hour).zfill(2) + "-" + \
                   str(current.tm_min).zfill(2) + "-" + \
                   str(current.tm_sec).zfill(2)

        return self.dir + "\\logs_" + t_string

    def log_all(self, logs_dir, population, hof, logbook, start_time):
        """
        Creates all logs of the current state of evolution.
        :param logs_dir: Logging directory.
        :param population: Population to log.
        :param hof: Hall of fame to log (can be None).
        :param logbook: Logbook info (from deap lib).
        :param start_time: Start time of evolution.
        """
        t = time.time() - start_time
        h = t // 3600
        m = (t % 3600) // 60
        s = t - (h * 3600) - (m * 60)
        elapsed_time = "{}h {}m {}s".format(int(h), int(m), s)

        self.create_log_files(logs_dir, population, logbook, elapsed_time)
        print("Time elapsed: {}".format(elapsed_time))

        best_dir = logs_dir + "/best"
        last_dir = logs_dir + "/last"

        if not os.path.exists(best_dir):
            os.makedirs(best_dir)
        if not os.path.exists(last_dir):
            os.makedirs(last_dir)

        number_to_log = max(self.evolution_params.hof_size, self.evolution_params.elite)
        for i in range(number_to_log):
            self.write_to_file(population[i], last_dir + "\\last_" + str(i) + ".json")
            self.all_time_best.append(population[i])

        self.all_time_best.sort(key=lambda ind: ind.fitness.values, reverse=True)
        self.all_time_best = self.all_time_best[:number_to_log]

        for i in range(number_to_log):
            self.write_to_file(self.all_time_best[i], best_dir + "\\best_" + str(i) + ".json")

    def start_simple_ea(self):
        """
        Starts simple evolution algorithm.
        """
        start_time = time.time()

        logs_dir = self.init_directories()

        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("min", np.min)
        stats.register("max", np.max)

        toolbox = self.deap_toolbox_init()
        population = toolbox.population(pop_size=self.evolution_params.pop_size)

        logbook = tools.Logbook()
        logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

        if (self.evolution_params.hof_size > 0):
            halloffame = tools.HallOfFame(self.evolution_params.hof_size)
        else:
            halloffame = None

        # invalid_ind = [ind for ind in population if not ind.fitness.valid]
        invalid_ind = population
        seeds = [np.random.randint(0, 2 ** 16) for _ in range(len(invalid_ind))]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind, seeds)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        if halloffame is not None:
            halloffame.update(population)

        record = stats.compile(population) if stats else {}
        logbook.record(gen=0, nevals=str(len(invalid_ind)), **record)

        print(logbook.stream)
        population.sort(key=lambda ind: ind.fitness.values, reverse=True)

        # Begin the generational process
        for gen in range(1, self.evolution_params.ngen + 1):

            # Select the next generation individuals
            offspring = toolbox.select(population, len(population) - self.evolution_params.elite)
            offspring = [toolbox.clone(ind) for ind in offspring]

            # Apply crossover and mutation on the offspring
            for i in range(1, len(offspring), 2):
                if np.random.random() < self.evolution_params.cxpb:
                    offspring[i - 1], offspring[i] = toolbox.mate(offspring[i - 1], offspring[i])
                    del offspring[i - 1].fitness.values, offspring[i].fitness.values

            for i in range(len(offspring)):
                if np.random.random() < self.evolution_params.mut[1]:
                    offspring[i], = toolbox.mutate(offspring[i])
                    del offspring[i].fitness.values

            # Add elite individuals (they lived through mutation and x-over)
            for i in range(self.evolution_params.elite):
                offspring.append(toolbox.clone(population[i]))

            # invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            invalid_ind = offspring
            seeds = [np.random.randint(0, 2 ** 16) for _ in range(len(invalid_ind))]
            fitnesses = toolbox.map(toolbox.evaluate, invalid_ind, seeds)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            # Update the hall of fame with the generated individuals
            if halloffame is not None:
                halloffame.update(offspring)

            # Replace the current population by the offspring
            population[:] = offspring
            population.sort(key=lambda ind: ind.fitness.values, reverse=True)

            # Append the current generation statistics to the logbook
            record = stats.compile(population) if stats else {}
            logbook.record(gen=gen, nevals=str(len(invalid_ind)), **record)

            print(logbook.stream)

            if (gen % self.logs_every == 0):
                self.log_all(logs_dir, population, halloffame, logbook, start_time)

        self.log_all(logs_dir, population, halloffame, logbook, start_time)

        return population, logbook

    def start_evolution_strategy(self):
        """
        Starts evolution strategy (CMA-ES).
        """

        start_time = time.time()
        logs_dir = self.init_directories()

        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("min", np.min)
        stats.register("max", np.max)

        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        toolbox = base.Toolbox()
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        toolbox.register("map", executor.map)
        toolbox.register("evaluate", self.eval_fitness)

        logbook = tools.Logbook()
        logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

        N = self.get_number_of_weights()
        print("N: {}".format(N))
        strategy = cma.Strategy(centroid=[0.0] * N, sigma=self.evolution_params.sigma,
                                lambda_=self.evolution_params.pop_size)
        print("CMA strategy created ({} s)".format(time.time() - start_time))
        toolbox.register("generate", strategy.generate, creator.Individual)
        toolbox.register("update", strategy.update)

        if (self.evolution_params.hof_size > 0):
            hof = tools.HallOfFame(self.evolution_params.hof_size)
        else:
            hof = None

        print("ES Started")
        for gen in range(1, self.evolution_params.ngen + 1):

            # Generate a new population
            population = toolbox.generate()

            # Evaluate the individuals
            seeds = [np.random.randint(0, 2 ** 16) for _ in range(len(population))]
            fitnesses = toolbox.map(toolbox.evaluate, population, seeds)
            for ind, fit in zip(population, fitnesses):
                ind.fitness.values = fit

            if hof is not None:
                hof.update(population)

            print("Updating population...")
            st = time.time()
            # Update the strategy with the evaluated individuals
            toolbox.update(population)
            print("Population updated ({} s)".format(time.time() - st))

            record = stats.compile(population) if stats is not None else {}
            logbook.record(gen=gen, nevals=len(population), **record)
            print(logbook.stream)

            if (gen % self.logs_every == 0):
                self.log_all(logs_dir, population, hof, logbook, start_time)

        self.log_all(logs_dir, population, hof, logbook, start_time)
        print("ES Complete")

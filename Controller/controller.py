# Basic wrapper to start process with any game that has proper interface.
from __future__ import division
from __future__ import print_function

import random
import numpy as np

from evolution.differential_evolution import DifferentialEvolution
from evolution.evolution_parameters import EvolutionaryAlgorithmParameters, EvolutionStrategyParameters, \
    DifferentialEvolutionParameters
from evolution.evolution_strategy import EvolutionStrategy
from evolution.evolutionary_algorithm import EvolutionaryAlgorithm
from models.echo_state_network import EchoState
from models.mlp import MLP
from reinforcement.ddpg.ddpg_reinforcement import DDPGReinforcement
from reinforcement.reinforcement_parameters import DDPGParameters, DQNParameters
from reinforcement.dqn.dqn import DQN

MASTER_SEED = 42
random.seed(MASTER_SEED)
np.random.seed(MASTER_SEED)


def run_eva(game):
    eva_parameters = EvolutionaryAlgorithmParameters(
        pop_size=25,
        cxpb=0.2,
        mut=("uniform", 0.05, 0.5),
        ngen=1000,
        game_batch_size=10,
        cxindpb=0.1,
        hof_size=0,
        elite=5,
        selection=("tournament", 3))

    mlp = MLP(hidden_layers=[100, 100], activation="relu")
    # esn = EchoState(n_readout=32, n_components=256, output_layers=[], activation="relu")
    evolution = EvolutionaryAlgorithm(game=game, evolution_params=eva_parameters, model=mlp, logs_every=100,
                                      max_workers=4)
    evolution.run()


def run_ddpg(game):
    ddpg_parameters = DDPGParameters(
        batch_size=100,
        episodes=500,
        test_size=1)

    RL = DDPGReinforcement(game=game, parameters=ddpg_parameters, logs_every=5)
    RL.run()


def run_es(game):
    strategy_parameters = EvolutionStrategyParameters(
        pop_size=25,
        ngen=5000,
        game_batch_size=10,
        hof_size=0,
        elite=5,
        sigma=5.0)

    mlp = MLP(hidden_layers=[32, 32], activation="relu")
    # esn = EchoState(n_readout=32, n_components=256, output_layers=[], activation="relu")
    strategy = EvolutionStrategy(game, strategy_parameters, mlp, logs_every=10, max_workers=5)
    strategy.run()


def run_de(game):
    diff_evolution_parameters = DifferentialEvolutionParameters(
        pop_size=25,
        ngen=5000,
        game_batch_size=50,
        hof_size=5,
        cr=0.25,
        f=1)

    mlp = MLP(hidden_layers=[256, 256], activation="relu")
    diff = DifferentialEvolution(game, diff_evolution_parameters, mlp, max_workers=5, logs_every=5)
    diff.run()


def run_dqn(game):
    parameters = DQNParameters(batch_size=100,
                               init_exp=0.9,
                               final_exp=0.01,
                               anneal_steps=1000000,
                               replay_buffer_size=10000,
                               store_replay_every=1,
                               discount_factor=0.9,
                               target_update_frequency=500,
                               reg_param=0.01,
                               double_q_learning=False,
                               test_size=100)

    optimizer_params = {}
    optimizer_params["name"] = "adam"
    optimizer_params["learning_rate"] = 0.01

    q_network_parameters = {}
    q_network_parameters["hidden_layers"] = [500, 500]
    q_network_parameters["activation"] = "relu"
    q_network_parameters["dropout"] = None

    RL = DQN(game, parameters, q_network_parameters, optimizer_params, test_every=100)
    RL.run()


if __name__ == '__main__':
    game = "mario"

    # run_greedy(game)
    # run_ddpg(game)
    # run_es(game)
    run_eva(game)
    # run_de(game)
    # run_dqn(game)

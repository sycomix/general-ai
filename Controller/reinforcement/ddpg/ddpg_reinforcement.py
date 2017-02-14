from  reinforcement.ddpg.filter_env import *
from reinforcement.ddpg.ddpg_agent import DDPGAgent
from reinforcement.environment import Environment
from reinforcement.reinforcement import Reinforcement
import utils.miscellaneous
import tensorflow as tf
import gc
import os
import numpy as np
import constants
import time
import json

gc.enable()


class DDPGReinforcement(Reinforcement):
    """
    Represents a DDPG model.
    """

    def __init__(self, game, parameters, logs_every=10):
        """
        Initializes a new DDPG model using specified parameters.
        :param game: Game that will be played.
        :param parameters: Parameters of the model. (DDPGParameters)
        :param logs_every: At each n-th episode model will be saved.
        """
        self.game = game
        self.parameters = parameters
        self.episodes = parameters.episodes
        self.batch_size = parameters.batch_size
        self.game_config = utils.miscellaneous.get_game_config(game)
        self.game_class = utils.miscellaneous.get_game_class(game)
        self.state_size = self.game_config["input_sizes"][0]  # inputs for all phases are the same in our games
        self.logs_every = logs_every
        self.checkpoint_name = "ddpg.ckpt"

        self.actions_count = self.game_config["output_sizes"]
        self.actions_count_sum = sum(self.actions_count)
        self.logdir = self.init_directories(dir_name="deep_deterministic_policy_gradient")

        # DDPG (deep deterministic gradient policy)
        self.agent = DDPGAgent(self.batch_size, self.state_size, self.actions_count_sum, self.logdir)

    def log_metadata(self):
        """
        Saves model metadata into a logdir.
        """
        with open(os.path.join(self.logdir, "metadata.json"), "w") as f:
            data = {}
            data["model_name"] = "reinforcement_learning_ddpg"
            data["game"] = self.game
            data["parameters"] = self.parameters.to_dictionary()
            f.write(json.dumps(data))

    def run(self):
        """
        Starts an evaluation of DDPG model.
        """
        self.log_metadata()

        start = time.time()
        data = []
        for episode in range(self.episodes):

            self.env = Environment(game_class=self.game_class,
                                   seed=np.random.randint(0, 2 ** 16),
                                   observations_count=self.state_size,
                                   actions_in_phases=self.actions_count)
            state = self.env.state
            for step in range(100000):
                action = self.agent.play(state, episode)
                next_state, reward, done, score = self.env.step(action)
                score = score[0]
                self.agent.perceive(state, action, reward, next_state, done)
                state = next_state
                if done:
                    break

            report_measures = ([tf.Summary.Value(tag='score', simple_value=score),
                                tf.Summary.Value(tag='number_of_steps', simple_value=step)])
            self.agent.summary_writer.add_summary(tf.Summary(value=report_measures), episode)

            if episode % self.logs_every == 0:
                checkpoint_path = os.path.join(self.logdir, self.checkpoint_name)
                self.agent.saver.save(self.agent.sess, checkpoint_path)
                with open(os.path.join(self.logdir, "logbook.txt"), "w") as f:
                    for line in data:
                        f.write(line)
                        f.write('\n')

            elapsed_time = utils.miscellaneous.get_elapsed_time(start)
            line = "Episode {}/{}, Score: {}, Steps: {}, Total Time: {}".format(episode, self.episodes, score, step,
                                                                                elapsed_time)
            print(line)
            data.append(line)

        self.env.close()

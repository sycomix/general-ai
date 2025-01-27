from games.abstract_game import AbstractGame
import subprocess
import json
import numpy as np
from threading import Lock
from constants import *
import platform


class Torcs(AbstractGame):
    MAX_NUMBER_OF_TORCS_PORTS = 10

    master_lock = Lock()
    port_locks = [Lock() for _ in range(MAX_NUMBER_OF_TORCS_PORTS)]
    ddpg_wrong_ports = []

    def __init__(self, model, game_batch_size, seed, vis_on=False, test=False):
        """
        Initializes a new instance of TORCS game.
        :param model: Model which will be playing this game.
        :param game_batch_size: Number of games that will be played immediately (one after one) within the single game
        instance. Result is averaged.
        :param seed: A random seed for random generator within the game.
        :param vis_on: Determines whether TORCS will run with visual output. If True, different subprocess will be used.
        :param test: Indicates whether the game is in testing mode. Using different track.
        """
        super(Torcs, self).__init__()
        self.model = model
        self.game_batch_size = game_batch_size
        self.seed = seed
        self.test = test
        self.vis_on = vis_on

    def run(self, advanced_results=False):
        """
        Starts a single TORCS game.
        :return: TORCS game result (passed distance for example).
        """
        avg_result = 0
        for _ in range(self.game_batch_size):
            state, current_phase = self.init_process()
            while True:
                result = self.model.evaluate(state, current_phase)

                state, current_phase, _, done = self.step(result)
                if done:
                    avg_result += self.score
                    break

        avg_result = avg_result / float(self.game_batch_size)
        return [avg_result] if advanced_results else avg_result

    def init_process(self):
        """
        Initializes a new process with TORCS game. Maximum 10 process at time (maximum 10 ports that are available for
        TORCS).
        """
        Torcs.master_lock.acquire()

        index = np.random.randint(Torcs.MAX_NUMBER_OF_TORCS_PORTS)
        self.my_port_lock = Torcs.port_locks[index]
        for i in range(len(Torcs.port_locks)):
            port_number = 3001 + i # torcs ports are between 3001 and 3010
            if port_number in self.ddpg_wrong_ports:
                print("Using different port...")
                continue
            if not Torcs.port_locks[i].locked():
                self.my_port_lock = Torcs.port_locks[i]
                index = i
                break
            if i == len(Torcs.port_locks) - 1:
                print("All ports have been locked...")

        self.my_port_lock.acquire()
        Torcs.master_lock.release()

        port_num = 3001 + index
        self.current_port = port_num
        xml = " \"" + prefix + "general-ai/Game-interfaces/TORCS/race_config_" + str(port_num) + ".xml\""

        if self.test:
            # For testing purposes, we use different track:
            port_num = 3010
            xml = " \"" + prefix + "general-ai/Game-interfaces/TORCS/race_config_3010_test.xml\""

        port = " \"" + str(port_num) + "\""

        with open(TORCS_INSTALL_DIRECTORY_REF, "r") as f:
            torcs_install_dir = f.readline()

        windows = platform.system() == "Windows"
        if not windows:
            raise NotImplementedError("TORCS is supported only on Windows at the moment.")

        if self.vis_on:
            params = [TORCS_VIS_ON_BAT, xml, TORCS_JAVA_CP, port, torcs_install_dir]
        else:
            params = [TORCS_BAT, xml, TORCS_JAVA_CP, port, torcs_install_dir]
        command = "{} {} {} {} {}".format(*params)
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=-1)

        data = self.get_process_data()
        return data["state"], data["current_phase"]

    def get_process_data(self):
        """
        Gets a subprocess next data (line).
        :return: a subprocess next data (line).
        """
        line = ' '
        while line[0] != "{":
            # Not a proper json
            line = self.process.stdout.readline().decode('ascii')

        return json.loads(line)

    def finalize(self, internal_error=False):
        """
        Finalizes the game subprocess. Releases used locks and kills the subprocess.
        :return:
        """
        try:
            if internal_error:
                print(f"Unreleased port: {self.current_port}")
                self.ddpg_wrong_ports.append(self.current_port)
            else:
                self.my_port_lock.release()
        except:
            pass

        self.process.kill()

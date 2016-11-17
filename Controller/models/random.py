from models.model import Model
import numpy as np

class Random(Model):

    def evaluate(self, input):
        game_phases = int(self.game_config["game_phases"])
        input_sizes = list(map(int, self.game_config["input_sizes"]))
        output_sizes = list(map(int, self.game_config["output_sizes"]))
        curr_phase = int(input["current_phase"])

        assert (input_sizes[curr_phase] == len(input["state"]))

        result = ""
        for i in range(output_sizes[curr_phase]):
            result += str(np.random.random())
            if (i < output_sizes[curr_phase] - 1):
                result += " "

        return result
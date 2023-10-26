class GreedyPolicyParameters():
    """
    Encapsulates parameters of for reinforcement learning.
    """

    @staticmethod
    def from_dict(data):
        return GreedyPolicyParameters(
            data["batch_size"],
            data["episodes"],
            data["gamma"],
            data["optimizer"],
            data["epsilon"],
            data["test_size"],
            data["learning_rate"],
        )

    def __init__(self,
                 batch_size,
                 episodes,
                 gamma,
                 optimizer,
                 epsilon,
                 test_size,
                 learning_rate=0.001):
        self.batch_size = batch_size
        self.episodes = episodes
        self.gamma = gamma
        self.optimizer = optimizer
        self.epsilon = epsilon
        self.test_size = test_size
        self.learning_rate = learning_rate

    def to_dictionary(self):
        return {
            "batch_size": self.batch_size,
            "episodes": self.episodes,
            "gamma": self.gamma,
            "optimizer": self.optimizer,
            "epsilon": self.epsilon,
            "test_size": self.test_size,
            "learning_rate": self.learning_rate,
        }

    def to_string(self):
        return f"gamma: {self.gamma}, optimizer: {self.optimizer}, learning rate: {self.learning_rate}, epsilon: {self.epsilon}, batch_size: {self.batch_size}, episodes: {self.episodes}, test_size: {self.test_size}"


class DDPGParameters():
    """
    Encapsulates parameters of for reinforcement learning.
    """

    @staticmethod
    def from_dict(data):
        return DDPGParameters(
            data["batch_size"],
            data["replay_buffer_size"],
            data["discount_factor"],
            data["episodes"],
            data["test_size"],
        )

    def __init__(self,
                 batch_size,
                 replay_buffer_size,
                 discount_factor,
                 episodes,
                 test_size):
        self.batch_size = batch_size
        self.episodes = episodes
        self.replay_buffer_size = replay_buffer_size
        self.discount_factor = discount_factor
        self.test_size = test_size

    def to_dictionary(self):
        return {
            "batch_size": self.batch_size,
            "replay_buffer_size": self.replay_buffer_size,
            "discount_factor": self.discount_factor,
            "episodes": self.episodes,
            "test_size": self.test_size,
        }

    def to_string(self):
        return f"batch_size: {self.batch_size}, replay_buffer_size: {self.replay_buffer_size}, discount_factor: {self.discount_factor}, test_size: {self.test_size}"


class DQNParameters():
    """
    Encapsulates parameters fo DQN reinforcement learning.
    """

    @staticmethod
    def from_dict(data):
        return DQNParameters(
            data["batch_size"],
            data["init_exp"],
            data["final_exp"],
            data["anneal_steps"],
            data["replay_buffer_size"],
            data["store_replay_every"],
            data["discount_factor"],
            data["target_update_frequency"],
            data["reg_param"],
            data["double_q_learning"],
            data["test_size"],
        )

    def __init__(self,
                 batch_size,
                 init_exp=0.5,  # initial exploration prob
                 final_exp=0.1,  # final exploration prob
                 anneal_steps=10000,  # N steps for annealing exploration
                 replay_buffer_size=10000,
                 store_replay_every=5,  # how frequent to store experience
                 discount_factor=0.9,  # discount future rewards
                 target_update_frequency=1000,
                 reg_param=0.01,  # regularization constants
                 double_q_learning=False,
                 test_size=100):
        self.batch_size = batch_size
        self.init_exp = init_exp
        self.final_exp = final_exp
        self.anneal_steps = anneal_steps
        self.replay_buffer_size = replay_buffer_size
        self.store_replay_every = store_replay_every
        self.discount_factor = discount_factor
        self.target_update_frequency = target_update_frequency
        self.reg_param = reg_param
        self.double_q_learning = double_q_learning
        self.test_size = test_size

    def to_dictionary(self):
        return {
            "batch_size": self.batch_size,
            "init_exp": self.init_exp,
            "final_exp": self.final_exp,
            "anneal_steps": self.anneal_steps,
            "replay_buffer_size": self.replay_buffer_size,
            "store_replay_every": self.store_replay_every,
            "discount_factor": self.discount_factor,
            "target_update_frequency": self.target_update_frequency,
            "reg_param": self.reg_param,
            "double_q_learning": self.double_q_learning,
            "test_size": self.test_size,
        }

    def to_string(self):
        return f"batch_size: {self.batch_size}, init_exp: {self.init_exp}, final_exp: {self.final_exp}, final_exp: {self.final_exp}, replay_buffer_size: {self.replay_buffer_size}, store_replay_every: {self.store_replay_every}. discount_factor: {self.discount_factor}, target_update_frequency: {self.target_update_frequency}, reg_param: {self.reg_param}, double_q_learning: {self.double_q_learning}"

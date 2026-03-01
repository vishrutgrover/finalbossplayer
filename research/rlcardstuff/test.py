import rlcard
from rlcard.agents import DQNAgent
from rlcard.utils import set_global_seed, tournament
from rlcard.utils import Logger

env = rlcard.make('limit-holdem', config={'seed': 0})
eval_env = rlcard.make('limit-holdem', config={'seed': 0})

set_global_seed(0)

agent = DQNAgent(scope='dqn', action_num=env.action_num, replay_memory_size=50000, update_target_estimator_every=1000, discount_factor=0.99, epsilon_start=1.0, epsilon_end=0.1, epsilon_decay_steps=20000, batch_size=32, train_every=1, mlp_layers=[64,64])
env.set_agents([agent, agent])

log_dir = './experiments/limit_holdem_dqn_result/'
logger = Logger(log_dir)

for episode in range(10000):
    trajectories, payoffs = env.run(is_training=True)
    agent.feed(trajectories)
    if episode % 100 == 0:
        logger.log_performance(env.tournament(eval_env, 1000)[0])

logger.close_files()
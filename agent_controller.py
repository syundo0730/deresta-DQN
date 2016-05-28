from cnn_dqn_agent import CnnDqnAgent
import argparse

parser = argparse.ArgumentParser(description='ml-agent-for-deresta')
parser.add_argument('--gpu', '-g', default=-1, type=int, help='GPU ID (negative value indicates CPU)')
args = parser.parse_args()


class AgentController:
    def __init__(self):
        self.agent = CnnDqnAgent()
        self.agent_initialized = False
        self.cycle_counter = 0
        self.log_file = 'reward.log'
        self.reward_sum = 0
        # press, up, down, left, right, none
        self.commands = ["none", "none", "none", "none", "none"]

    def get_commands(self):
        return self.commands

    def set_commands_from_action(self, action):
        command_candidate = ["press", "up", "down", "right", "left", "none"]
        self.commands = [command_candidate[a] for a in action]

    def update(self, message):
        image = message["image"]
        pad_states = message["pad_states"]
        end_episode = message['end_episode']
        observation = {"image": image, "pad_states": pad_states}
        reward = message['reward']

        if not self.agent_initialized:
            self.agent_initialized = True
            print ("initializing agent......")
            self.agent.agent_init(use_gpu=args.gpu, pad_states_dim=len(pad_states))

            action = self.agent.agent_start(observation)
            self.set_commands_from_action(action)
            with open(self.log_file, 'w') as the_file:
                the_file.write('cycle, episode_reward_sum \n')
        else:
            self.cycle_counter += 1
            self.reward_sum += reward

            if end_episode:
                self.agent.agent_end(reward)
                with open(self.log_file, 'a') as the_file:
                    the_file.write(str(self.cycle_counter) +
                                   ',' + str(self.reward_sum) + '\n')
                self.reward_sum = 0
            else:
                action, eps, q_now, obs_array = self.agent.agent_step(reward, observation)
                self.set_commands_from_action(action)
                self.agent.agent_step_update(reward, action, eps, q_now, obs_array)

# -*- coding: utf-8 -*-

from cnn_dqn_agent import CnnDqnAgent
from deresta_score_service import ScoreEvaluator, NotesLoader
import cv2
import argparse

parser = argparse.ArgumentParser(description='ml-agent-for-deresta')
parser.add_argument('--gpu', '-g', default=-1, type=int, help='GPU ID (negative value indicates CPU)')
args = parser.parse_args()
windowname = "CinderellaStage"

class Game:
    def __init__(self):
        self.capture = cv2.VideoCapture('anzu.mp4')
        self.width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)

        cv2.namedWindow(windowname, cv2.WINDOW_NORMAL)

        notes_array = NotesLoader(195, 4590).load("cm_anzu_master.json")
        self.evaluator = ScoreEvaluator(notes_array)

    def __del__(self):
        self.capture.release()
        cv2.destroyAllWindows()
        cv2.destroyAllWindows()

    def start(self, player):
        while True:
            if self.capture.isOpened():
                # capture frame
                ret, frame = self.capture.read()
                if not ret:
                    break
                time = self.capture.get(cv2.CAP_PROP_POS_MSEC)
                print("Time ms: %d" % time)
                self.update(frame, time, player, False)
                cv2.imshow(windowname, frame)
            else:
                self.update(None, 0, player, True)

    def update(self, frame, time, player, end_episode):
        if frame is not None:
            self.evaluator.update(player.get_commands(), time)
            scores = self.evaluator.get_scores()
            self.draw_scores(frame, scores)
            resized_frame = cv2.resize(frame, (227, 227))

        player.update(
            {"reward": sum(scores),
             "image": resized_frame,
             "pad_states": self.evaluator.get_pad_states(),
             "end_episode": end_episode})

    def draw_scores(self, frame, scores):
        # constants
        w_center = self.width * 0.5
        interval = self.width / 6.5
        pos_x_1 = int(w_center - interval * 2)
        pos_x_2 = int(w_center - interval)
        pos_x_3 = int(w_center)
        pos_x_4 = int(w_center + interval)
        pos_x_5 = int(w_center + interval * 2)
        pos_y = int(self.height - 60)
        radius = 40
        color = (0, 255, 255)
        line_width = 3
        type = 4

        if scores[0] is not 0:
            cv2.circle(frame, (pos_x_1, pos_y), radius, color, line_width, type)
        if scores[1] is not 0:
            cv2.circle(frame, (pos_x_2, pos_y), radius, color, line_width, type)
        if scores[2] is not 0:
            cv2.circle(frame, (pos_x_3, pos_y), radius, color, line_width, type)
        if scores[3] is not 0:
            cv2.circle(frame, (pos_x_4, pos_y), radius, color, line_width, type)
        if scores[4] is not 0:
            cv2.circle(frame, (pos_x_5, pos_y), radius, color, line_width, type)

class Player:
    def __init__(self):
        self.agent = CnnDqnAgent()
        self.agent_initialized = False
        self.cycle_counter = 0
        self.log_file = 'reward.log'
        self.reward_sum = 0
        self.commands = ["none", "none", "none", "none", "none"]

    def get_commands(self):
        return self.commands

    def set_commands_from_action(self, action):
        self.commands = ["press", "press", "press", "press", "press"]

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

            return action
        else:
            self.cycle_counter += 1
            self.reward_sum += reward

            if end_episode:
                self.agent.agent_end(reward)
                action = self.agent.agent_start(observation)  # TODO
                self.set_commands_from_action(action)
                with open(self.log_file, 'a') as the_file:
                    the_file.write(str(self.cycle_counter) +
                                   ',' + str(self.reward_sum) + '\n')
                self.reward_sum = 0
                return action
            else:
                action, eps, q_now, obs_array = self.agent.agent_step(reward, observation)
                self.set_commands_from_action(action)
                self.agent.agent_step_update(reward, action, eps, q_now, obs_array)
                return action

if __name__ == "__main__":
    game = Game()
    player = Player()
    game.start(player)
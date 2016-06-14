import cv2
import numpy as np


class GameViewer():
    def __init__(self, video_file_name):
        self.video_file_name = video_file_name
        self.capture = None
        self.width = 0
        self.height = 0
        self.enabled = True
        self.window_name = "CinderellaStage"
        self.frame_num = 0
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)

    def __del__(self):
        self.capture.release()
        cv2.destroyAllWindows()

    def init(self):
        if self.capture is not None and self.capture.isOpened():
            self.capture.release()
        self.capture = cv2.VideoCapture(self.video_file_name)
        self.width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.frame_num = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)

    def read(self):
        if self.capture is not None and self.capture.isOpened():
            ret, frame = self.capture.read()
            if not ret:
                return None, 0, True
            time = self.capture.get(cv2.CAP_PROP_POS_MSEC)
            frame_pos = self.capture.get(cv2.CAP_PROP_POS_FRAMES)
            return frame, time, (frame_pos == self.frame_num-1)
        else:
            return None, 0, True

    def show(self, frame, command, score):
        self.draw_action(frame, command, score)
        cv2.imshow(self.window_name, frame)

    def draw_action(self, frame, commands, scores):
        w_center = self.width * 0.5
        interval = self.width / 6.5
        pos_x_1 = int(w_center - interval * 2)
        pos_x_2 = int(w_center - interval)
        pos_x_3 = int(w_center)
        pos_x_4 = int(w_center + interval)
        pos_x_5 = int(w_center + interval * 2)
        pos_y = int(self.height - self.height / 6.0)

        self.draw_command(frame, (pos_x_1, pos_y), commands[0], scores[0])
        self.draw_command(frame, (pos_x_2, pos_y), commands[1], scores[1])
        self.draw_command(frame, (pos_x_3, pos_y), commands[2], scores[2])
        self.draw_command(frame, (pos_x_4, pos_y), commands[3], scores[3])
        self.draw_command(frame, (pos_x_5, pos_y), commands[4], scores[4])

    def draw_command(self, frame, pos, command, score):
        # BGR
        blue = (255, 0, 0)
        red = (0, 0, 255)
        yellow = (0, 255, 255)
        black = (0, 0, 0)
        if command == "press":
            cv2.circle(frame, pos, 40, yellow, 3, 4)
        if command == "up":
            cv2.circle(frame, pos, 40, red, 3, 4)
        if command == "down":
            cv2.circle(frame, pos, 40, blue, 3, 4)
        if command == "left":
            cv2.fillConvexPoly(
                frame,
                np.array([[pos[0]-30, pos[1]], [pos[0]+30, pos[1]+30], [pos[0]+30, pos[1]-30]]),
                yellow)
        if command == "right":
            cv2.fillConvexPoly(
                frame,
                np.array([[pos[0]+30, pos[1]], [pos[0]-30, pos[1]-30], [pos[0]-30, pos[1]+30]]),
                yellow)
        cv2.putText(frame, str(score), (pos[0], pos[1] - 40), cv2.FONT_HERSHEY_PLAIN, 2, black, 2)


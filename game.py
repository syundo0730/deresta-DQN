from deresta_score_service import ScoreEvaluator, NotesLoader
from game_viewer import GameViewer
import cv2


class Game:
    def __init__(self, note_file_name, video_file_name, bpm, offset):
        self.play_time = 10
        self.game_viewer = GameViewer(video_file_name)
        notes_array = NotesLoader(bpm, offset).load(note_file_name)
        self.evaluator = ScoreEvaluator(notes_array)

    def init_game(self):
        self.evaluator.reset()
        self.game_viewer.init()

    def start(self, player):
        # Run game {play_time} times
        for i in range(self.play_time):
            self.init_game()
            # Start game
            while True:
                print("Game: {0}".format(i+1))
                frame, time, is_last = self.game_viewer.read()
                if frame is None:
                    break

                if is_last:
                    pass
                self.update(frame, time, player, is_last)

    def update(self, frame, time, player, end_episode):
        commands = player.get_commands()
        self.evaluator.update(commands, time)
        scores = self.evaluator.get_scores()

        self.game_viewer.show(frame, commands, scores)

        player.update(
            {"reward": sum(scores),
             "image": cv2.resize(frame, (227, 227)),
             "pad_states": self.evaluator.get_pad_states(),
             "end_episode": end_episode})


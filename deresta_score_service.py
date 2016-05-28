# -*- coding:utf-8 -*-
import json


class ScoreEvaluator:
    def __init__(self, notes_array):
        self.pad_states = [PadState(notes) for notes in notes_array]
        self.time = 0
        self.commands = ["none", "none", "none", "none", "none"]

    def reset(self):
        # reset all pad states
        for pad in self.pad_states:
            pad.reset()
        self.time = 0
        self.commands = ["none", "none", "none", "none", "none"]

    def update(self, commands, time):
        self.commands = commands
        self.time = time
        for (pad_state, command) in zip(self.pad_states, self.commands):
            pad_state.update(command, self.time)

    def get_scores(self):
        return [pad_state.get_score(command, self.time) for (pad_state, command) in zip(self.pad_states, self.commands)]

    def get_pad_states(self):
        return [1 if pad_state.is_pressed else 0 for pad_state in self.pad_states]

class PadState:
    def __init__(self, notes):
        self.hit_note = HitNote(notes)
        self.is_pressed = False

    def reset(self):
        self.hit_note.index = 0
        self.is_pressed = False

    def update(self, command, time):
        self.hit_note.update(time)
        self.update_press_state(command)

    def update_press_state(self, command):
        if command == "up":
            self.is_pressed = False
        elif command == "down":
            self.is_pressed = True
        elif command == "none":
            pass
        else:
            self.is_pressed = False

    def get_score(self, command, timestamp):
        note = self.hit_note.get_note()

        if note.start - 100.0 <= timestamp <= note.start:
            if note.is_type_normal():
                if command == "press":
                    return 20.0
                if command == "left" or command == "right":
                    return 10.0
            elif note.is_type_slide():
                if note.direction == "R" and command == "right":
                    return 20.0
                if note.direction == "L" and command == "left":
                    return 20.0
                if command == "press" or command == "right" or command == "left":
                    return 10.0
            elif note.is_type_long():
                if not self.is_pressed and command == "down":
                    return 20.0

        if note.end - 100.0 <= timestamp <= note.end:
            if note.is_type_long():
                if self.is_pressed:
                    if note.direction == "":
                        if command == "up":
                            return 20.0
                        if command == "right" or command == "left":
                            return 10.0
                    if note.direction == "R":
                        if command == "right":
                            return 20.0
                        if command == "up" or command == "left":
                            return 10.0
                    if note.direction == "L":
                        if command == "left":
                            return 20.0
                        if command == "up" or command == "right":
                            return 10.0
        if note.start + 100.0 <= timestamp <= note.end - 100.0:
            if note.is_type_long():
                if self.is_pressed:
                    if command == "none":
                        return 10.0
                    else:
                        return -10.0

        return 0

class HitNote:
    def __init__(self, notes):
        self.notes = notes
        self.notes_len = len(notes)
        self.index = 0

    def update(self, time):
        while True:
            if self.index == self.notes_len - 1:
                break
            elif time > (self.notes[self.index].end + self.notes[self.index+1].start) * 0.5:
                self.index += 1
            else:
                break

    def get_note(self):
        return self.notes[self.index]

class Note:
    def __init__(self, type, position, start, end, direction):
        self.type = type
        self.position = position
        self.start = start
        self.end = end
        self.direction = direction
    def is_type_normal(self):
        return self.type == "normal"
    def is_type_long(self):
        return self.type == "long"
    def is_type_slide(self):
        return self.type == "slide"
    def __repr__(self):
        return "Note(%s, %s, %s, %s, %s)" % (self.type, self.position, self.start, self.end, self.direction)
    def __str__(self):
        return "{type: %s, position: %s, start: %s, end: %s, direction: %s}" % (self.type, self.position, self.start, self.end, self.direction)

class NotesLoader:
    def __init__(self, bpm, offset):
        self.bpm = bpm
        self.offset = offset

    def load(self, filename):
        file = open(filename)
        data = file.read()
        file.close()
        data_as_dic = json.loads(data)
        sorted_notes_array = []
        for pos in range(1, 6):
            normal = self.load_normal_note(data_as_dic, pos)
            long = self.load_long_note(data_as_dic, pos)
            slide = self.load_slide_note(data_as_dic, pos)
            sorted_notes = sorted(normal + long + slide, key=lambda x: x.start)
            sorted_notes_array.append(sorted_notes)
        return sorted_notes_array

    def beat_as_ms(self, time):
        return self.offset + 60000.0 * time / self.bpm

    def load_normal_note(self, dic, pos):
        data = dic["notes"]
        notes = []
        for note in data:
            time = self.beat_as_ms(note[0])
            position = note[1]
            if pos == position:
                notes.append(Note("normal", position, time, time, ""))
        return notes

    def load_long_note(self, dic, pos):
        data = dic["long"]
        notes = []
        for note in data:
            start = self.beat_as_ms(note[0])
            end = self.beat_as_ms(note[1])
            position = note[2]
            direction = note[3]
            if pos == position:
                notes.append(Note("long", position, start, end, direction))
        return notes

    def load_slide_note(self, dic, pos):
        data = dic["slide"]
        notes = []
        for slide in data:
            for note in slide:
                time = self.beat_as_ms(note[0])
                position = note[1]
                direction = note[2]
                if pos == position:
                    notes.append(Note("slide", position, time, time, direction))
        return notes

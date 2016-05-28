# -*- coding: utf-8 -*-


from game import Game
from agent_controller import AgentController

if __name__ == "__main__":
    game = Game()
    agent_controller = AgentController()
    game.start(agent_controller)


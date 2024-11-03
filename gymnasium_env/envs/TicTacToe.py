"""
TicTacToe is considered a multiagent game,in order to make it single agent
the O player will be follwoing random strategie and the X is the one that 
have to learn (this sound incovinient but this is all i can see rn)
"""

from ...TicTacToe_interface import TicTacToeGame

import gymnasium as gym
from gymnasium import spaces

import pygame
import numpy as np


class TicTacToeEnv(gym.Env):
    metadata = {
        'render_modes':["human","rgb_array"],
        'render_fps':4
    }

    def __init__(self,render_mode=None,size=3,strategies = None):

        #initialse a tictactoe game
        self.game = TicTacToeGame(strategies=strategies) #random strategy by default for both X and O
        
        self.size = size # The size of the square grid
        self.window_size = 512 # The size of the PyGame window

        #Observations are dictionnaries with the two players states
        self.observation_space = spaces.Dict(
            {
                "Player_X":spaces.Discrete(start=0,n=2**9-1),
                "Player_O":spaces.Discrete(start=0,n=2**9-1),
            }
        )
        self.player_x_state = self.game.players[1].state.get()
        self.player_o_state = self.game.players[0].state.get()

        #We have 9 possible actions
        self.action_space = spaces.Discrete(9)

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        """
        If human-rendering is used, `self.window` will be a reference
        to the window that we draw to. `self.clock` will be a clock that is used
        to ensure that the environment is rendered at the correct framerate in
        human-mode. They will remain `None` until human-mode is used for the
        first time.
        """
        self.window = None
        self.clock = None

    def _get_obs(self):
        return {"Player_X": self.player_x_state, "Player_O": self.player_o_state}
    
    def _get_info(self):
        #We can get some info as a dict
        return None

    def reset(self,seed=None):
        # We need the following line to seed self.np_random
        super().reset(seed=seed)

        self.game.reset()

        observation = self._get_obs()
        info = self._get_info()

        return observation,info

    def step(self,action=None):
        """
        This contains most of the logic of the game

        * Since player.O is our agent, x will always play randomly and then O plays

        (We can add a parameter speciying the strategies 'self.startegie')
        """

        #X will play a random move ( We can improve it's strategy so that O learns better )
        self.game.move(player='O') #move according to self.game.strategies['O']
        
        #now it's our agent O turn
        self.game.move(player='X') #move according to self.game.strategies['X']

        observation = self._get_obs()
        reward = self.game.get_reward()
        terminated = self.game.is_done()
        truncated = False
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, terminated, truncated, info
    
    def render(self):
        if self.render_mode == "rgb_array":
            return self._render_frame()

    def _render_frame(self):
        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode(
                (self.window_size, self.window_size)
            )
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        canvas = pygame.Surface((self.window_size, self.window_size))
        canvas.fill((255, 255, 255))
        pix_square_size = (
            self.window_size / self.size
        )  # The size of a single grid square in pixels

        x_positions = self.game.get_positions(self.game.players[1].state.get())
        o_positions = self.game.get_positions(self.game.players[0].state.get())

        #Function to draw X
        def draw_X(canvas=canvas, x_positions=x_positions, color=(255, 0, 0), line_width=5):
            """Draws an 'X' in the specified grid square."""
            for row,col in x_positions:
                x_start = col * pix_square_size
                y_start = row * pix_square_size
                x_end = x_start + pix_square_size
                y_end = y_start + pix_square_size

                # Draw the two lines for the 'X'
                pygame.draw.line(canvas, color, (x_start, y_start), (x_end, y_end), line_width)
                pygame.draw.line(canvas, color, (x_start, y_end), (x_end, y_start), line_width)

        #Function to draw O
        def draw_O(canvas=canvas, o_positions=o_positions, color=(255, 0, 0), line_width=5):
            """Draws an 'O' in the specified grid square."""
            for row,col in o_positions:
                x_center = col * pix_square_size + pix_square_size / 2
                y_center = row * pix_square_size + pix_square_size / 2
                radius = pix_square_size / 2 - line_width  # Adjust radius so it fits within the square

                # Draw the circle for the 'O'
                pygame.draw.circle(canvas, color, (int(x_center), int(y_center)), int(radius), line_width)

        # We draw the grid with Xs and Os
        draw_X()
        draw_O()

        # Finally, add some gridlines
        for x in range(self.size + 1):
            pygame.draw.line(
                canvas,
                0,
                (0, pix_square_size * x),
                (self.window_size, pix_square_size * x),
                width=3,
            )
            pygame.draw.line(
                canvas,
                0,
                (pix_square_size * x, 0),
                (pix_square_size * x, self.window_size),
                width=3,
            )

        if self.render_mode == "human":
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            self.clock.tick(self.metadata["render_fps"])
        else:  # rgb_array
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
            )
        
    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
        

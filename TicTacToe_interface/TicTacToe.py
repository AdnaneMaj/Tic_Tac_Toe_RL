# Credit of this code goes to : JAMOR Moussa .Link : https://github.com/JamorMoussa/Tic-Tac-Toe-Reinforcement-Learning/blob/main/tic_env/tic_game.py

from enum import Enum 
from typing import Dict
from copy import deepcopy

from .strategies import Strategy

class PlayerId(Enum):
    X: int = 1
    O: int = -1 


class State:

    WIN_STATES_LIST = [
            0b000000111, 0b000111000, 0b111000000,  # rows
            0b001001001, 0b010010010, 0b100100100,  # columns
            0b100010001, 0b001010100  # diagonals
        ]

    def __init__(self, state: int):
        self._state: int = state  #A number reprenting a state among the 2**9=19683

    def set(self, state: int):
        self._state = state 

    def get(self) -> int:
        return self._state 
    
    @staticmethod
    def reset():
        return State(state= 0b000000000)
    
    @staticmethod
    def draw_state():
        return State(state=0b111111111)

    @classmethod
    def win_states(cls):
        return list(map(lambda state: State(state=state), cls.WIN_STATES_LIST)) #transform the win_states_list to a list of State objects

    def __repr__(self):
        return f"<state: id={self._state}>"


class Player:

    def __init__(self, id: PlayerId, state: State):

        self.state: State = state 
        self.id: PlayerId = id
        self.old_state = deepcopy(self.state)

    def move(self, action: int):
        action -= 1
        self.old_state = deepcopy(self.state)
        self.state = State(state= (self.state.get() | (1 << action)))

    def undo(self):
        self.state = deepcopy(self.old_state)

    def __repr__(self):
        return f"<Player: id={self.id}>"


class BoardState:

    def __init__(self, players: list[Player]):
        
        self.players: list[Player] = players

    def get_state(self):
        return State(state= (self.players[0].state.get() | self.players[1].state.get()))

    def allowed_actions(self):

        return [
            (action + 1) for action in range(0, 9) 
            if ((1 << action) & self.get_state().get() == State.reset().get())        
        ]


class TicTacToeGame:

    def __init__(self, cur_player_id: PlayerId = None,strategies: Dict[str] = None):
        
        self.cur_player_id: PlayerId = PlayerId.X if cur_player_id == None else cur_player_id #player X is starting by default
        self.strategies = {"X":"random","O":"random"} if strategies == None else strategies #Set the players strategies

        self.reset()

    def reset(self):

        self.players: list[Player] = [
            Player(
                id= PlayerId.O, state= State.reset()
            ),
            Player(
                id= PlayerId.X, state= State.reset()
            )
        ]

        self.board_state: BoardState = BoardState(players=self.players) 

    @property
    def cur_player(self) -> Player:
        return self.players[(self.cur_player_id.value + 1)//2] #-1 : O and 1 : X

    def change_player(self):
        self.cur_player_id = PlayerId(self.cur_player_id.value * -1)

    def undo_action(self):
        self.change_player()
        self.cur_player.undo()

    def is_winner(self, player: Player):
        for win in State.win_states():
            if (player.state.get() & win.get()) == win.get():
                return True
        return False

    def is_draw(self, board_state: BoardState):
        return board_state.get_state().get() == State.draw_state().get() 

    def get_reward(self):

        if self.is_winner(player=self.players[0]): # O wins
            return 1

        elif self.is_winner(player=self.players[1]): # X wins
            return -2

        elif self.is_draw(board_state=self.board_state):
            return -1
        
        else: return 0 

    def is_done(self):

        return (
            any(self.is_winner(player) for player in self.players) or self.is_draw(self.board_state)
        )

    def get_allowed_actions(self):
        return self.board_state.allowed_actions()
    
    def move(self,player:str='O',action:int = None):
        
        if action==None:
            action = Strategy(strategy=self.strategies[player]).get_action(self.get_allowed_actions())

        player_index = 0 if player=='O' else 1
        self.players[player_index].move(action=action)

    def get_positions(n):
        # Ensure the input number is in the valid range and convert it to a 9-bit binary string
        binary_string = f"{n:09b}"

        # List to store the positions of "X"s
        positions = []

        # Iterate over each bit in the binary string
        for i, bit in enumerate(binary_string):
            if bit == '1':  # If the bit is 1, it's an "X"
                # Calculate row and column based on the index
                row = i // 3
                col = i % 3
                positions.append((row, col))
    
        return positions


    def render(self):
        # TODO: change this implimentation it's weird.

        board = {}
        for i in range(1, 10):
            if (self.players[0].state.get() & (1 << (i-1))) == (1 << (i-1)):
                board[i] = " X "
            elif (self.players[1].state.get() & (1 << (i-1))) == (1 << (i-1)):
                board[i] = " O "
            else:
                board[i] = f"   "
        
        map_repr = ""
        line = "+---+---+---+\n"
        map_repr += line
        for i in range(3):
            map_repr += f"|{board[3*i+1]}|{board[3*i+2]}|{board[3*i+3]}|\n"
            map_repr += line
        print(map_repr)
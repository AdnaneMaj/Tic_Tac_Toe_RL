from typing import List
import random

class Strategy:
    def __init__(self,strategy:str = None):
        self.strategy = 'random' if strategy==None else strategy
        self.strategies_func = {'random':self.random_strategy}

    def random_strategy(self,possible_actions:List[int]):
        return random.choice[possible_actions]

    def get_action(self,*args,**kwargs):
        return self.strategies_func[self.strategy](*args,**kwargs)
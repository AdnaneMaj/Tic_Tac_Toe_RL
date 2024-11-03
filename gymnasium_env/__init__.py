from gymnasium.envs.registration import register

register(
    id="gymnasium_env/TicTacToe-v0",
    entry_point="gymnasium_env.envs:TicTacToeEnv",
)
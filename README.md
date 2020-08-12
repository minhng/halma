# halma

An A.I agent that plays Halma, a more complex variation of Chinese Checkers on a 16x16 gameboard.

To win the game, a player needs to transfer all of their 19 pieces from their starting corner to the opposite corner, into the positions that were initially occupied by the opponent. The rule of the game is subject to preventing spoiling. 2 teams switch sides after each game.

Total time available for my agent to play the whole game is 600 seconds/game. My agent played 9 full games against minimax agent with depth 3 and won 8 out of 9 games.

Strategies deployed to win within given time: a) alpha/beta pruning, b) precomputed the optimized state that gets all pieces out of zone with least moves c) only considered moves that move toward opponent's zone

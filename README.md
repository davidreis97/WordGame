# WordGame

## Game Rules

This is a 2-player turn-based word game where the user plays against the computer. Each player says a letter on their turn, the first to form a complete word wins.

## Computer

The CPU tries to choose letters that prevent the player from winning and match words that allow it to win. For example, if the current word is "r", and it's the CPU move, it might consider playing the letter "e" in order to form the word "read" in its next turn. However, as the player can play a "d" after the CPU plays "e" and form the word "red", the CPU will not make that move and will instead find another word to form. 
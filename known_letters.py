from typing import Tuple
import common

class KnownLetters:
    def __init__(self, guess_tables: Tuple[str, str]):
        self.included_letters = []
        self.excluded_letters = []
        self.unknown = []
        self.__process(guess_tables)

    def __process(self, guess_tables: Tuple[str, str]) -> None:
        for t in guess_tables:
            word = t[0].strip().lower()
            guess = t[1].strip()

            if len(word) != len(guess):
                raise Exception(f'Guess mask must match word length (word `{word}`)')

            for i in range(len(word)):
                letter = word[i]
                mask = guess[i]

                if mask == common.CHAR_NOT_FOUND:
                    self.__add_excluded(letter)
                elif mask == common.CHAR_FOUND or mask == common.CHAR_WRONG_POSITION:
                    self.__add_included(letter)
                else:
                    self.unknown.append(letter)

    def __add_included(self, letter: str) -> None:
        letter = letter[0]
        if letter not in self.included_letters:
            self.included_letters.append(letter)

    def __add_excluded(self, letter: str) -> None:
        letter = letter[0]
        if letter not in self.included_letters and \
           letter not in self.excluded_letters:
            self.excluded_letters.append(letter)

import re
import sys
from typing import List, Pattern


class PositionTable:
    def __init__(self, letter: str, positions: List[bool]):
        self.letter: str = letter[0]
        self.can_be_at_position: List[bool] = positions

    def can_be_located_at_pos(self, position: int) -> bool:
        if position > len(self.can_be_at_position):
            raise Exception(f'Positions table don\'t have enough positions `{self}`[{position}]')
            return False

        return self.can_be_at_position[position]

    def set_false(self, position: int) -> None:
        self.can_be_at_position[position] = False

    def __str__(self):
        repr = ''.join(['+' if can_be else '-' for can_be in self.can_be_at_position])
        return f'{self.letter}: `{repr}`'

    def __repr__(self):
        return self.__str__()


class PositionTablesList:
    def __init__(self, word_length: int):
        self.tables: List[PositionTable] = []

        if word_length < 1:
            raise Exception('Word length must be greater than 0')

        self.__word_length = word_length

    def get_for(self, letter: str) -> PositionTable:
        letter = letter[0].lower()

        for t in self.tables:
            if t.letter == letter:
                return t

        result = PositionTable(letter, [True] * self.__word_length)
        self.tables.append(result)
        return result

    def update_for(self, letter: str, mask: str, pos: int) -> PositionTable:
        expected_can_be_at_position = False if mask[0] == '-' else True

        letter = letter[0].lower()
        existing = self.get_for(letter)

        if expected_can_be_at_position:
            return existing

        actual_can_be_at_position = existing.can_be_located_at_pos(pos)
        if actual_can_be_at_position and mask[0] == '-':
            existing.set_false(pos)
            return existing

        return existing


def main(lang: str, \
         word_length: int, \
         mask: str, \
         excluded_words: List[str], \
         included_letters: str, \
         guess_masks: List[str]) -> None:
    filename = f'wordlist_{lang}_{word_length}.txt.'
    
    regex = __build_regex(mask)
    excluded_letters = __build_excluded_letters_from(included_letters, excluded_words)
    positions_tables = __build_position_tables(excluded_words, guess_masks, word_length)

    with open(filename, 'r', encoding='utf-8') as f:
        words = f.readlines()
        words = [w.strip() for w in words]

    with open('output.txt', 'w', encoding='utf-8') as f:
        for word in words:

            g = regex.match(word)
            if not g:
                #log_exit('Word mask')
                continue
            
            result = g.group(0)

            def log_exit(phase: str) -> None:
                #print(f'Word: {word}, exit on phase {phase}')
                pass

            stop_condition_meet = False
            for excluded_letter in excluded_letters:
                if excluded_letter in result:
                    stop_condition_meet = True
                    break

            if stop_condition_meet:
                log_exit('Excluded letter found')
                continue

            for included_letter in included_letters:
                if included_letter not in result:
                    stop_condition_meet = True
                    break

            if stop_condition_meet:
                log_exit('Included letter not found')
                continue

            for excluded_word in excluded_words:
                if len(excluded_word.strip()) > 0 and word.startswith(excluded_word):
                    stop_condition_meet = True
                    break

            if stop_condition_meet:
                log_exit('Excluded word')
                continue

            for pos in range(len(word)):
                letter = word[pos]
                can_be_at_position = positions_tables.get_for(letter).can_be_located_at_pos(pos)
                if not can_be_at_position:
                    stop_condition_meet = True
                    break

            if stop_condition_meet:
                log_exit('Letter can\'t be at position')
                continue

            f.write(f'{result}\n')

    with open('output.txt', 'r', encoding='utf-8') as f:
        text = f.read()
        print(text)

    print(f'info: Excluded letters: {excluded_letters}')


def __build_regex(mask: str) -> Pattern[str]:
    # mask = mask.replace('?', '[a-zA-Z]')
    return re.compile(mask)


def __build_excluded_letters_from(included_letters: str, excluded_words: str) -> str:
    charset = [letter for letter in included_letters]
    result: List[str] = []

    for excluded_word in excluded_words:
        for letter in excluded_word:
            if letter not in charset and letter not in result:
                result.append(letter)

    return ''.join(result)


def __build_position_tables(excluded_words: List[str], guess_masks: List[str], words_length: int) -> PositionTablesList:
    result: PositionTablesList = PositionTablesList(words_length)

    if len(excluded_words) != len(guess_masks):
        raise Exception('Define guess mask for each of the excluded words')

    zipped = tuple(zip(excluded_words, guess_masks))
    for word_wordmask in zipped:
        word = word_wordmask[0]
        wordmask = word_wordmask[1]

        data = tuple(zip(word, wordmask))
        for position in range(len(data)):
            letter = data[position][0]
            mask = data[position][1]

            result.update_for(letter, mask, position)

    return result


def __get_pos_arg(pos: int, default, name: str):
    if pos < 0:
        raise ValueError('Unable to fetch argument on negative position')

    if len(sys.argv) - 1 < pos:
        if default is None:
            raise ValueError(f'Positional argument `{name}` not found on position `{pos}`')
        else:
            return default
        
    return sys.argv[pos]


if __name__ == "__main__":

    try:
        lang = __get_pos_arg(1, None, "Language")
        mask = __get_pos_arg(2, None, "Mask")
        included_letters = __get_pos_arg(3, "", "Included Letters")
        excluded_words = __get_pos_arg(4, "", "Excluded words").split(',')
        guess_mask = __get_pos_arg(5, "", "Guess mask").split(',')
        length = int(__get_pos_arg(6, 5, "Expected length"))

        main(lang, length, mask, excluded_words, included_letters, guess_mask) 
    except Exception as e:
        print(e)


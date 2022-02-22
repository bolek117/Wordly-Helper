import json
import re
import sys
from typing import List, Pattern


# TODO: auto known letters based on guess patterns


class PositionTable:
    def __init__(self, letter: str, positions: List[bool]):
        self.letter: str = letter[0]
        self.can_be_at_position: str = positions

    def can_be_located_at_pos(self, position: int) -> bool:
        if position > len(self.can_be_at_position):
            raise Exception(f'Positions table don\'t have enough positions `{self}`[{position}]')
            return False

        return self.can_be_at_position[position] != '-'

    def __set_at_pos(self, pos: int, value: str) -> None:
        as_list = list(self.can_be_at_position)
        as_list[pos] = value[0]
        self.can_be_at_position = ''.join(as_list)

    def set_by_guess(self, position: int, mask: str) -> None:
        mask = mask.strip()
        if len(mask) != 1:
            raise Exception('Mask have to be only on character')

        if mask == '-' or \
           (mask == '+' and self.can_be_at_position[position] != '-') or \
           (mask == '?' and self.can_be_at_position[position] not in ['-', '+']):
           self.__set_at_pos(position, mask)

    def __str__(self):
        repr = ''.join(['+' if mask != '-' else '-' for mask in self.can_be_at_position])
        return f'{self.letter}: `{repr}`'

    def __repr__(self):
        return self.__str__()


class PositionTablesList:
    def __init__(self, word_length: int):
        self.tables: List[PositionTable] = []

        if word_length < 1:
            raise Exception('Word length must be greater than 0')

        self.word_length = word_length

    def get_for(self, letter: str) -> PositionTable:
        letter = letter[0].lower()

        for t in self.tables:
            if t.letter == letter:
                return t

        result = PositionTable(letter, '?' * self.word_length)
        self.tables.append(result)
        return result

    def update_for(self, letter: str, mask: str, pos: int) -> PositionTable:
        letter = letter[0].lower()
        existing = self.get_for(letter)
        existing.set_by_guess(pos, mask)
        return existing


def main(lang: str, \
         word_length: int, \
         excluded_words: List[str], \
         included_letters: str, \
         guess_masks: List[str]) -> None:
    filename = f'wordlist_{lang}_{word_length}.txt.'
    
    excluded_letters = __build_excluded_letters_from(included_letters, excluded_words)
    positions_tables = __build_position_tables(excluded_words, guess_masks, word_length)
    regex = __build_regex(positions_tables)

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
                table = positions_tables.get_for(letter)
                can_be_at_position = table.can_be_located_at_pos(pos)
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

    print(f'INFO Excluded letters: {excluded_letters}')

    found_words = len(text.split('\n'))
    print(f'INFO Found words: {found_words}')


def __build_regex(position_tables: PositionTablesList) -> Pattern[str]:
    result = ['.'] * position_tables.word_length
    for table in position_tables.tables:
        guess_mask = table.can_be_at_position
        letter = table.letter
        
        for i in range(0, len(guess_mask)):
            if guess_mask[i] == '+':
                result[i] = letter

    result = ''.join(result)
    return re.compile(''.join(result))


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


if __name__ == "__main__":
    # TODO: Generate known words automatically
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
        
    try:
        lang = config['lang']
        known_letters = config['knownLetters']
        used_words = config['usedWords'].split(',')
        guess_masks = config['guessMasks'].split(',')
        length = int(config['length'])

        main(lang, length, used_words, known_letters, guess_masks) 
    except Exception as e:
        print(e)


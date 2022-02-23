import json
import re
from typing import List, Pattern, Tuple

# TODO: Optimize guess masks by replacing removing one `?` when match (`+`) is found
class PositionTable:
    __default_character = ' '
    
    def __init__(self, letter: str, positions: List[bool]):
        self.letter: str = letter[0]
        self.position_mask: List[str] = positions
        self.__modified: bool = False

    def can_be_located_at_pos(self, position: int) -> bool:
        if position > len(self.position_mask):
            raise Exception(f'Positions table don\'t have enough positions `{self}`[{position}]')

        return self.position_mask[position] not in ['-', '?']

    def __set_at_pos(self, pos: int, mask: str) -> None:
        self.position_mask[pos] = mask[0]
        self.__modified = True

    def set_by_guess(self, position: int, mask: str) -> None:
        mask = mask.strip()
        if len(mask) != 1:
            raise Exception('Mask have to be only on character')
        
        if mask == '-' or \
           (mask == '+' and self.position_mask[position] != '-') or \
           (mask == '?' and self.position_mask[position] not in ['-', '+']):
           self.__set_at_pos(position, mask)

    def set_not_found(self) -> None:
        for i in range(len(self.position_mask)):
            if self.position_mask[i] not in ['?', '+']:
                self.position_mask[i] = '-' 

    @staticmethod
    def default_for(letter: str, length: int):
        return PositionTable(letter, [PositionTable.__default_character] * length)

    def __str__(self):
        repr = ''.join(self.position_mask)
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

        result = PositionTable.default_for(letter, self.word_length)
        self.tables.append(result)
        return result

    def update_for(self, letter: str, mask: str, pos: int) -> PositionTable:
        letter = letter[0].lower()
        mask = mask[0]

        existing = self.get_for(letter)

        if mask == '-':
            existing.set_not_found()
            return existing

        existing.set_by_guess(pos, mask)
        return existing


def read_dictionary(lang: str, word_length: int) -> List[str]:
    filename = f'wordlist_{lang}_{word_length}.txt'

    with open(filename, 'r', encoding='utf-8') as f:
        words = f.readlines()
        words = [w.strip() for w in words]
        return words


def main(lang: str, \
         word_length: int, \
         used_words: List[str], \
         guess_masks: List[str]) -> None:
    guess_tables = tuple(zip(used_words, guess_masks))

    position_tables = __build_position_tables(used_words, guess_masks, word_length)
    
    known_letters = KnownLetters(guess_tables)
    regex = __build_regex(position_tables)

    words = read_dictionary(lang, word_length)
    output = []
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
            for excluded_letter in known_letters.excluded_letters:
                if excluded_letter in result:
                    stop_condition_meet = True
                    break

            if stop_condition_meet:
                log_exit('Excluded letter found')
                continue

            for included_letter in known_letters.included_letters:
                if included_letter not in result:
                    stop_condition_meet = True
                    break

            if stop_condition_meet:
                log_exit('Included letter not found')
                continue

            for excluded_word in used_words:
                if len(excluded_word.strip()) > 0 and word.startswith(excluded_word):
                    stop_condition_meet = True
                    break

            if stop_condition_meet:
                log_exit('Excluded word')
                continue

            for pos in range(len(word)):
                letter = word[pos]
                table = position_tables.get_for(letter)
                can_be_at_position = table.can_be_located_at_pos(pos)
                if not can_be_at_position:
                    stop_condition_meet = True
                    break

            if stop_condition_meet:
                log_exit('Letter can\'t be at position')
                continue

            line = f'{result}\n'
            f.write(line)
            output.append(line.strip())

    print('\n'.join(output))
    print()
    print(f'INFO Included letters: {known_letters.included_letters}')
    print(f'INFO Excluded letters: {known_letters.excluded_letters}')
    print(f'INFO Found words: {len(output)}')


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

                if mask == '-':
                    self.__add_excluded(letter)
                elif mask == '+' or mask == '?':
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


def __build_regex(position_tables: PositionTablesList) -> Pattern[str]:
    result = ['.'] * position_tables.word_length
    for table in position_tables.tables:
        guess_mask = table.position_mask
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
        used_words = config['usedWords'].split(',')
        guess_masks = config['guessMasks'].split(',')
        length = int(config['length'])

        main(lang, length, used_words, guess_masks) 
    except Exception as e:
        print(e)


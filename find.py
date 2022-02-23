import json
import re
from typing import List, Pattern
from known_letters import KnownLetters

# TODO: Optimize guess masks by replacing removing one `?` when match (`+`) is found
class PositionTable:
    __default_character = True
    
    def __init__(self, letter: str, positions: List[bool]):
        self.letter: str = letter[0]
        self.position_mask: List[bool] = positions

    def can_be_at(self, position: int) -> bool:
        if position > len(self.position_mask):
            raise Exception(f'Positions table don\'t have enough positions `{self}`[{position}]')

        return self.position_mask[position]

    def __set_at_pos(self, pos: int, can_be_at_pos: bool) -> None:
        self.position_mask[pos] = can_be_at_pos

    def set_by_guess(self, position: int, mask: str) -> None:
        mask = mask.strip()
        if len(mask) != 1:
            raise Exception('Mask have to be one character long')
        
        can_be_at_position = mask == '+'
        self.__set_at_pos(position, can_be_at_position)

    def set_not_found(self) -> None:
        not_found_mask = [False] * len(self.position_mask)
        self.position_mask = not_found_mask

    @staticmethod
    def default_for(letter: str, length: int):
        return PositionTable(letter, [PositionTable.__default_character] * length)

    def __str__(self):
        repr = ['+' if c else '-' for c in self.position_mask]
        return f'{self.letter}: `{repr}`'

    def __repr__(self):
        return self.__str__()


class PositionTablesList:
    def __init__(self, word_length: int):
        self.tables: List[PositionTable] = []

        word_length = int(word_length)
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
        existing.set_by_guess(pos, mask)
        return existing

    def set_not_found(self, letter: str) -> PositionTable:
        existing = self.get_for(letter)
        existing.set_not_found()


def main(lang: str, \
         word_length: int, \
         used_words: List[str], \
         guess_masks: List[str]) -> None:
    guess_tables = tuple(zip(used_words, guess_masks))
    known_letters = KnownLetters(guess_tables)

    position_tables = __build_position_tables(used_words, guess_masks, known_letters)
    
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
                can_be_at_position = table.can_be_at(pos)
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


def __build_position_tables(used_words: List[str], \
        guess_masks: List[str], \
        known_letters: KnownLetters) \
        -> PositionTablesList:
    word_length = len(used_words[0].strip())
    result: PositionTablesList = PositionTablesList(word_length)

    if len(used_words) != len(guess_masks):
        raise Exception('Define guess mask for each of the excluded words')

    zipped = tuple(zip(used_words, guess_masks))
    for word_wordmask in zipped:
        word = word_wordmask[0]
        wordmask = word_wordmask[1]

        data = tuple(zip(word, wordmask))
        for position in range(len(data)):
            letter = data[position][0]
            if letter in known_letters.excluded_letters:
                result.set_not_found(letter)
            else:
                mask = data[position][1]
                result.update_for(letter, mask, position)

    return result


def read_dictionary(lang: str, word_length: int) -> List[str]:
    filename = f'wordlist_{lang}_{word_length}.txt'

    with open(filename, 'r', encoding='utf-8') as f:
        words = f.readlines()
        words = [w.strip() for w in words]
        return words


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


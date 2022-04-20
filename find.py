import json
from random import randrange
import re
import tabulate
from typing import List, Pattern, Tuple
from known_letters import KnownLetters
from position_table import PositionTable, PositionTablesList
import common


def main(lang: str, \
         word_length: int, \
         used_words: List[str], \
         guess_masks: List[str]) -> None:
    guess_tables = tuple(zip(used_words, guess_masks))
    known_letters = KnownLetters(guess_tables)

    position_tables = __build_position_tables(used_words, guess_masks, known_letters)
    regex = __build_regex(guess_tables)

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

    expected_count = 15
    found_words_count = len(output)
    found_words = __draw_from(output, expected_count)

    all_withouth_repetitions = __get_withouth_repetitions(output)
    withouth_repetitions = __draw_from(all_withouth_repetitions, expected_count)
    withouth_repetitions = __fill_to_count(withouth_repetitions, expected_count)

    table = list(zip(found_words, withouth_repetitions))
    table.append(('-- SUM --', '-- SUM --'))
    table.append((found_words_count, len(all_withouth_repetitions)))

    print(tabulate.tabulate(table, tablefmt='psql',
          headers=['From all words', 'Withouth repeated letters']))

    print()
    print(f'INFO Included letters: {known_letters.included_letters}')
    print(f'INFO Excluded letters: {known_letters.excluded_letters}')
    print(f'INFO Found words: {found_words_count}')


def __draw_from(collection: List, expected_count: int) -> List:
    collection_len = len(collection)
    if collection_len <= expected_count:
        return collection

    result = []
    for _ in range(expected_count):
        upper_limit = collection_len - 1
        draw = randrange(upper_limit)
        collection_len -= 1

        element = collection.pop(draw)
        result.append(element)

    return result


def __fill_to_count(collection: List[str], expected_count: int) -> List[str]:
    collection_len = len(collection)
    if collection_len >= expected_count:
        return collection

    to_be_inserted = expected_count - collection_len
    filler = [''] * to_be_inserted

    result = list(collection)
    result.extend(filler)

    return result

def __get_withouth_repetitions(collection: List[str]) -> List[str]:
    result = []
    for word in collection:
        used_letters = []
        repetition_found = False

        for letter in word:
            if letter in used_letters:
                repetition_found = True
                break

            used_letters.append(letter)

        if not repetition_found:
            result.append(word)

    return result


# TODO: use [^excluded_letters] instead of `.`
def __build_regex(guess_tables: Tuple[str, str]) -> Pattern[str]:
    result = ['.'] * len(guess_tables[0][0])
    for t in guess_tables:
        word = t[0]
        guess = t[1]

        if common.CHAR_FOUND not in guess:
            continue

        for i in range(len(word)):
            letter = word[i][0].lower()
            mask = guess[i]

            if mask == common.CHAR_FOUND:
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


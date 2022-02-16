import re
import string
import sys
from typing import List, Pattern


def main(lang: str, \
         length: int, \
         mask: str, \
         excluded_words: List[str], \
         included_letters: str, \
         guess_mask: List[str]) -> None:
    filename = f'wordlist_{lang}_{length}.txt.'
    
    regex = __build_regex(mask)
    excluded_letters = __build_excluded_letters_from(included_letters, excluded_words)

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
        length = __get_pos_arg(6, 5, "Expected length")

        main(lang, length, mask, excluded_words, included_letters, guess_mask) 
    except Exception as e:
        print(e)


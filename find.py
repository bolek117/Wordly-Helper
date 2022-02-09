import re
import sys
from typing import List, Pattern


def main(lang: str, length: int, mask: str, excluded: str, excluded_words: List[str]) -> None:
    filename = f'wordlist_{lang}_{length}.txt.'
    
    regex = __build_regex(mask)

    with open(filename, 'r', encoding='utf-8') as f:
        words = f.readlines()

    with open('output.txt', 'w') as f:
        for w in words:
            word = w.strip()
            g = regex.match(word)

            if not g:
                continue
            
            result = g.group(0)

            should_continue = False
            for excluded_letter in excluded:
                if excluded_letter in result:
                    should_continue = True
                    break

            if should_continue:
                continue

            for excluded_word in excluded_words:
                if word.startswith(excluded_word):
                    should_continue = True
                    break

            if should_continue:
                continue

            f.write(f'{result}\n')

    with open('output.txt', 'r') as f:
        print(f.read())


def __build_regex(mask: str) -> Pattern[str]:
    # mask = mask.replace('?', '[a-zA-Z]')
    return re.compile(mask)


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
        excluded_letters = __get_pos_arg(3, "", "Excluded Letters")
        excluded_words = __get_pos_arg(4, "", "Excluded words").split(',')
        length = __get_pos_arg(5, 5, "Expected length")

        main(lang, length, mask, excluded_letters, excluded_words) 
    except Exception as e:
        print(e)


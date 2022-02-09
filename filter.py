from typing import List


def add_to_result(result: List[str], word: str, expected_len: int=5) -> List[str]:
    word = word.strip()
    parts = word.split('/')

    if len(parts) == 2:
        word = parts[0]

    if len(word) == expected_len:
        result.append(word)


def process(filename: str, expected_len: int = 5, encoding: str = 'utf-8') -> None:
    with open(filename, 'r', encoding=encoding) as f:
        words = f.readlines()

    result = []
    for word in words:
        word = word.strip()
        parts = word.split('/')

        if len(parts) == 2:
            word = parts[0]

        if len(word) == expected_len:
            result.append(word)

    name, extension = filename.rsplit('.', 1)
    with open(f'{name}_{expected_len}.{extension}', 'w', encoding=encoding) as f:
        for word in result:
            f.write(f'{word.lower()}\n')


def main():
    process('wordlist_pl.txt')
    

if __name__ == "__main__":
    main()

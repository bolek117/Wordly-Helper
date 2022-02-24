from typing import List
import common


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
        
        can_be_at_position = (mask == common.CHAR_FOUND)
        self.__set_at_pos(position, can_be_at_position)

    def set_not_found(self) -> None:
        not_found_mask = [False] * len(self.position_mask)
        self.position_mask = not_found_mask

    @staticmethod
    def default_for(letter: str, length: int):
        return PositionTable(letter, [PositionTable.__default_character] * length)

    def __str__(self):
        repr = [common.CHAR_FOUND if c else common.CHAR_NOT_FOUND for c in self.position_mask]
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
        
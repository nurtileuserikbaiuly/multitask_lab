import re

from config import WORDS


class WordTest:
    """Проверяет, сколько слов из списка студент вспомнил."""

    def __init__(self, words=WORDS):
        self.words = {self.normalize(w) for w in words}

    @staticmethod
    def normalize(text):
        """Приводит слово к единому виду: маленькие буквы, ё -> е."""
        return text.lower().replace("ё", "е").strip()

    def parse_answer(self, text):
        """Разбивает ответ студента на отдельные слова."""
        parts = re.split(r"[\W_]+", text)
        return {self.normalize(p) for p in parts if p}

    def count_correct(self, text):
        """Считает верные слова (каждое слово учитывается один раз)."""
        answers = self.parse_answer(text)
        return len(answers & self.words)
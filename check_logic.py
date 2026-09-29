from logic import WordTest

test = WordTest()

# Верные: яблоко, книга, река. Повтор "КНИГА" и слово "слон" не считаются.
print(test.count_correct("Яблоко, книга, КНИГА, река, слон"))  # ожидаем 3
print(test.count_correct(""))                                  # ожидаем 0
print(test.count_correct("яблоко\nмост\nчай"))                  # ожидаем 3
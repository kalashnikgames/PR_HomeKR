"""Проверки синтаксиса, вложенных словарей и чисел."""

import tomllib
import unittest

from src.parser import TranslationError, translate_source
from src.toml_writer import to_toml


class ParserTests(unittest.TestCase):
    """Проверить допустимые конструкции и синтаксические ошибки."""

    def test_nested_dictionary_and_comments(self):
        """Комментарии не меняют значения, вложенная таблица сохраняется."""
        source = """#[ многострочный
комментарий ]#
{
    value = 00012.50, * пояснение
    nested = { small = 1., inner = { leaf = 0.25 } },
}
"""
        result = to_toml(translate_source(source))
        self.assertEqual(tomllib.loads(result), {
            "value": 12.5,
            "nested": {"small": 1.0, "inner": {"leaf": 0.25}},
        })
        self.assertIn("value = 12.50", result)
        self.assertIn("small = 1.0", result)

    def test_empty_dictionaries(self):
        """Пустые словари допустимы и становятся таблицами TOML."""
        self.assertEqual(tomllib.loads(to_toml(
            translate_source("{ empty = {} }")
        )), {"empty": {}})
        self.assertEqual(to_toml(translate_source("{}")), "")

    def test_syntax_and_duplicate_key(self):
        """Неверные токены и повтор ключа объясняются пользователю."""
        for source in ("{ a = 1 }", "{ a = 1.2 b = 2.0 }"):
            with self.subTest(source=source):
                with self.assertRaisesRegex(
                    TranslationError, "синтаксическая ошибка: строка"
                ):
                    translate_source(source)
        with self.assertRaisesRegex(TranslationError, "повтор ключа a"):
            translate_source("{ a = 1.0, a = 2.0 }")


if __name__ == "__main__":
    unittest.main()

"""Проверки объявлений, ссылок и вложенных областей констант."""

import tomllib
import unittest

from src.parser import TranslationError, translate_source
from src.toml_writer import to_toml


class ConstantTests(unittest.TestCase):
    """Проверить вычисление значений до генерации TOML."""

    def test_global_and_local_constants(self):
        """Локальная константа затеняет внешнюю только внутри словаря."""
        source = """def base := 8.1 * объявление до корня
def template := { precision = 0.01,
                  scales = { factor = 2. } }
{
    threshold = ^(base),
    first = ^(template),
    nested = {
        def base := 9.2,
        local = ^(base),
        reused = ^(template),
        deeper = { inherited = ^(base) }
    },
    later = ^(base)
}
"""
        result = tomllib.loads(to_toml(translate_source(source)))
        self.assertEqual(result["threshold"], 8.1)
        self.assertEqual(result["later"], 8.1)
        self.assertEqual(result["nested"]["local"], 9.2)
        self.assertEqual(result["nested"]["deeper"]["inherited"], 9.2)
        self.assertEqual(result["first"], result["nested"]["reused"])
        self.assertEqual(result["first"]["scales"]["factor"], 2.0)

    def test_chained_references_and_comments(self):
        """Константа может ссылаться на объявленную ранее константу."""
        source = """def first := 001.50
#[ игнорируемая запись
def missing := 99.0 ]#
def second := ^(first)
{ value = ^(second) }
"""
        self.assertEqual(to_toml(translate_source(source)), "value = 1.50\n")

    def test_errors_in_definitions_and_references(self):
        """Неизвестные и повторные константы содержат место ошибки."""
        cases = (
            ("{ value = ^(missing) }", "неизвестная константа missing"),
            ("def a := ^(b) { value = 1.0 }", "неизвестная константа b"),
            ("def a := 1.0 def a := 2.0 {}", "повтор константы a"),
            ("{ def a := 1.0, def a := 2.0 }", "повтор константы a"),
        )
        for source, message in cases:
            with self.subTest(source=source):
                with self.assertRaisesRegex(TranslationError, message):
                    translate_source(source)

    def test_inner_definition_is_not_visible_outside(self):
        """Вложенные определения не выходят за пределы словаря."""
        source = "{ nested = { def local := 1.0 }, out = ^(local) }"
        with self.assertRaisesRegex(TranslationError, "константа local"):
            translate_source(source)


if __name__ == "__main__":
    unittest.main()

"""Синтаксический разбор конфигурации средствами Lark."""

from lark import Lark, Tree, UnexpectedInput


GRAMMAR = r"""
    start: dictionary
    dictionary: "{" [entry ("," entry)* [","]] "}"
    entry: NAME "=" value
    ?value: NUMBER -> number
          | dictionary

    NAME: /[a-zA-Z][a-zA-Z0-9]*/
    NUMBER: /[0-9]+\.[0-9]*/

    %import common.WS
    %ignore WS
    %ignore /\*[^\n]*/
    %ignore /#\[(.|\n)*?\]#/
"""

PARSER = Lark(GRAMMAR, parser="lalr", propagate_positions=True,
              maybe_placeholders=False)


class TranslationError(Exception):
    """Ошибка входного текста с указанием места возникновения."""


def parse_source(source):
    """Проверить синтаксис и вернуть дерево Lark."""
    try:
        return PARSER.parse(source)
    except UnexpectedInput as error:
        location = f"строка {error.line}, столбец {error.column}"
        raise TranslationError(f"синтаксическая ошибка: {location}") from error


def normalize_number(token):
    """Записать десятичное число в допустимом формате TOML."""
    whole, fraction = str(token).split(".")
    return f"{int(whole)}.{fraction or '0'}"


def evaluate_dictionary(node):
    """Вычислить словарь из дерева без потери порядка полей."""
    result = {}
    for entry in node.children:
        name, value_node = entry.children
        if name.value in result:
            location = f"строка {name.line}, столбец {name.column}"
            raise TranslationError(f"повтор ключа {name.value}: {location}")
        result[name.value] = evaluate_value(value_node)
    return result


def evaluate_value(node):
    """Вычислить число или вложенный словарь."""
    if isinstance(node, Tree) and node.data == "dictionary":
        return evaluate_dictionary(node)
    return normalize_number(node.children[0])


def translate_source(source):
    """Преобразовать полный входной текст в дерево значений."""
    document = parse_source(source)
    return evaluate_dictionary(document.children[0])

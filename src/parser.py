"""Синтаксический разбор конфигурации средствами Lark."""

from copy import deepcopy
from unicodedata import decimal

from lark import Lark, Tree, UnexpectedInput


GRAMMAR = r"""
    start: definition* dictionary
    dictionary: "{" [item ("," item)* [","]] "}"
    ?item: entry | definition
    entry: name "=" value
    definition: "def" name ":=" value
    ?value: NUMBER -> number
          | dictionary
          | reference
    reference: "^" "(" name ")"
    name: NAME | DEF

    DEF: "def"
    NAME: /[a-zA-Z][a-zA-Z0-9]*/
    NUMBER: /\d+\.\d*/

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
    whole = "".join(str(decimal(digit)) for digit in whole)
    fraction = "".join(str(decimal(digit)) for digit in fraction)
    return f"{whole.lstrip('0') or '0'}.{fraction or '0'}"


def name_token(node):
    """Получить имя вместе с позицией, включая имя `def`."""
    return node.children[0]


def define_constant(node, scope, local_names):
    """Вычислить объявление и проверить повтор в текущей области."""
    name_node, value_node = node.children
    name = name_token(name_node)
    if name.value in local_names:
        location = f"строка {name.line}, столбец {name.column}"
        raise TranslationError(f"повтор константы {name.value}: {location}")
    scope[name.value] = evaluate_value(value_node, scope)
    local_names.add(name.value)


def evaluate_dictionary(node, inherited_scope):
    """Вычислить словарь с локальными константами и порядком полей."""
    result = {}
    scope = inherited_scope.copy()
    local_names = set()
    for item in node.children:
        if item.data == "definition":
            define_constant(item, scope, local_names)
            continue
        name_node, value_node = item.children
        name = name_token(name_node)
        if name.value in result:
            location = f"строка {name.line}, столбец {name.column}"
            raise TranslationError(f"повтор ключа {name.value}: {location}")
        result[name.value] = evaluate_value(value_node, scope)
    return result


def evaluate_value(node, scope):
    """Вычислить число, словарь или ссылку на известную константу."""
    if isinstance(node, Tree) and node.data == "dictionary":
        return evaluate_dictionary(node, scope)
    if node.data == "reference":
        name = name_token(node.children[0])
        if name.value not in scope:
            location = f"строка {name.line}, столбец {name.column}"
            raise TranslationError(
                f"неизвестная константа {name.value}: {location}")
        return deepcopy(scope[name.value])
    return normalize_number(node.children[0])


def translate_source(source):
    """Преобразовать полный входной текст в дерево значений."""
    document = parse_source(source)
    scope = {}
    local_names = set()
    for definition in document.children[:-1]:
        define_constant(definition, scope, local_names)
    return evaluate_dictionary(document.children[-1], scope)

"""Командная строка: stdin с конфигурацией, файл с TOML."""

import argparse
import sys
from pathlib import Path

from src.parser import TranslationError, translate_source
from src.toml_writer import to_toml


def main(argv=None):
    """Прочитать stdin, проверить текст и записать TOML в файл."""
    parser = argparse.ArgumentParser(description="Транслятор конфигурации")
    parser.add_argument("-o", "--output", required=True, type=Path,
                        help="путь к выходному файлу TOML")
    arguments = parser.parse_args(argv)
    try:
        result = to_toml(translate_source(sys.stdin.read()))
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(result, encoding="utf-8")
    except (TranslationError, OSError, UnicodeError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

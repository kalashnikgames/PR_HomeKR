"""Командная строка: stdin с конфигурацией, файл с TOML."""

import argparse
import os
import sys
import tempfile
from pathlib import Path

from src.parser import TranslationError, translate_source
from src.toml_writer import to_toml


def write_output(path, content):
    """Атомарно заменить файл, не оставляя частичный результат."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=".config-", suffix=".toml", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8",
                       newline="\n") as stream:
            stream.write(content)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def main(argv=None):
    """Прочитать UTF-8 stdin, проверить текст и записать TOML в файл."""
    parser = argparse.ArgumentParser(description="Транслятор конфигурации")
    parser.add_argument("-o", "--output", required=True, type=Path,
                        help="путь к выходному файлу TOML")
    arguments = parser.parse_args(argv)
    try:
        if sys.stdin.isatty():
            print("Введите конфигурацию. Для завершения в Windows "
                  "нажмите Ctrl+Z, затем Enter; в Linux/macOS — Ctrl+D.",
                  file=sys.stderr)
        source = sys.stdin.buffer.read().decode("utf-8-sig")
        result = to_toml(translate_source(source))
        write_output(arguments.output, result)
    except KeyboardInterrupt:
        print("\nВвод прерван.", file=sys.stderr)
        return 130
    except (TranslationError, OSError, UnicodeError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

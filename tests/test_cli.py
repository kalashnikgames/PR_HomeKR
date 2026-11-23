"""Проверка чтения stdin и записи результата по ключу CLI."""

import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch

from src.cli import main


class CliTests(unittest.TestCase):
    """Проверить полный запуск без создания файлов в репозитории."""

    def test_output_and_failed_input(self):
        """Успех пишет TOML, ошибка оставляет существующий файл целым."""
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "settings.toml"
            command = [sys.executable, "-B", "-m", "src.cli",
                       "--output", str(output)]
            success = subprocess.run(command, input="{ size = 2.5 }",
                                     text=True, capture_output=True,
                                     encoding="utf-8")
            self.assertEqual(success.returncode, 0, success.stderr)
            self.assertEqual(tomllib.loads(output.read_text("utf-8")),
                             {"size": 2.5})
            failure = subprocess.run(command, input="{ size = 2 }",
                                     text=True, capture_output=True,
                                     encoding="utf-8")
            self.assertEqual(failure.returncode, 1)
            self.assertIn("строка", failure.stderr)
            self.assertEqual(tomllib.loads(output.read_text("utf-8")),
                             {"size": 2.5})

    def test_utf8_comments_and_nested_output(self):
        """UTF-8 комментарии и каталоги пути проходят через CLI."""
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested" / "result.toml"
            command = [sys.executable, "-B", "-m", "src.cli",
                       "-o", str(output)]
            source = "#[ температура ]#\n{ temp = 21.5 }"
            result = subprocess.run(command, input=source, text=True,
                                    encoding="utf-8", capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(tomllib.loads(output.read_text("utf-8")),
                             {"temp": 21.5})

    def test_interrupted_console_input(self):
        """Ctrl+C завершает CLI без traceback и выходного файла."""
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.toml"
            with patch("src.cli.sys.stdin") as standard_input:
                standard_input.isatty.return_value = True
                standard_input.buffer.read.side_effect = KeyboardInterrupt
                with patch("src.cli.sys.stderr") as standard_error:
                    self.assertEqual(main(["-o", str(output)]), 130)
            self.assertFalse(output.exists())
            self.assertTrue(standard_error.write.called)


if __name__ == "__main__":
    unittest.main()

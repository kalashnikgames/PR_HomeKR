"""Проверка чтения stdin и записи результата по ключу CLI."""

import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


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


if __name__ == "__main__":
    unittest.main()

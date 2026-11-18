"""Интеграционная проверка трех предметных областей через CLI."""

import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


EXAMPLES = Path(__file__).resolve().parent.parent / "examples"
EXPECTED = {
    "server": {
        "server": {"port": 8080.0,
                   "limits": {"memory": 512.0, "workers": 4.0}},
        "monitoring": {"alert": 75.5, "retries": 3.0},
    },
    "experiment": {
        "experiment": {
            "sample": {"temperature": 21.5, "pressure": 101.3},
            "sensorA": {"offset": 0.01, "scale": 0.025},
            "sensorB": {"offset": 0.01, "scale": 0.025},
        },
    },
    "budget": {
        "year": 2026.0,
        "departments": {
            "research": {"allocated": 125000.0, "tax": 20.0},
            "training": {"allocated": 48000.0, "tax": 10.0},
        },
        "standardTax": 20.0,
    },
}


class ExampleTests(unittest.TestCase):
    """Сопоставить полноценный вывод CLI с ожидаемыми значениями."""

    def test_three_domains(self):
        """Каждый пример запускается и порождает корректный TOML."""
        with tempfile.TemporaryDirectory() as directory:
            for name, expected in EXPECTED.items():
                with self.subTest(example=name):
                    source = (EXAMPLES / f"{name}.conf").read_bytes()
                    output = Path(directory) / f"{name}.toml"
                    command = [sys.executable, "-B", "-m", "src.cli",
                               "-o", str(output)]
                    result = subprocess.run(command, input=source,
                                            capture_output=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    actual = tomllib.loads(output.read_text("utf-8"))
                    self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()

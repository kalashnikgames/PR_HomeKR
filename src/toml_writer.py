"""Преобразование словарей и десятичных чисел в TOML."""


def render_table(values, path, lines):
    """Записать скаляры таблицы до вложенных таблиц."""
    if path:
        lines.append(f"[{'.'.join(path)}]")
    for name, value in values.items():
        if not isinstance(value, dict):
            lines.append(f"{name} = {value}")
    for name, value in values.items():
        if isinstance(value, dict):
            if lines:
                lines.append("")
            render_table(value, (*path, name), lines)


def to_toml(values):
    """Вернуть корректный TOML с завершающим переводом строки."""
    lines = []
    render_table(values, (), lines)
    return "\n".join(lines).rstrip() + "\n" if lines else ""

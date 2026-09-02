#!/usr/bin/env python
"""Django management CLI."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Не удалось импортировать Django. Убедитесь, что виртуальное "
            "окружение активировано и зависимости установлены."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

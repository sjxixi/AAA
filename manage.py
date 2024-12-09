#!/usr/bin/env python
"""Django 用于管理任务的命令行实用程序."""
import os
import sys


def main():
    """运行管理任务."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AAA.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "无法导入 Django。您确定它已安装并且 "
            "在您的 PYTHONPATH 环境变量上可用？你 "
            "忘记激活虚拟环境？"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

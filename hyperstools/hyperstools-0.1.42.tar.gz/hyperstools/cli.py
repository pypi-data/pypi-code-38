import os
import click
import django

import importlib

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")


def import_module(dotted_path):
    dotted_path = dotted_path.replace(".py", "").replace("/", ".")
    module_parts = dotted_path.split(".")
    if len(module_parts) < 2:
        module_parts.append("main")  # 默认调用main函数
    if len(module_parts) == 2:
        module_parts.insert(0, "utility")  # 默认调用utility/下的文件
    module_path = ".".join(module_parts[:-1])
    module = importlib.import_module(module_path)
    return getattr(module, module_parts[-1])


@click.command()
@click.argument('path')
@click.option('args', nargs=-1)
def main(path, args):
    """
    python cli.py rabbit  即调用utility/rabbit.py 下的main函数
    python cli.py rabbit.listen  即调用utility/rabbit.py 下的listen函数
    python cli.py dataset/latLng2Region.py.main 调用dataset/latLng2Region下的main函数
    """
    django.setup()
    func = import_module(path)
    response = func(*args)
    click.echo(response)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

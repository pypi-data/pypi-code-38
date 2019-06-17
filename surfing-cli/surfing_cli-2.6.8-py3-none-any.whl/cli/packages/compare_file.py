"""
比较两个文件内容[行]
"""
import click, cli, os, os.path as path


def get_file_lines(file):
    """
    读取文件行列表
    :param file:
    :return:
    """
    lines = []
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            lines.append(line.strip().strip("\n"))
    return lines


@click.option('--compare_type', '-t', help="返回值类型：相同的部分 | a多出来的部分 | b多出来的部分",
              type=click.Choice(['a_and_b', 'not_b', 'not_a']))
@click.argument('file_b', type=click.Path(exists=True))
@click.argument('file_a', type=click.Path(exists=True))
@click.command()
def compare_file(file_a, file_b, compare_type):
    """
    比较两个文件[行比较] 更多信息用 --help 获取帮助
    """
    if not compare_type:
        cli.error("请用 -t 参数指定比较类型，更多信息用 --help 获取")
    a_lines = get_file_lines(file_a)  # 去重
    b_lines = get_file_lines(file_b)  # 去重

    lines = []
    if compare_type == "a_and_b":
        lines.extend(a_lines)
        lines.extend(b_lines)
    elif compare_type == "not_a":
        for line in b_lines:
            if line not in a_lines:
                lines.append(line)
    elif compare_type == "not_b":
        for line in a_lines:
            if line not in b_lines:
                lines.append(line)
    print("\n".join(lines))

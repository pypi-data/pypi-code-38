import rx
from rx import Observable
from pathlib import Path

import subprocess
from functools import partial
from typing import Callable

from ..primitives.base import maybe_type
from .combinator import sequential
from ..primitives.FS import File, Directory


class CLI:
    @staticmethod
    def func(fn: Callable) -> Observable:
        """
        Turn a function to Observable.
        """
        return rx.create(fn)

    @staticmethod
    def cli(body: str, dir: str = "./") -> func:
        def cmd(observer, scheduler, body=body):
            try:
                result = (
                    subprocess.run(
                        body.split(" "), cwd=dir, check=True, stdout=subprocess.PIPE
                    )
                    .stdout.decode()
                    .split("\n")
                )
                observer.on_next(result[:-1])
                observer.on_completed()
            except FileNotFoundError as err:
                observer.on_error(f"CMD error! {err}")

        return CLI.func(partial(cmd, body=body))

    # @staticmethod
    # def cli_at_dir(body: str, dir: str):
    #     def cmd(observer, scheduler, body=body):
    #         try:
    #             result = (
    #                 subprocess.run(
    #                     body.split(" "), cwd=dir, check=True, stdout=subprocess.PIPE
    #                 )
    #                 .stdout.decode()
    #                 .split("\n")
    #             )
    #             observer.on_next(result[:-1])
    #             observer.on_completed()
    #         except FileNotFoundError as err:
    #             observer.on_error(f"CMD error! {err}")
    #
    #     return CLI.func(partial(cmd, body=body))

    @staticmethod
    def ls(source=".") -> func:
        return CLI.cli(f"ls {source}")

    @staticmethod
    def mkdir(target_dir) -> "Observable[Path]":
        """
        Return a observable that make a directory, or just return
        directory url if dir already exist and empty.

        :param target_dir:
        :return:
        """

        def _mkdir(target: "Path") -> 'func[Resource["Path"]]':
            return CLI.cli("mkdir " + maybe_type(target, str))

        target_dir = Path(target_dir)

        if target_dir.exists() and not len(list(target_dir.iterdir())):
            return rx.of(str(target_dir))
        else:
            return sequential([_mkdir(target_dir), rx.of(str(target_dir))])

    @staticmethod
    def mv(source: "File", target: "Path | File") -> 'func[Resource["File"]]':
        source = Path(source)
        target = Path(target)
        if source.is_file():
            return CLI.cli(f"mv {source} {target}")
        else:
            raise ValueError("Given url dose not exist.")

    @staticmethod
    def cp(source: "url", target: "url") -> 'func[Resource["File"]]':
        if Path(source).is_file():
            return CLI.cli(f"cp {str(source)} {str(target)}")
        else:
            raise ValueError(f"Resource: {source} is not legal.")

    @staticmethod
    def rm(url: "File | Directory") -> 'func[Resource["File"]]':
        if maybe_type(url, File) is not None:
            return CLI.cli(f"rm {str(url)}")
        elif maybe_type(url, Directory) is not None:
            return CLI.cli(f"rm -r {str(url)}")
        else:
            raise ValueError(f"url: {str(url)} not exist or cannot be removed.")


# from .primitive import cli, Resource, func
# from .combinator import sequential
# from ..primitives.FS import Directory, File
# from ..primitives.base import maybe_type
# from pathlib import Path
# import rx
#
#
# def ls(source=".") -> func:
#     return cli(f"ls {source}")
#
#
# def mv(source: "File", target: "Path | File") -> 'func[Resource["File"]]':
#     try:
#         source = Path(source)
#         target = Path(target)
#         if source.is_file():  # and target.is_dir():
#             return cli(f"mv {source} {target}")
#         else:
#             raise ValueError
#     except Exception as e:
#         print(e)
#
#
# def mkdir(target: "Path") -> 'func[Resource["Path"]]':
#     if not isinstance(target, str):
#         try:
#             target = str(target)
#         except Exception as e:
#             raise e
#
#     return cli("mkdir " + target)
#
#
# def mkdir_n_return(dir) -> "Observable[Path]":
#     dir = maybe_type(dir, Path)
#     if dir.exists() and not len(list(dir.iterdir())):
#         return rx.of(str(dir.absolute()))
#     else:
#         return sequential([mkdir(dir), rx.of(dir)])
#
#
# def mkdir_if_not_exist(target: "Path") -> 'func[Resource["Path"]]':
#     if Path(target).is_dir():
#         return ls(target)
#     return mkdir_n_return(target)
#
#
# def cp(source: "url", target: "url", check=True) -> 'func[Resource["File"]]':
#     if check:
#         if Path(source).is_file() and Path(target).is_dir():
#             return cli(f"cp {str(source)} {str(target)}")
#         else:
#             raise ValueError(
#                 f"Resource: {source} is not a file, or target {target} is not a dir."
#             )
#     else:
#         return cli(f"cp {str(source)} {str(target)}")
#
#
# def rm(target: "File") -> 'func[Resource["File"]]':
#     try:
#         target = Path(target)
#     except:
#         raise ValueError(f"Target {target} is not an acceptable url.")
#
#     if target.is_dir():
#         return cli(f"rm -r {str(target)}")
#     return cli(f"rm {str(target)}")

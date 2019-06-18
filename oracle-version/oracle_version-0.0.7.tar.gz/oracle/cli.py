from cmd import Cmd

import emoji

import oracle


class OracleCli(Cmd):
    intro = "Hello! Type help to list commands for Oracle\n"
    prompt = emoji.emojize(':crystal_ball: Oracle Listen  :crystal_ball:: ')
    file = open(".version_journal", "a+")

    def do_version(self, args) -> None:
        """GET unique version name\nIf you have version id, type: version <id>"""
        version_name, seed = oracle.get_version_name(None if not args else args)

        while seed in self.file.read().split("\n"):
            version_name, seed = oracle.get_version_name()

        self.file.write(f"{seed}\n")

        self.stdout.write(f"{version_name}\n")

    def do_object(self, args) -> None:
        """Get random object name"""

        self.stdout.write(f"{oracle.get_object()}\n")

    def do_property(self, args) -> None:
        """Get random property name"""

        self.stdout.write(f"{oracle.get_property()}\n")

    def do_clear(self, args) -> None:
        """Clear version journal"""
        self.file.truncate(0)

    def do_exit(self, args) -> bool:
        """Exit from oracle"""
        self.file.close()
        self.stdout.write(f"Bye! Bye!\n")

        return True


if __name__ == "__main__":
    OracleCli().cmdloop()

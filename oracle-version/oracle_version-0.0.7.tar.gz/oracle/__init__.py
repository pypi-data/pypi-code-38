from .oracle import get_property, get_object, get_version_name

name = "oracle_version"

if __name__ == "__main__":
    from cli import OracleCli

    OracleCli().cmdloop()

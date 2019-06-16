import sys
from eh.cli import Eh


def completion_hook(cmd, curr_word, prev_word):
    eh_obj = Eh(False, True)
    eh_keys = list(eh_obj.subjects.keys()) + list(eh_obj.repo_subs.subjects)
    eh_keys.sort()
    matches = [k for k in eh_keys if k.startswith(curr_word)]
    return matches


def main():
    results = completion_hook(*sys.argv[1:])
    if len(results):
          print("\n".join(results))


if __name__ == "__main__":
    main()

#! /usr/bin/env python
import json,sys
def main():
    if sys.argv[1:]:
        source = open(sys.argv[1]).read()
    else:
        source = sys.stdin.read()
    content = json.loads(source)
    sys.stdout.write(
        json.dumps( 
            content, 
            indent=2,
            sort_keys=True,
        )
    )
if __name__ == "__main__":
    main()

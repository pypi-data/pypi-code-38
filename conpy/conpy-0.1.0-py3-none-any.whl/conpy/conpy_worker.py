#!/usr/bin/env python
import gzip

try:
    import cPickle as pickle
except ImportError:
    import pickle

def main():
    with gzip.open("task.p.gz", 'rb') as f:
        task = pickle.load(f)

    result = task["task"](*task["args"], **task["kwargs"])

    with gzip.open("result.p.gz", 'wb') as f:
        pickle.dump(result, f)

if __name__ == "__main__":
    main()

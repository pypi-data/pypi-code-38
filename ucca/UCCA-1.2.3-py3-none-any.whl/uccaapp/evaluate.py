import argparse
import sys

from tqdm import tqdm

from ucca.evaluation import evaluate, Scores, LABELED, UNLABELED
from uccaapp.download_task import TaskDownloader

desc = """Download tasks from UCCA-App and evaluate them"""


def main(task_ids, by_filename=False, validate=None, log=None, **kwargs):
    kwargs["write"] = False
    if by_filename:
        task_ids_from_file = []
        for filename in task_ids:
            with open(filename, 'r') as f:
                task_ids_from_file += zip(*list(map(str.split, filter(None, map(str.strip, f)))))
        task_ids = task_ids_from_file
    else:
        task_ids = [[task_id] for task_id in task_ids]
    assert len(task_ids) == 2, "Got %d lists of task IDs instead of two" % len(task_ids)
    downloader = TaskDownloader(**kwargs)
    scores = []
    validate_h = open(validate, "w", encoding="utf-8") if validate else None
    log_h = open(log, "w", encoding="utf-8") if log else None
    if log:
        fields = ["guessed", "ref"] + Scores.field_titles(eval_type=LABELED) + Scores.field_titles(eval_type=UNLABELED)
        print(*fields, file=log_h, sep="\t", flush=True)
    for task_id_pair in tqdm(list(zip(*task_ids)), unit=" tasks", desc="Evaluating"):
        passage_pair = []
        for task_id in task_id_pair:
            passage, *_ = downloader.download_task(task_id, validate=validate_h, **kwargs)
            passage_pair.append(passage)
        score = evaluate(*passage_pair, **kwargs)
        if log:
            fields = list(task_id_pair) + score.fields(eval_type=LABELED) + score.fields(eval_type=UNLABELED)
            print(*fields, file=log_h, sep="\t", flush=True)
        scores.append(score)
    if validate:
        validate_h.close()
    if log:
        log_h.close()
    print()
    if len(scores) > 1:
        print("Aggregated scores:")
    Scores.aggregate(scores).print()


def check_args(p, args):
    if len(args.task_ids) not in (1, 2):
        p.error("Must supply exactly two task IDs or files with IDs, but got %d arguments" % len(args.task_ids))
    return args


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser(description=desc)
    TaskDownloader.add_arguments(argument_parser)
    main(**vars(check_args(argument_parser, argument_parser.parse_args())))
    sys.exit(0)

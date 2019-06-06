# Output pipelines in JSON.

import argparse
import json
import os
import sys

import sri.pipelines.all
import sri.pipelines.datasets

def load_args():
    parser = argparse.ArgumentParser(description = "Output a primitive's pipelines in the standard format.")

    parser.add_argument(
        'primitive', action = 'store', metavar = 'PRIMITIVE',
        help = "the D3M entrypoint of the primitive whose pipelines will be output"
    )

    parser.add_argument(
        'outdir', action = 'store', metavar = 'OUTPUT_DIR',
        help = "where to write the file"
    )

    parser.add_argument(
        '-o', '--one', action = "store_true",
        help = "only generate at most one pipeline"
    )

    parser.add_argument(
        '-p', '--prediction', action = "store_true",
        help = "only generate prediction pipelines"
    )

    arguments = parser.parse_args()

    return arguments.primitive, os.path.abspath(arguments.outdir), arguments.one, arguments.prediction

def main():
    primitive, out_dir, only_one, only_prediction = load_args()

    if (primitive not in sri.pipelines.all.get_primitives()):
        print("Could not locate pipelines for primitive: %s." % (primitive), file = sys.stderr)
        return

    os.makedirs(out_dir, exist_ok = True)

    for pipeline_class in sri.pipelines.all.get_pipelines(primitive):
        datasets = set(pipeline_class().get_datasets()) - sri.pipelines.datasets.SLOW_DATASETS

        for dataset in datasets:
            pipeline = pipeline_class()

            if (only_prediction and not pipeline.is_prediction_pipeline()):
                continue

            try:
                meta_info = {
                    'problem': sri.pipelines.datasets.get_problem_id(dataset),
                    'full_inputs': [ sri.pipelines.datasets.get_full_dataset_id(dataset) ],
                    'train_inputs': [ sri.pipelines.datasets.get_train_dataset_id(dataset) ],
                    'test_inputs': [ sri.pipelines.datasets.get_test_dataset_id(dataset) ],
                    'score_inputs': [ sri.pipelines.datasets.get_score_dataset_id(dataset) ],
                }

                out_path = os.path.join(out_dir, "%s.json" % (pipeline.get_id()))
                with open(out_path, 'w') as file:
                    file.write(pipeline.get_json())

                meta_path = os.path.join(out_dir, "%s.meta" % (pipeline.get_id()))
                with open(meta_path, 'w') as file:
                    json.dump(meta_info, file, indent = 4)

            except LookupError:
                print("Could not find dataset '%s'" % dataset, file=sys.stderr)
                continue

            if (only_one):
                break

if __name__ == '__main__':
    main()

import os
import random


class NegativeSamplesGenerator:

    def __init__(self, num_neg_samples=10):
        self.num_neg_samples = num_neg_samples

    def generate(self, input_files, output_dir):
        """Generate negative samples for each example of each input_file, and save the results in output_dir.

        Args:
            input_files: A list of negative samples files
            output_dir: A file path to save the generated negative samples.

        Returns:
            A list of negative samples files.
        """

        output_files = []
        for f in input_files:
            output_files.append(self._generate(f, output_dir))
        return output_files

    def _generate(self, f, output_dir):
        output_file = os.path.join(output_dir, str(f) + '.neg.txt')

        pos_query_doc_dict = {}
        pos_query_set = set()
        with open(f, mode='rt', encoding='utf8', buffering=8192) as fin:
            for line in fin:
                line = line.strip('\n')
                if not line:
                    continue
                segs = line.split('@')
                if len(segs) != 3:
                    continue
                query, doc, label = segs[0], segs[1], segs[2]
                if not query or not doc or not label:
                    continue

                if query in pos_query_doc_dict:
                    docs = pos_query_doc_dict.get(query, [])
                    docs.append(doc)
                    pos_query_doc_dict[query] = docs
                else:
                    docs = []
                    docs.append(query)
                    pos_query_doc_dict[query] = docs
                pos_query_set.add(query)

        pos_query_list = list(pos_query_set)
        print('len queries: %s' % len(pos_query_list))

        with open(output_file, mode='a+', encoding='utf8', buffering=8192) as fout:

            for q in pos_query_list:
                selected_query = [pos_query_list[i] for i in
                                  sorted(random.sample(range(len(pos_query_list)), self.num_neg_samples))]

                selected_docs = []
                for sq in selected_query:
                    values = pos_query_doc_dict.get(sq)
                    selected_docs.extend(values)

                selected_docs = [selected_docs[i] for i in
                                 sorted(random.sample(range(len(selected_docs)), self.num_neg_samples))]

                for d in selected_docs:
                    line = q + '@' + d + '@' + '0'
                    fout.write(line + '\n')

        return output_file

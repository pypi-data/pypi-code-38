import os
import shutil
import tempfile
from subprocess import DEVNULL, Popen


class ExactCover:

    def __init__(self, bitstrings, cover_string_length):
        self.bitstrings = bitstrings
        self.cover_string_length = cover_string_length

    def exact_cover(self):
        try:
            for res in self.exact_cover_gurobi():
                yield res
        except Exception as exc:
            raise RuntimeError(
                "Gurobi may not be installed and there are no alternative "
                "solution method at the moment.") from exc

    def _call_Popen(self, inp, outp):
        return Popen('gurobi_cl ResultFile=%s %s' % (outp, inp), shell=True,
                     stdout=DEVNULL)

    def exact_cover_gurobi(self):
        tdir = None
        used = set()
        anything = False
        try:
            tdir = str(tempfile.mkdtemp(prefix='combcov_tmp'))
            inp = os.path.join(tdir, 'inp.lp')
            outp = os.path.join(tdir, 'out.sol')

            with open(inp, 'w') as lp:
                lp.write('Minimize %s\n' % ' + '.join(
                    'x%d' % i for i in range(len(self.bitstrings))))
                lp.write('Subject To\n')

                for i in range(self.cover_string_length):
                    here = []
                    for j in range(len(self.bitstrings)):
                        if (self.bitstrings[j] & (1 << i)) != 0:
                            here.append(j)
                    lp.write(
                        '    %s = 1\n' % ' + '.join('x%d' % x for x in here))

                lp.write('Binary\n')
                lp.write('    %s\n' % ' '.join(
                    'x%d' % i for i in range(len(self.bitstrings))))
                lp.write('End\n')

            p = self._call_Popen(inp, outp)
            assert p.wait() == 0

            with open(outp, 'r') as sol:
                while True:
                    line = sol.readline()
                    if not line:
                        break
                    if line.startswith('#') or not line.strip():
                        continue
                    anything = True

                    k, v = line.strip().split()
                    if int(v) == 1:
                        used.add(int(k[1:]))
        finally:
            if tdir is not None:
                shutil.rmtree(tdir)

        if anything:
            yield sorted(used)

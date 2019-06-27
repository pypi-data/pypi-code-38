from Genome import Genome
from Benchmark import Benchmark

NUM_TEST = 10000

genome = Genome('data/P2MC7N8HCE3K_chr2L.bedgraph', 'chr2L', 100)

# Benchmark(genome, NUM_TEST, 512, 512, 'data/P2MC7N8HCE3K.bw', 'approx')

genome.stats_from_file('intervals.txt', 'out.txt', 'approx_mean')

intervals = [
    [0, 100],
    [101, 200],
    [4, 100],
    [100000, 999999]
]


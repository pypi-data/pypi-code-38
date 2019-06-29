# requires: pytest, pytest-benchmark, memory_profiler, pycallgraph, faker

import random
import memory_profiler
import pycallgraph
import faker
import csvmatch
import tests

def generated():
    fake = faker.Faker('en_GB')
    matches = [[fake.name(), fake.street_address()] for _ in range(0, 2500)]
    headers1 = ['name', 'street']
    data1 = matches + [[fake.name(), fake.street_address()] for _ in range(0, 2500)]
    random.shuffle(data1) # in-place
    headers2 = ['person', 'place']
    data2 = matches + [[fake.name(), fake.street_address()] for _ in range(0, 2500)]
    random.shuffle(data2) # in-place
    results, keys = csvmatch.run(data1, headers1, data2, headers2)
    assert keys == ['name', 'street', 'person', 'place']
    assert list(results).sort() == [row + row for row in matches].sort()

def test_speed_benchmark_simple(benchmark):
    benchmark(tests.test_simple)

def test_speed_benchmark_fields(benchmark):
    benchmark(tests.test_fields)

def test_speed_benchmark_join_full_outer(benchmark):
    benchmark(tests.test_join_full_outer)

def test_speed_benchmark_generated(benchmark):
    benchmark(generated)

# def test_speed_profile_simple():
#     visualisation = pycallgraph.output.GraphvizOutput()
#     visualisation.output_file = 'profile-simple.png'
#     with pycallgraph.PyCallGraph(output=visualisation):
#         tests.test_simple()

# def test_speed_profile_fields():
#     visualisation = pycallgraph.output.GraphvizOutput()
#     visualisation.output_file = 'profile-fields.png'
#     with pycallgraph.PyCallGraph(output=visualisation):
#         tests.test_fields()

# def test_speed_profile_join_full_outer():
#     visualisation = pycallgraph.output.GraphvizOutput()
#     visualisation.output_file = 'profile-join-full-outer.png'
#     with pycallgraph.PyCallGraph(output=visualisation):
#         tests.test_join_full_outer()

# def test_speed_profile_multiprocess():
#     visualisation = pycallgraph.output.GraphvizOutput()
#     visualisation.output_file = 'profile-multiprocess.png'
#     with pycallgraph.PyCallGraph(output=visualisation):
#         tests.test_multiprocess()

# def test_speed_profile_generated():
#     visualisation = pycallgraph.output.GraphvizOutput()
#     visualisation.output_file = 'profile-generated.png'
#     with pycallgraph.PyCallGraph(output=visualisation):
#         generated()

# def test_memory_threshold_simple():
#     usage = memory_profiler.memory_usage(tests.test_simple)
#     mean = sum(usage) / float(len(usage))
#     assert mean < 0 #33 # in megabytes

# def test_memory_threshold_fields():
#     usage = memory_profiler.memory_usage(tests.test_fields)
#     mean = sum(usage) / float(len(usage))
#     assert mean < 0 #33 # in megabytes

# def test_memory_threshold_join_full_outer():
#     usage = memory_profiler.memory_usage(tests.test_join_full_outer)
#     mean = sum(usage) / float(len(usage))
#     assert mean < 0 #33 # in megabytes

# def test_memory_threshold_multiprocess():
#     usage = memory_profiler.memory_usage(tests.test_multiprocess)
#     mean = sum(usage) / float(len(usage))
#     assert mean < 0 #33 # in megabytes

# def test_memory_threshold_generated():
#     usage = memory_profiler.memory_usage(generated)
#     mean = sum(usage) / float(len(usage))
#     assert mean < 0 #40 # in megabytes

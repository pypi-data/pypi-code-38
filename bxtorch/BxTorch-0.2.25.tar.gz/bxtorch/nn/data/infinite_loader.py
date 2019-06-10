#
#  nn/data/infinite_loader.py
#  bxtorch
#
#  Created by Oliver Borchert on May 20, 2019.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#  

import os
import sys
import torch
import torch.multiprocessing as mp
from bxtorch.utils.torch import share_memory, pin_memory

def _default_collate_fn(items):
    return torch.stack(items)

class InfiniteDataLoader:
    """
    The infinite data loader works analogously to PyTorch's DataLoader. However,
    instead of being provided with a fixed-size dataset, it uses an infinite
    dataset from which infinitely many items can be sampled.
    """

    # MARK: Initialization
    def __init__(self, dataset, batch_size=1, num_workers=0, prefetch=3,
                 pin_memory=False, collate_fn=_default_collate_fn):
        """
        Initializes a new infinite data loader.

        Parameters:
        -----------
        - dataset: bxtorch.nn.InfiniteDataset
            The infinite dataset to sample from.
        - batch_size: int
            The number of items to use in every batch.
        - num_workers: int
            The number of workers to use for loading data. If set to 0, items
            are sampled from the dataset on the main thread. Otherwise, as many
            workers are used on background threads to sample from the dataset
            collaboratively. If set to None, the number of workers equals the
            number of cores on the computer.
        - prefetch: int, default: 3
            A number indicating how many batches should be precomputed at any
            given time.
        - pin_memory: bool, default: False
            Whether to pin data in CUDA pinned memory.
        - collate_fn: func (objects) -> torch.Tensor
            The function used to aggregate samples obtained from a dataset to
            a batch.
        """
        assert prefetch >= 1, "The prefetch must be at least 1."

        self.dataset = dataset
        self.iterator = iter(dataset)
        self.batch_size = batch_size
        self.pin_memory = pin_memory
        self.collate_fn = collate_fn

        if num_workers is None:
            self.num_workers = os.cpu_count()
        else:
            self.num_workers = num_workers
        
        if self.num_workers != 0:
            self.distribution_queue = mp.Queue()
            self.worker_queue = mp.Queue()
            self.result_queue = mp.Queue()
            self.batch_queue = mp.Queue()

            # 1) Initialize distributer
            self.distributer = mp.Process(
                target=_distribution_function,
                args=(self.num_workers, self.distribution_queue,
                      self.worker_queue)
            )
            self.distributer.daemon = True
            self.distributer.start()

            # 2) Initialize workers
            self.workers = []
            for _ in range(self.num_workers):
                worker = mp.Process(
                    target=_worker_function,
                    args=(self.iterator, self.worker_queue, self.result_queue,
                          self.pin_memory)
                )
                worker.daemon = True
                worker.start()
                self.workers.append(worker)

            # 3) Initialize aggregator
            self.aggregator = mp.Process(
                target=_aggregator_function,
                args=(self.batch_size, self.result_queue, self.batch_queue,
                      self.collate_fn)
            )
            self.aggregator.daemon = True
            self.aggregator.start()

            # 4) Prefetch data
            self.prefetch = prefetch
            self.expected_batch_count = 0
            self._prefetch_batch(
                decrement=False
            )

    # MARK: Private Methods
    def _prefetch_batch(self, decrement=True):
        if decrement:
            self.expected_batch_count -= 1
        if self.expected_batch_count < self.prefetch:
            num = self.batch_size * self.prefetch
            self.expected_batch_count += self.prefetch
        else:
            return
        self.distribution_queue.cancel_join_thread()
        self.distribution_queue.put(num)

    # MARK: Special Methods
    def __iter__(self):
        return self

    def __next__(self):
        if self.num_workers == 0:
            items = [next(self.iterator) for _ in range(self.batch_size)]
            return self.collate_fn(items)
        else:
            self._prefetch_batch()
            return self.batch_queue.get()

    def __del__(self):
        if hasattr(self, 'workers'):
            # 1) Shutdown distributer
            self.distribution_queue.put(None)
            self.distribution_queue.close()

            # 2) Shutdown workers
            for _ in range(self.num_workers):
                self.worker_queue.put(None)
            self.worker_queue.close()

            # 3) Shutdown aggregator
            self.result_queue.put(None)
            self.result_queue.close()
            self.batch_queue.close()

            # 4) Ensure graceful shutdown
            for worker in self.workers:
                worker.join()
            self.aggregator.join()


def _distribution_function(num_workers, distribution_queue, worker_queue):
    while True:
        num = distribution_queue.get()
        if num is None:
            return
        length = num // num_workers
        for i in range(num_workers):
            if i == num_workers - 1:
                count = num - length * (num_workers - 1)
            else:
                count = length
            worker_queue.cancel_join_thread()
            worker_queue.put(count)

def _worker_function(generator, worker_queue, result_queue, pin_memory):
    while True:
        num_samples = worker_queue.get()
        if num_samples is None:
            return

        items = [next(generator) for _ in range(num_samples)]
        if pin_memory:
            items = pin_memory(items)
        else:
            items = share_memory(items)

        result_queue.cancel_join_thread()
        result_queue.put(items)
    
def _aggregator_function(batch_size, result_queue, batch_queue, collate_fn):
    int_result = None
    count = 0
    while True:

        while count < batch_size:
            items = result_queue.get()

            if items is None:
                return
            
            if int_result is None:
                int_result = items
            else:
                int_result += items

            count += len(items)

        batch = int_result[:batch_size]
        int_result = int_result[batch_size:]
        count -= batch_size

        batch_queue.cancel_join_thread()
        batch_queue.put(collate_fn(batch))

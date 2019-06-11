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
            if self.pin_memory:
                self.unpinned_result_queue = mp.Queue()
            self.result_queue = mp.Queue()

            if self.pin_memory:
                worker_result_queue = self.unpinned_result_queue
            else:
                worker_result_queue = self.result_queue

            # 1) Initialize distributer
            self.distributer = mp.Process(
                target=_distribution_function,
                args=(self.num_workers, self.distribution_queue,
                      self.worker_queue, self.batch_size)
            )
            self.distributer.daemon = True
            self.distributer.start()

            # 2) Initialize workers
            self.workers = []
            for _ in range(self.num_workers):
                worker = mp.Process(
                    target=_worker_function,
                    args=(self.iterator, self.worker_queue, worker_result_queue,
                          self.collate_fn)
                )
                worker.daemon = True
                worker.start()
                self.workers.append(worker)

            # 3) Initialize pin memory thread if needed
            if self.pin_memory:
                self.pinner = mp.Process(
                    target=_pin_memory_function,
                    args=(self.unpinned_result_queue, self.result_queue)
                )
                self.pinner.daemon = True
                self.pinner.start()

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
            num_batches = self.prefetch - self.expected_batch_count
            self.expected_batch_count += num_batches
        else:
            return

        self.distribution_queue.cancel_join_thread()
        self.distribution_queue.put(num_batches)

    # MARK: Special Methods
    def __iter__(self):
        return self

    def __next__(self):
        if self.num_workers == 0:
            items = [next(self.iterator) for _ in range(self.batch_size)]
            result = self.collate_fn(items)
            if self.pin_memory:
                return pin_memory(result)
            return result
        else:
            self._prefetch_batch()
            return self.result_queue.get()

    def __del__(self):
        if hasattr(self, 'workers'):
            # 1) Shutdown distributer
            self.distribution_queue.put(None)
            self.distribution_queue.close()

            # 2) Shutdown workers
            for _ in range(self.num_workers):
                self.worker_queue.put(None)
            self.worker_queue.close()

            # 3) Shutdown pinner
            if self.pin_memory:
                self.unpinned_result_queue.put(None)
                self.unpinned_result_queue.close()
            self.result_queue.close()

            # 4) Ensure graceful shutdown
            for worker in self.workers:
                worker.join()
            if self.pin_memory:
                self.pinner.join()


def _distribution_function(num_workers, distribution_queue, worker_queue, 
                           batch_size):
    while True:
        num_batches = distribution_queue.get()
        if num_batches is None:
            return

        for _ in range(num_batches):
            worker_queue.cancel_join_thread()
            worker_queue.put(batch_size)


def _worker_function(generator, worker_queue, result_queue, collate_fn):
    while True:
        num_samples = worker_queue.get()
        if num_samples is None:
            return

        items = [next(generator) for _ in range(num_samples)]
        result = collate_fn(items)

        result_queue.cancel_join_thread()
        result_queue.put(result)
    

def _pin_memory_function(unpinned_queue, result_queue):
    while True:
        sample = unpinned_queue.get()
        if sample is None:
            return

        pinned = pin_memory(sample)

        result_queue.cancel_join_thread()
        result_queue.put(pinned)

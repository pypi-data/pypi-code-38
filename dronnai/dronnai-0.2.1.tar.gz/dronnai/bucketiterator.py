from torchtext.data import Iterator
import random



class BucketIterator(Iterator):
    '''
    BucketIterator is torchtext Iterator which has capability to reduce padding and sorting batches in epochs
    '''
    def create_batches(self):
        self.batches = self.pool(self.data(), self.batch_size,
                                self.sort_key, self.batch_size_fn,
                                random_shuffler=self.random_shuffler,
                                shuffle=self.shuffle)

    def batch(self, data, batch_size, batch_size_fn=None):
        if batch_size_fn is None:
            batch_size_fn = lambda new, count, sofar: count
        minibatch, size_so_far = [], 0
        for ex in data:
            minibatch.append(ex)
            size_so_far = batch_size_fn(ex, len(minibatch), size_so_far)
            if size_so_far == batch_size:
                yield minibatch
                minibatch, size_so_far = [], 0
            elif size_so_far > batch_size:
                yield minibatch[:-1]
                minibatch, size_so_far = minibatch[-1:], batch_size_fn(ex, 1, 0)
        if minibatch:
            yield minibatch

    def pool(self, data, batch_size, key, batch_size_fn,
             random_shuffler,shuffle):
        p_batch = self.batch(sorted(data, key=key), batch_size, batch_size_fn)
        if shuffle:
            for b in random_shuffler(list(p_batch)):
                yield b
        else:
            for b in list(p_batch):
                yield b
                
    def __len__(self):
        p_batch = self.batch(sorted(self.data(), key=self.sort_key), self.batch_size, self.batch_size_fn)
        return len(list(p_batch))
    
def conf_bsf(batch_size,field_name):
    '''
    configurator of batch size function which help us to utilize all GPU card capability by creating batch based on number of tokens
    batch_size - how many tokens should appear with every batch
    field_name - field_name in torchtext Iterator base on which batch_size should be computed
    '''
    def bsf(new, count, sofar):
        '''
        new - batch example which will be added to batch
        count - the true size of batch
        sofar - the size on batch computing by this function after previous example

        return new batch size bese which is sum of exaples lengths (sum of tokens in batch)
        '''
        example_len = len(getattr(new,field_name))
        if count == 1 and example_len > batch_size:
            return batch_size
        if count == 1 or sofar/(count-1) == example_len:
            return example_len+sofar
        else:
            return example_len+sofar+(count-1)*(example_len-sofar/(count-1))
    return bsf
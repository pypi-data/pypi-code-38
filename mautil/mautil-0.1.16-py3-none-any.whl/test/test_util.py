from base_test_class import Test
from mautil import util
import numpy as np
import unittest


class TestUtil(Test):
    def gen_score(self, target_inds, N, beam_ids= None):
        batch_size, beam_size, max_len = target_inds.shape
        #scores = np.zeros([batch_size, beam_size, max_len, N])
        scores = []
        #max_scores = np.zeros([batch_size, 1])
        max_scores = np.zeros([batch_size, beam_size])
        if beam_ids is None:
            beam_ids = np.arange(beam_size)
        for step in range(max_len):
            #step_scores = scores[:,:,step,:]
            step_scores = np.zeros([batch_size, beam_size, N])
            inds = target_inds[:, :, step:step+1]
            #beam_scores = max_scores + np.expand_dims(np.arange(beam_size)+1, 0)*0.01
            beam_scores = np.max(max_scores, -1, keepdims=True) + np.expand_dims(np.arange(beam_size)+1, 0)*0.01
            #np.random.shuffle(beam_ids)
            #step_scores[np.arange(batch_size)[:,None,None], np.arange(beam_size)[None,:,None], inds] += np.expand_dims(beam_scores, -1)
            step_scores[np.arange(batch_size)[:,None,None], beam_ids[None,:,None], inds] = np.expand_dims(beam_scores-max_scores[:, beam_ids], -1)
            scores.append(step_scores)
            #max_scores = np.max(beam_scores, -1, keepdims=True)
            max_scores = beam_scores
        return np.stack(scores,2)
        
    def test_beam_search(self):
        N = 6
        inds = [];
        inds.append([[1,1,1],[2,3,5],[0,0,1],[0,3,4]])
        inds.append([[2,2,2],[1,2,4],[1,1,1],[2,1,4]])
        inds = np.stack(inds, 1)
        scores = self.gen_score(inds, N)

        cross_beam_inds = []
        cross_beam_inds.append([[0,2,3]])
        cross_beam_inds.append([[1,1,4]])
        cross_beam_inds = np.stack(cross_beam_inds, 1)
        beam_ids = np.array([0,0])
        cross_beam_scores = self.gen_score(np.array(cross_beam_inds), N, beam_ids)
        cross_beam_inds[-1][-1] = np.array([0,2,4]) # correct it from first beam id
        scores = np.concatenate([scores, cross_beam_scores], 0)
        target_inds = np.concatenate([inds, cross_beam_inds], 0)

        target_lens = np.array([[0, 3],[3, 0],[2, 0],[3, 1],[3, 3]])
        print('scores is {}'.format(scores))
        print('target lens is {}'.format(target_lens))

        batch_size, beam_size, max_len = target_inds.shape
        inputs = np.zeros([batch_size, beam_size, max_len, 10])
        init_inds = np.array([-1] * batch_size)
                    
        stop = 1
        cnt = 0
        def loop_func(inp, inds):
            nonlocal cnt
            next_inputs = inputs[:, cnt%beam_size, cnt//beam_size, :]
            next_scores = scores[:, cnt%beam_size, cnt//beam_size, :]
            cnt += 1
            return next_scores, next_inputs
    
        inds, lens = util.beam_search(loop_func, beam_size, max_len, inputs[:,0,0,:], init_inds, stop=stop, return_top=False)
        print('beam search inds is {}'.format(inds))
        print('beam search lens is {}'.format(lens))
        assert np.all(np.array(target_inds)==inds)
        assert np.all(np.array(target_lens)==lens)
        

if  __name__ == "__main__":
    unittest.main()
    
        
        

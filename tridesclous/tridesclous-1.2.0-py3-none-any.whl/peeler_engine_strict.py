import time
import numpy as np


from .peeler_tools import *
from .peeler_tools import _dtype_spike
from .tools import make_color_dict
from . import signalpreprocessor
from .peakdetector import  detect_peaks_in_chunk



from .peeler_engine_classic import PeelerEngineClassic

# this should be an attribute
maximum_jitter_shift = 4


class PeelerEngineStrict(PeelerEngineClassic):
    def classify_and_align_one_spike(self, local_index, residual, catalogue):
        # local_index is index of peaks inside residual and not
        # the absolute peak_pos. So time scaling must be done outside.
        
        width = catalogue['peak_width']
        n_left = catalogue['n_left']
        #~ alien_value_threshold = catalogue['clean_waveforms_params']['alien_value_threshold']
        
        
        #ind is the windows border!!!!!
        ind = local_index + n_left

        if ind+width+maximum_jitter_shift+1>=residual.shape[0]:
            # too near right limits no label
            label = LABEL_RIGHT_LIMIT
            jitter = 0
        elif ind<=maximum_jitter_shift:
            # too near left limits no label
            #~ print('     LABEL_LEFT_LIMIT', ind)
            label = LABEL_LEFT_LIMIT
            jitter = 0
        elif catalogue['centers0'].shape[0]==0:
            # empty catalogue
            label  = LABEL_UNCLASSIFIED
            jitter = 0
        else:
            waveform = residual[ind:ind+width,:]
            
            if self.alien_value_threshold is not None and \
                    np.any(np.abs(waveform)>self.alien_value_threshold) :
                label  = LABEL_ALIEN
                jitter = 0
            else:
                
                #~ t1 = time.perf_counter()
                label, jitter = self.estimate_one_jitter(waveform)
                #~ t2 = time.perf_counter()
                #~ print('  estimate_one_jitter', (t2-t1)*1000.)

                #~ jitter = -jitter
                #TODO debug jitter sign is positive on right and negative to left
                
                #~ print('label, jitter', label, jitter)
                
                # if more than one sample of jitter
                # then we try a peak shift
                # take it if better
                #TODO debug peak shift
                if np.abs(jitter) > 0.5 and label >=0:
                    prev_ind, prev_label, prev_jitter =ind, label, jitter
                    
                    shift = -int(np.round(jitter))
                    #~ print('classify and align shift', shift)
                    
                    if np.abs(shift) >maximum_jitter_shift:
                        #~ print('     LABEL_MAXIMUM_SHIFT avec shift')
                        label = LABEL_MAXIMUM_SHIFT
                    else:
                        ind = ind + shift
                        if ind+width>=residual.shape[0]:
                            #~ print('     LABEL_RIGHT_LIMIT avec shift')
                            label = LABEL_RIGHT_LIMIT
                        elif ind<0:
                            #~ print('     LABEL_LEFT_LIMIT avec shift')
                            label = LABEL_LEFT_LIMIT
                            #TODO: force to label anyway the spike if spike is at the left of FIFO
                        else:
                            waveform = residual[ind:ind+width,:]
                            new_label, new_jitter = self.estimate_one_jitter(waveform)
                            if np.abs(new_jitter)<np.abs(prev_jitter):
                                print('  keep shift', 'new_label', new_label, 'new_jitter', new_jitter, 'prev_label', prev_label, 'prev_jitter', prev_jitter)
                                label, jitter = new_label, new_jitter
                                local_index += shift
                            else:
                                print('  no keep shift worst jitter')
                                pass

        #security if with jitter the index is out
        if np.abs(jitter)<0.5 and  label>=0:
            local_pos = local_index - np.round(jitter).astype('int64') + n_left
            if local_pos<0:
                label = LABEL_LEFT_LIMIT
            elif (local_pos+width) >=residual.shape[0]:
                label = LABEL_RIGHT_LIMIT
        else:
            label = LABEL_UNCLASSIFIED
        
        return Spike(local_index, label, jitter)


    def estimate_one_jitter(self, waveform):
        """
        Estimate the jitter for one peak given its waveform
        
        Method proposed by Christophe Pouzat see:
        https://hal.archives-ouvertes.fr/hal-01111654v1
        http://christophe-pouzat.github.io/LASCON2016/SpikeSortingTheElementaryWay.html
        
        for best reading (at least for me SG):
          * wf = the wafeform of the peak
          * k = cluster label of the peak
          * wf0, wf1, wf2 : center of catalogue[k] + first + second derivative
          * jitter0 : jitter estimation at order 0
          * jitter1 : jitter estimation at order 1
          * h0_norm2: error at order0
          * h1_norm2: error at order1
          * h2_norm2: error at order2
        """
        
        # This line is the slower part !!!!!!
        # cluster_idx = np.argmin(np.sum(np.sum((catalogue['centers0']-waveform)**2, axis = 1), axis = 1))
        
        catalogue = self.catalogue
        
        if self.use_opencl_with_sparse:
            rms_waveform_channel = np.sum(waveform**2, axis=0).astype('float32')
            
            pyopencl.enqueue_copy(self.queue,  self.one_waveform_cl, waveform)
            pyopencl.enqueue_copy(self.queue,  self.rms_waveform_channel_cl, rms_waveform_channel)
            event = self.kern_waveform_distance(self.queue,  self.cl_global_size, self.cl_local_size,
                        self.one_waveform_cl, self.catalogue_center_cl, self.mask_cl, 
                        self.rms_waveform_channel_cl, self.waveform_distance_cl)
            pyopencl.enqueue_copy(self.queue,  self.waveform_distance, self.waveform_distance_cl)
            cluster_idx = np.argmin(self.waveform_distance)

        elif self.use_pythran_with_sparse:
            s = pythran_tools.pythran_loop_sparse_dist(waveform, 
                                catalogue['centers0'],  catalogue['sparse_mask'])
            cluster_idx = np.argmin(s)
        else:
            # replace by this (indentique but faster, a but)
            
            #~ t1 = time.perf_counter()
            d = catalogue['centers0']-waveform[None, :, :]
            d *= d
            #s = d.sum(axis=1).sum(axis=1)  # intuitive
            #s = d.reshape(d.shape[0], -1).sum(axis=1) # a bit faster
            s = np.einsum('ijk->i', d) # a bit faster
            cluster_idx = np.argmin(s)
            #~ t2 = time.perf_counter()
            #~ print('    np.argmin V2', (t2-t1)*1000., cluster_idx)
        

        k = catalogue['cluster_labels'][cluster_idx]
        chan = catalogue['max_on_channel'][cluster_idx]
        #~ print('cluster_idx', cluster_idx, 'k', k, 'chan', chan)

        
        #~ return k, 0.

        wf0 = catalogue['centers0'][cluster_idx,: , chan]
        wf1 = catalogue['centers1'][cluster_idx,: , chan]
        wf2 = catalogue['centers2'][cluster_idx,: , chan]
        wf = waveform[:, chan]
        #~ print()
        #~ print(wf0.shape, wf.shape)
        
        
        #it is  precompute that at init speedup 10%!!! yeah
        #~ wf1_norm2 = wf1.dot(wf1)
        #~ wf2_norm2 = wf2.dot(wf2)
        #~ wf1_dot_wf2 = wf1.dot(wf2)
        wf1_norm2= catalogue['wf1_norm2'][cluster_idx]
        wf2_norm2 = catalogue['wf2_norm2'][cluster_idx]
        wf1_dot_wf2 = catalogue['wf1_dot_wf2'][cluster_idx]
        
        
        h = wf - wf0
        h0_norm2 = h.dot(h)
        h_dot_wf1 = h.dot(wf1)
        jitter0 = h_dot_wf1/wf1_norm2
        h1_norm2 = np.sum((h-jitter0*wf1)**2)
        #~ print(h0_norm2, h1_norm2)
        #~ print(h0_norm2 > h1_norm2)
        
        
        
        if h0_norm2 > h1_norm2:
            #order 1 is better than order 0
            h_dot_wf2 = np.dot(h,wf2)
            rss_first = -2*h_dot_wf1 + 2*jitter0*(wf1_norm2 - h_dot_wf2) + 3*jitter0**2*wf1_dot_wf2 + jitter0**3*wf2_norm2
            rss_second = 2*(wf1_norm2 - h_dot_wf2) + 6*jitter0*wf1_dot_wf2 + 3*jitter0**2*wf2_norm2
            jitter1 = jitter0 - rss_first/rss_second
            #~ h2_norm2 = np.sum((h-jitter1*wf1-jitter1**2/2*wf2)**2)
            #~ if h1_norm2 <= h2_norm2:
                #when order 2 is worse than order 1
                #~ jitter1 = jitter0
        else:
            jitter1 = 0.
        #~ print('jitter1', jitter1)
        #~ return k, 0.
        
        #~ print(np.sum(wf**2), np.sum((wf-(wf0+jitter1*wf1+jitter1**2/2*wf2))**2))
        #~ print(np.sum(wf**2) > np.sum((wf-(wf0+jitter1*wf1+jitter1**2/2*wf2))**2))
        #~ return k, jitter1

        if np.max(np.abs(wf-(wf0+jitter1*wf1+jitter1**2/2*wf2)))< 6.:
        #~ if np.sum(wf**2) > np.sum((wf-(wf0+jitter1*wf1+jitter1**2/2*wf2))**2):
            #prediction should be smaller than original (which have noise)
            return k, jitter1
        else:
            #otherwise the prediction is bad
            #~ print('bad prediction')
            return LABEL_UNCLASSIFIED, 0.

        
        #~ if np.abs(jitter1)<0.5:
            #~ print('short')
            #~ r = catalogue['subsample_ratio']
            #~ shift = -int(np.round(jitter1))
            #~ int_jitter = int((jitter1+shift)*r) + r//2
            #~ pred = catalogue['interp_centers0'][cluster_idx, int_jitter::r, chan]
            
            
            #~ if np.max(np.abs(wf-pred))< 5.:
                #~ return k, jitter1
            #~ else:
                #~ #otherwise the prediction is bad
                #~ return LABEL_UNCLASSIFIED, 0.
        #~ else:
            #~ print('long')
            
            #~ # same rules as classical peeler
            #~ if np.sum(wf**2) > np.sum((wf-(wf0+jitter1*wf1+jitter1**2/2*wf2))**2):
                #~ #prediction should be smaller than original (which have noise)
                #~ return k, jitter1
            #~ else:
                #~ #otherwise the prediction is bad
                #~ print('bad prediction')
                #~ return LABEL_UNCLASSIFIED, 0.

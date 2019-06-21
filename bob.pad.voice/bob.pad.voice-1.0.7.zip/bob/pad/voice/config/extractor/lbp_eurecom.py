
import bob.bio.spear.extractor

"""
This LBP-based feature extraction is implemented based on the paper
Federico Alegre, Ravichander Vipperla, Asmaa Amehraye, Nicholas Evans.
"A new speaker verification spoofing countermeasure based on local binary patterns".
INTERSPEECH 2013, 14th Annual Conference of the International Speech Communication Association, Lyon: France (2013)

According to the paper, lbp_uniform LBP_8,1 is computed on the whole spectrogram, which consists of 51 coefficients
(16 LFCCs, energy, plus their delta and delta-delta). Histograms are computed for each row of the resulted LBP 'textogram'
of the signal. Histogram size is 58 (as lbp_uniform LBP8,1 has 58 different values) and number of rows are (51-2), since
GLCMs are not computed for top and bottom row of the spectrogram. Hence, the resulted size of the feature vector is 2842.
"""

lfcc16_eurecom = bob.bio.spear.extractor.CepstralExtended(
    # the parameters are as specified in the paper by Eurecom
    # Federico Alegre, Ravichander Vipperla, Asmaa Amehraye, Nicholas Evans.
    # "A new speaker verification spoofing countermeasure based on local binary patterns".
    # INTERSPEECH 2013, 14th Annual Conference of the International Speech Communication Association, Lyon: France (2013)

    n_ceps=16, # they used 16
    n_filters=24,
    mel_scale=False,
    with_delta=True,  # As reported in the paper
    with_delta_delta=True,  # As reported in the paper
    # together with deltas and delta-deltas, it gives (16*3+1)=53 features,
    # which is different from how they computed features (they have 51)
    with_energy=True,
    win_length_ms=20.,  # 20 ms
    win_shift_ms=10.,  # 10 ms
)


extractor = bob.pad.voice.extractor.LBPHistograms(
    features_processor = lfcc16_eurecom,
    n_lbp_histograms=1,
    lbp_neighbors=8,
    lbp_to_average=False,
    lbp_uniform=True,
    lbp_radius=1,
    lbp_circular=True,
    lbp_elbp_type='regular',
    histograms_for_rows=True,  # this flag triggers computation of histograms for each row
)

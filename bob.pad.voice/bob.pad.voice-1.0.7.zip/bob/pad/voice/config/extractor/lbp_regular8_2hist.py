
import bob.pad.voice.extractor

spectral_bands = bob.pad.voice.extractor.SpectrogramExtended(
    win_length_ms=20.,  # 20 ms
    win_shift_ms=10.,  # 10 ms
    n_filters=40,
    f_min=0.0,  # 0 Hz
    f_max=4000,  # 4 KHz
    pre_emphasis_coef=1.0,
    mel_scale=True,
    rect_filter=False,
    inverse_filter=False,
    normalize_spectrum=False,
    log_filter=True,
    energy_filter=False,
    energy_bands=True,
    vad_filter="trim_silence",
    normalize_feature_vector=False,
)

extractor = bob.pad.voice.extractor.LBPHistograms(
    features_processor = spectral_bands,
    n_lbp_histograms=2,
    lbp_neighbors=8,
    lbp_to_average=False,
    lbp_uniform=False,
    lbp_radius=1,
    lbp_circular=True,
    lbp_elbp_type='regular',
    histograms_for_rows=False,
)



import bob.pad.voice.extractor

spectral_bands = bob.pad.voice.extractor.SpectrogramExtended(
    n_filters=20,
    win_length_ms=20.,  # 20 ms
    win_shift_ms=10.,  # 10 ms
    f_min=0.0,  # 0 Hz
    f_max=8000, #this number insures we take half of the frequencies after FFT - so we retain only 257 values for 512 window
    pre_emphasis_coef=0.97,
    mel_scale=True, # seems to give better results than linear scaling
    rect_filter=False,
    inverse_filter=False,
    normalize_spectrum=False,
    log_filter=True,
    energy_filter=False,
    energy_bands=True,
    vad_filter="trim_silence",
    normalize_feature_vector=False,
)

extractor = bob.pad.voice.extractor.Ratios(
    features_processor=spectral_bands,
    n_bands=2,  # ratio between higher and lower halves of the spectrum
)


from rnngen.processing.preprocessing import ProcessData


def process(save_pickle_dir, use_text_dir):
    # Create processed data
    ProcessData(save_pickle_dir, use_text_dir)

from tqdm import tqdm
import requests

import pickle

import torch
from pytorch_pretrained_bert import BertTokenizer, BertModel, BertForMaskedLM

class XGBert:
    def __init__(self, model_name='bert-base-uncased', cuda=False):
        self.model_name = model_name
        self.cuda = cuda
        self.tokenizer, self.model = load_model()
        self.sep_idx = self.tokenizer.vocab['[SEP]']

    def load_model(self):
        tokenizer = BertTokenizer.from_pretrained(self.model_name)
        model = BertModel.from_pretrained(self.model_name)
        model.eval()
        return tokenizer, model

    def tensorize(self, *sentences):
        assert len(sentences) <= 2, "Currenlty, only supports one and/or two sentences."
        # Create the expected BERT text input.
        text = '[CLS] ' + ' [SEP] '.join(filter(None.__ne__, sentences)) + ' [SEP]'
        # Tokenize text.
        tokenized_text = self.tokenizer.tokenize(text)
        indexed_tokens = tokenizer.convert_tokens_to_ids(tokenized_text)
        # Find the [SEP] locations.
        sep_locations = np.where(np.array(indexed_tokens) == self.sep_idx)[0]
        segments_tensors = np.repeat(np.arange(sep_locations.size), sep_locations)
        sep_loc = indexed_tokens.index(sep_idx)
        segments_ids = [0] * sep_loc + [1] * (len(tokenized_text) - sep_loc)
        return torch.tensor([indexed_tokens]), torch.tensor([segments_ids])

    def bert_me(self, *sentences):
        tokens_tensor, segments_tensors = self.tensorize(*sentences)
        # Predict hidden states features for each layer
        with torch.no_grad():
            _, pooled_output = model(tokens_tensor, segments_tensors)
        return pooled_output.squeeze()
    

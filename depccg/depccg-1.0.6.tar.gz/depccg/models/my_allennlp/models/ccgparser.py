from typing import Dict, Optional, Tuple, Any, List
import logging

from overrides import overrides
import torch

from allennlp.data import Vocabulary
from allennlp.modules import Seq2SeqEncoder, TextFieldEmbedder
from allennlp.modules import FeedForward
from allennlp.models.model import Model
from allennlp.nn import InitializerApplicator, RegularizerApplicator
from allennlp.data.vocabulary import DEFAULT_OOV_TOKEN, DEFAULT_PADDING_TOKEN

from depccg.models.my_allennlp.nn.bilinear import BilinearWithBias
from depccg.models.my_allennlp.models.supertagger import Supertagger
from depccg.download import CONFIGS, SEMANTIC_TEMPLATES
from depccg.parser import EnglishCCGParser
from depccg.printer import to_string
from depccg.cat import Category


logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


@Model.register("ccgparser")
class CCGParser(Supertagger):
    def __init__(self,
                 vocab: Vocabulary,
                 text_field_embedder: TextFieldEmbedder,
                 encoder: Seq2SeqEncoder,
                 tag_representation_dim: int,
                 arc_representation_dim: int,
                 tag_feedforward: FeedForward = None,
                 arc_feedforward: FeedForward = None,
                 dropout: float = 0.5,
                 input_dropout: float = 0.5,
                 head_tag_temperature: Optional[float] = None,
                 head_temperature: Optional[float] = None,
                 initializer: InitializerApplicator = InitializerApplicator(),
                 regularizer: Optional[RegularizerApplicator] = None,
                 format: str = 'auto',
                 semantic_templates: Optional[str] = None,
                 **kwargs) -> None:
        super(CCGParser, self).__init__(
                vocab, text_field_embedder, encoder, tag_representation_dim,
                arc_representation_dim, tag_feedforward, arc_feedforward, dropout,
                input_dropout, head_tag_temperature, head_temperature, initializer, regularizer)
        self.format = format
        self.semantic_templates = semantic_templates or SEMANTIC_TEMPLATES['en']
        self.parser = EnglishCCGParser.from_json(CONFIGS['en'], **kwargs)
        all_categories = self.vocab.get_index_to_token_vocabulary('head_tags')
        all_categories = [token for _, token in sorted(all_categories.items())]
        categories, paddings = all_categories[2:], all_categories[:2]
        assert all(padding in [DEFAULT_PADDING_TOKEN, DEFAULT_OOV_TOKEN] for padding in paddings)
        self.categories = [Category.parse(category) for category in categories]

    @overrides
    def decode(self, output_dict: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        sentences = output_dict['words']
        head_tags = output_dict.pop('head_tags')
        head_tags = head_tags[:, 1:, 2:]  # discard a sentinel token and padding and unknown tags
        head_tags = head_tags.cpu().detach().numpy()
        heads = output_dict.pop('heads')
        heads = heads[:, 1:]
        heads = heads.cpu().detach().numpy()

        probabilities = []
        for sentence, head_tag, head in zip(sentences, head_tags, heads):
            words = sentence.split(' ')
            length = len(words)
            head_tag = head_tag[:length, :]
            assert head_tag.shape[-1] == len(self.categories)
            head = head[:length, :length+1]
            probabilities.append((head_tag, head))

        trees = self.parser.parse_doc(sentences, probabilities, tag_list=self.categories)
        output_dict['trees'] = to_string(trees,
                                         None,
                                         lang='en',
                                         format=self.format,
                                         semantic_templates=self.semantic_templates)
        return output_dict


# coding=utf-8
# Copyright 2018 The Google AI Language Team Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import tensorflow as tf


class ConfigBase(object):
    """Configuration flags required in all BERT implementations"""

    def __init__(self,
                 use_tpu=False,
                 tpu_name=None,
                 tpu_zone=None,
                 gcp_project=None,
                 master=None,
                 num_tpu_cores=8,
                 *args, **kwargs):
        self.flags = tf.flags
        self.set_tpu_gpu(*args, **kwargs)

    def set_model_paths(self,
                        bert_config_file=None,
                        bert_vocab_file=None,
                        bert_output_dir=None,
                        trained_model_dir=None,
                        *args, **kwargs):
        """Paths to support files required for BERT to run"""
        self.flags.DEFINE_string(
            "bert_config_file", bert_config_file,
            "The config json file corresponding to the pre-trained BERT "
            "model. This specifies the model architecture.")

        self.flags.DEFINE_string(
            "bert_vocab_file", bert_vocab_file,
            "The vocabulary file that the BERT model was trained on.")

        if bert_output_dir is None and trained_model_dir is None:
            raise ValueError("Please specify either 'bert_output_dir', or "
                             "trained_model_dir")
        if bert_output_dir is not None and trained_model_dir is not None:
            raise ValueError("Please specify only 'bert_output_dir', or "
                             "only 'trained_model_dir'")

        if trained_model_dir is not None:
            bert_output_dir = trained_model_dir
        self.flags.DEFINE_string(
            "bert_output_dir", bert_output_dir,
            "The output directory where the model checkpoints will be written")

    def set_model_params(self,
                         init_checkpoint=None,
                         do_lower_case=True,
                         max_seq_length=128,
                         warmup_proportion=0.1,
                         save_checkpoints_steps=1000,
                         iterations_per_loop=1000,
                         num_train_epochs=3.0,
                         batch_size_train=32,
                         batch_size_eval=8,
                         batch_size_predict=8,
                         learning_rate=3e-5):
        """BERT model parameters"""
        self.flags.DEFINE_string(
            "init_checkpoint", init_checkpoint,
            "Initial checkpoint (usually from a pre-trained BERT model).")

        self.flags.DEFINE_bool(
            "do_lower_case", do_lower_case,
            "Whether to lower case the input text. Should be True for uncased "
            "models and False for cased models.")

        self.flags.DEFINE_integer(
            "max_seq_length", max_seq_length,
            "The maximum total input sequence length after WordPiece "
            "tokenization. Sequences longer than this will be truncated, "
            "and sequences shorter than this will be padded.")

        self.flags.DEFINE_float(
            "warmup_proportion", warmup_proportion,
            "Proportion of training to perform linear learning rate warmup "
            "for. E.g., 0.1 = 10% of training.")

        self.flags.DEFINE_integer(
            "save_checkpoints_steps", save_checkpoints_steps,
            "How often to save the model checkpoint.")

        self.flags.DEFINE_integer(
            "iterations_per_loop", iterations_per_loop,
            "How many steps to make in each estimator call.")

        self.flags.DEFINE_float(
            "num_train_epochs", num_train_epochs,
            "Total number of training epochs to perform.")

        self.flags.DEFINE_integer(
            "batch_size_train", batch_size_train,
            "Total batch size for training.")

        self.flags.DEFINE_integer(
            "batch_size_eval", batch_size_eval,
            "Total batch size for eval.")

        self.flags.DEFINE_integer(
            "batch_size_predict", batch_size_predict,
            "Total batch size for predict.")

        self.flags.DEFINE_float(
            "learning_rate", learning_rate,
            "The initial learning rate for Adam.")

    def set_tpu_gpu(self,
                    use_tpu=False,
                    tpu_name=None,
                    tpu_zone=None,
                    gcp_project=None,
                    master=None,
                    num_tpu_cores=8,
                    *args, **kwargs):
        """TPU or GPU/CPU Configuration"""
        self.flags.DEFINE_bool(
            "use_tpu", use_tpu,
            "Whether to use TPU or GPU/CPU.")

        self.flags.DEFINE_string(
            "tpu_name", tpu_name,
            "The Cloud TPU to use for training. This should be either the "
            "name used when creating the Cloud TPU, or a "
            "grpc://ip.address.of.tpu:8470 url.")

        self.flags.DEFINE_string(
            "tpu_zone", tpu_zone,
            "[Optional] GCE zone where the Cloud TPU is located in. If not "
            "specified, we will attempt to automatically detect the GCE "
            "project from metadata.")

        self.flags.DEFINE_string(
            "gcp_project", gcp_project,
            "[Optional] Project name for the Cloud TPU-enabled project. If "
            "not specified, we will attempt to automatically detect the GCE "
            "project from metadata.")

        self.flags.DEFINE_string(
            "master", master,
            "[Optional] TensorFlow master URL.")

        self.flags.DEFINE_integer(
            "num_tpu_cores", num_tpu_cores,
            "Only used if `use_tpu` is True. Total number of TPU cores to use")

    def get_handle(self):
        self.validate_flags_and_config()
        return self.flags.FLAGS

    def validate_flags_and_config(self,):
        self.flags.mark_flag_as_required("bert_vocab_file")
        self.flags.mark_flag_as_required("bert_config_file")
        self.flags.mark_flag_as_required("bert_output_dir")


class ConfigSQuAD(ConfigBase):
    """Configuration flags specific to SQuAD implementations of BERT"""
    def __init__(self,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_model_paths(self,
                        file_to_train=None,
                        file_to_predict=None,
                        *args, **kwargs):
        """Set SQuAD specific files, in addition to BERT files"""
        self.flags.DEFINE_string(
            "file_to_train", file_to_train,
            "SQuAD json for training. E.g., train-v1.1.json")

        self.flags.DEFINE_string(
            "file_to_predict", file_to_predict,
            "SQuAD json for predictions. " +
            "E.g., dev-v1.1.json or test-v1.1.json")

        ConfigBase.set_model_paths(self, *args, **kwargs)

    def set_model_params(self,
                         doc_stride=128,
                         max_query_length=64,
                         n_best_size=20,
                         max_answer_length=30,
                         is_squad_v2=False,
                         verbose_logging=False,
                         null_score_diff_threshold=0.0,
                         *args, **kwargs):
        """Set SQuAD training params"""
        self.flags.DEFINE_integer(
            "doc_stride", doc_stride,
            "When splitting up a long document into chunks, how much stride "
            "to take between chunks.")

        self.flags.DEFINE_integer(
            "max_query_length", max_query_length,
            "The maximum number of tokens for the question. Questions "
            "longer than this will be truncated to this length.")

        self.flags.DEFINE_integer(
            "n_best_size", n_best_size,
            "The total number of n-best predictions to generate in the "
            "nbest_predictions.json output file.")

        self.flags.DEFINE_integer(
            "max_answer_length", max_answer_length,
            "The maximum length of an answer that can be generated. This is "
            "needed because the start and end predictions are not "
            "conditioned on one another")

        """Set non technical SQuAD specific configurations"""
        self.flags.DEFINE_bool(
            "verbose_logging", verbose_logging,
            "If true, all of the warnings related to data processing will "
            "be printed. A number of warnings are expected for a normal "
            "SQuAD evaluation.")

        self.flags.DEFINE_bool(
            "is_squad_v2", is_squad_v2,
            "If true, the SQuAD examples contain some that do not have an "
            "answer.")

        self.flags.DEFINE_float(
            "null_score_diff_threshold", null_score_diff_threshold,
            "If null_score - best_non_null is greater than the threshold "
            "predict null")

        ConfigBase.set_model_params(self, *args, **kwargs)

    def get_handle(self):
        self.validate_flags_and_config()
        return ConfigBase.get_handle(self)

    def validate_flags_and_config(self,):
        """Validate the input FLAGS or throw an exception."""
        FLAGS = self.flags.FLAGS
        if FLAGS.max_seq_length <= FLAGS.max_query_length + 3:
            raise ValueError(
                "The max_seq_length (%d) must be greater "
                "than max_query_length (%d) + 3" %
                (FLAGS.max_seq_length, FLAGS.max_query_length))

        ConfigBase.validate_flags_and_config(self)


class ConfigClassifier(ConfigBase):
    """Configuration flags specific to Classification implementations of BERT
    """
    def __init__(self,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_model_paths(self,
                        data_dir=None,
                        *args, **kwargs):
        # Classification specific files
        self.flags.DEFINE_string(
            "data_dir", data_dir,
            "The input data dir. Should contain the .tsv files "
            "(or other data files) for the task.")

        ConfigBase.set_model_paths(self, *args, **kwargs)

    def set_model_params(self,
                         *args, **kwargs):
        ConfigBase.set_model_params(self, *args, **kwargs)

    def get_handle(self):
        self.validate_flags_and_config()
        return ConfigBase.get_handle(self)

    def validate_flags_or_throw(self,):
        """Validate the input FLAGS or throw an exception."""
        ConfigBase.validate_flags_and_config(self)

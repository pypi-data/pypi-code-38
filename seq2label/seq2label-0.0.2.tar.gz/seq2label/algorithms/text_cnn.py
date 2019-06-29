import tensorflow as tf
from tensorflow.contrib import layers


class TextCNN(object):
    @classmethod
    def default_params(cls):
        return {
            'embed_type': 'rand',
            'filter_sizes': [2, 3, 4],
            "num_filters": 3,
            "max_seq_length": 20,
            "default_value": "<pad>",
            "embedding_vocabulary_size": 128003,
        }

    @classmethod
    def get_model_name(cls):
        return cls.__name__

    @classmethod
    def model_fn(cls, features, labels, mode, params):
        instance = cls(features, labels, mode, params)
        return instance()

    def __init__(self, features, labels, mode, params):
        self.features = features
        self.labels = labels
        self.mode = mode
        self.params = params

        self.dtype = tf.float32

    def __call__(self):
        word_ids, label = self.get_int_from_input()

        embedding_input = self.build_embed(word_ids)
        conv_output = self.build_conv_layers(embedding_input)
        label_prob = self.build_fully_connected_layers(conv_output)

        softmax_label_prob = tf.nn.softmax(label_prob)

        predicted_label_id = self._get_prediction(softmax_label_prob)

        mapping_tensor = self.get_mapping_tensor()

        predicted_label_str = self.get_label_str(predicted_label_id, mapping_tensor)

        loss = None
        train_op = None

        if self.mode != tf.estimator.ModeKeys.PREDICT:
            loss = self._build_loss(softmax_label_prob, label)
            train_op = self._build_optimizer(loss)

        return tf.estimator.EstimatorSpec(
            mode=self.mode,
            loss=loss,
            train_op=train_op,
            # eval_metric_ops=metrics,
            predictions={"label": predicted_label_str, "label_prob": softmax_label_prob, "label_mapping": mapping_tensor})

    def get_int_from_input(self):
        # word to id
        data = self.params['vocab_data']
        mapping_strings = tf.Variable(data)
        vocab_words = tf.contrib.lookup.index_table_from_tensor(
            mapping_strings, num_oov_buckets=1)
        words = self.features['words']
        print(self.features)
        word_ids = vocab_words.lookup(words)

        if self.mode != tf.estimator.ModeKeys.PREDICT:
            # tags to id
            data = self.params['tags_data']
            mapping_strings = tf.Variable(data)
            vocab_tags = tf.contrib.lookup.index_table_from_tensor(mapping_strings)

            print(self.labels)
            label = vocab_tags.lookup(self.labels)
            # label = tf.expand_dims(label, -1)
        else:
            label = None

        return word_ids, label

    def build_embed(self, input_data):
        with tf.variable_scope("embeddings", dtype=self.dtype) as scope:
            embed_type = self.params['embed_type']

            if embed_type == "rand":
                embedding = tf.get_variable(
                        "embedding-rand",
                        [self.params['embedding_vocabulary_size'], self.params['embedding_dim']],
                        self.dtype)
            elif embed_type == "static":
                raise NotImplementedError("CNN-static not implemented yet.")
            elif embed_type == "non-static":
                raise NotImplementedError("CNN-non-static not implemented yet.")
            elif embed_type == "multichannel":
                raise NotImplementedError("CNN-multichannel not implemented yet.")
            else:
                raise ValueError("Unknown embed_type {}".format(embed_type))

            return tf.expand_dims(tf.nn.embedding_lookup(embedding, input_data), -1)

    def build_conv_layers(self, embedding_input):
        with tf.variable_scope("convolutions", dtype=self.dtype) as scope:
            pooled_outputs = self._build_conv_maxpool(embedding_input)

            num_total_filters = self.params['num_filters'] * len(self.params['filter_sizes'])
            concat_pooled = tf.concat(pooled_outputs, 3)
            flat_pooled = tf.reshape(concat_pooled, [-1, num_total_filters])

            if self.mode == tf.estimator.ModeKeys.TRAIN:
                h_dropout = tf.layers.dropout(flat_pooled, self.params['dropout'])
            else:
                h_dropout = tf.layers.dropout(flat_pooled, 0)
            return h_dropout

    def _build_conv_maxpool(self, embedding_input):
        pooled_outputs = []
        for filter_size in self.params['filter_sizes']:
            with tf.variable_scope(f"conv-maxpool-{filter_size}-filter"):
                conv = tf.layers.conv2d(
                        embedding_input,
                        self.params['num_filters'],
                        (filter_size, self.params['embedding_dim']),
                        activation=tf.nn.relu)

                pool = tf.layers.max_pooling2d(
                        conv,
                        (self.params['max_seq_length'] - filter_size + 1, 1),
                        (1, 1))

                pooled_outputs.append(pool)
        return pooled_outputs

    def build_fully_connected_layers(self, conv_output):
        with tf.variable_scope("fully-connected", dtype=self.dtype) as scope:
            return tf.layers.dense(
                    conv_output,
                    self.params['num_classes'],
                    kernel_initializer=tf.contrib.layers.xavier_initializer())

    def _get_prediction(self, output):
        tf.argmax(output[0], name='train/pred_0') # for print_verbose
        predictions = tf.argmax(output, axis=1)

        return predictions

    def _build_loss(self, output, targets):
        loss = tf.losses.sparse_softmax_cross_entropy(
                targets,
                output,
                scope="loss")

        return loss

    def _build_optimizer(self, loss):
        train_op = layers.optimize_loss(
            loss, tf.train.get_global_step(),
            optimizer='Adam',
            learning_rate=self.params['learning_rate'],
            summaries=['loss', 'learning_rate'],
            name="train_op")

        return train_op

    def get_mapping_tensor(self):
        data = self.params['tags_data']
        mapping_strings = tf.constant(data)

        return mapping_strings

    def get_label_str(self, predicted_label_id, mapping_strings):
        vocab_tags = tf.contrib.lookup.index_to_string_table_from_tensor(mapping_strings)

        print(self.labels)
        label_str = vocab_tags.lookup(predicted_label_id)

        return label_str

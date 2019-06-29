import os
import time

import paddle
import paddle.fluid as fluid


def train_model(train_inpf, eval_inpf, config):
    main_program = fluid.Program()
    startup_program = fluid.Program()
    with fluid.program_guard(main_program=main_program, startup_program=startup_program):
        place = fluid.CPUPlace()

        train_reader = paddle.batch(
            paddle.reader.shuffle(train_inpf, buf_size=500),
            batch_size=config['batch_size'])

        hid_dim = 512

        words = fluid.layers.data(name='words', shape=[1], dtype='int64',
                                  lod_level=1)
        tags = fluid.layers.data(name='tags', shape=[1], dtype='int64')

        emb = fluid.layers.embedding(
            input=words, size=[config['embedding_vocabulary_size'], config['embedding_dim']])

        conv_3 = fluid.nets.sequence_conv_pool(
            input=emb,
            num_filters=hid_dim,
            filter_size=3,
            act="tanh",
            pool_type="sqrt")

        conv_4 = fluid.nets.sequence_conv_pool(
            input=emb,
            num_filters=hid_dim,
            filter_size=4,
            act="tanh",
            pool_type="sqrt")

        prediction = fluid.layers.fc(input=[conv_3, conv_4], size=len(config['tags_data']), act="softmax")

        cost = fluid.layers.cross_entropy(input=prediction, label=tags)
        avg_cost = fluid.layers.mean(cost)

        sgd_optimizer = fluid.optimizer.AdamOptimizer()

        sgd_optimizer.minimize(avg_cost)

        feeder = fluid.DataFeeder(place=place, feed_list=[words, tags])

        exe = fluid.Executor(place)

        exe.run(startup_program)

        save_dirname = os.path.join(config['saved_model_dir'], str(int(time.time())))

        for pass_id in range(config['epochs']):
            print(">>> pass_id: {}".format(pass_id))
            for data in train_reader():
                # print(data)
                feed = feeder.feed(data)

                avg_loss_value, = exe.run(
                    main_program, feed=feed, fetch_list=[avg_cost],
                    return_numpy=True)
                print(avg_loss_value[0])

        if save_dirname is not None:
            fluid.io.save_inference_model(save_dirname, ['words'], [prediction], exe)

            # save asset
            def write_asset(output_file, data):
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                with open(output_file, 'wt') as fd:
                    fd.write('\n'.join(data))

            write_asset(os.path.join(save_dirname, 'data/vocabulary.txt'), config['vocab_data'])
            write_asset(os.path.join(save_dirname, 'data/tags.txt'), config['tags_data'])

        return None, None, save_dirname
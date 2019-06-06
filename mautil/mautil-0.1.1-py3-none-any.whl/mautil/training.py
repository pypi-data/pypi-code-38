import numpy as np, logging, time, traceback, gc
from . import util
from .util import timer


class Trainer(object):
    def __init__(self, name, seed):
        self.name = name
        self.seed = seed

    def train_model(self, data, args, gl, process_data=True, copies=1, sleep_seconds=1):
        """

        :param data: dictionary of train, validate, test data.
        :param args: ArgParser args
        :param gl: dictionary of model classes
        :param process_data: True if the data has not been processed by model
        :param copies: num of copies to train for each model
        #param sleep_seconds: wait seconds after each copy trained(sometimes gpu resource was not released quickly)
        :return:
        """
        rs = np.random.RandomState(self.seed)
        preds_test = []
        preds_validate = []
        names = util.parse_model_name(args.model_names)
        if args.no_validate:
            _ = data.pop('validate', None)
        if args.no_test:
            _ = data.pop('test', None)

        d_train = data.get('train')
        d_validate = data.get('validate', None)
        d_test = data.get('test', None)

        for i, name in enumerate(names):
            logging.info('will train for model: %s', name)
            processed = False
            for j in range(copies):
                if copies == 1:
                    seed = None
                else:
                    seed = rs.randint(np.power(2, 32))
                model = util.create_model(name, args, gl[name], seed)
                if process_data and not processed:
                    with timer('process data'):
                        x_train, y_train, x_validate, y_validate, x_test, y_test =  \
                            model.process_data(data)
                    processed = True
                else:
                    x_train, y_train = d_train
                    if d_validate is not None:
                        x_validate, y_validate = d_validate
                    else:
                        x_validate = None
                        y_validate = None
                    if d_test is not None:
                        x_test, y_test = d_test
                    else:
                        x_test = None
                if args.no_train:
                    model.create_model()
                    model.restore()
                    break
                try:
                    model.fit(x_train, y_train, x_validate, y_validate, args.save_model, xTest=x_test, restore=args.restore, save_epoch=args.save_epoch, no_validate=args.no_validate, only_validate=args.only_validate)
                    break
                except Exception as e:
                    traceback.print_exc()
                    logging.error('********error when fit %sth  model %s:%s********', i, name, e)
                    model.destroy()
                    del model
                    gc.collect()
                finally:
                    time.sleep(sleep_seconds)
                    logging.info('sleeped 1 second for %sth model  %s', i, name)
            logging.info('train done for modle:%s,start predict', name)
            if args.predicting:
                suffix = ('_' + str(args.global_step)) if args.global_step is not None else ''
                if x_validate is not None:
                    pred_validate = model.predict(x_validate)
                    model.save_predict(pred_validate, suffix)
                    preds_validate.append(pred_validate)
                if x_test is not None:
                    pred_test = model.predict(x_test)
                    preds_test.append(pred_test)
                    if args.save_model:
                        model.save_predict(pred_test, suffix+'_test')

            model.destroy()
            del model
            gc.collect()
        if args.predicting and not args.no_validate:
            if copies>1:
                pred = np.mean(preds_validate, 0)
            else:
                pred = preds_validate[0]
            return pred

import os
import json
import zipfile

from keras.models import save_model

from easymodels import Model


DEFAULT_OPTIMIZER = 'adam'
DEFAULT_LOSS = 'categorical_crossentropy'


class KerasModel(Model):

    def __init__(self, **kwargs):
        self.optimizer = None
        self.loss = None

        super().__init__(**kwargs)

        if not self.optimizer:
            print('WARNING: optimizer not set, using default %s' % DEFAULT_OPTIMIZER)
            self.optimizer = DEFAULT_OPTIMIZER

        if not self.loss:
            print('WARNING: loss not set, using default %s' % DEFAULT_LOSS)
            self.loss = DEFAULT_LOSS

    def compile(self, model):
        print('Compiling model')
        model.compile(
            loss=self.loss,
            optimizer=self.optimizer,
            metrics=['accuracy']
        )

        return model

    def save(self, model_name, model, export_path, epoch):
        model_h5 = '%s.h5' % model_name
        model_yaml = '%s.yaml' % model_name
        zip_name = '%s-%03d.zip' % (model_name, epoch)

        print('Saving model in %s' % zip_name)

        model_file = os.path.join(export_path, model_h5)
        save_model(model, model_file)

        yaml_file = os.path.join(export_path, model_yaml)
        with open(yaml_file, 'w') as f:
            f.write(model.to_yaml())

        zip_path = os.path.join(export_path, zip_name)
        zipf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
        zipf.write(yaml_file)
        zipf.write(model_file)
        zipf.close()

        print('Model saved')

    def save_fitness(self, fitness, export_path):
        print('Saving fitness')
        fitness_file = os.path.join(export_path, 'fitness.json')
        with open(fitness_file, 'w') as f:
            json.dump(fitness, f)

        print('Fitness saved')


class MemoryModel(KerasModel):
    def train(self, model, round_step, x_train, y_train):
        model.fit(
            x_train,
            y_train,
            batch_size=self.batch_size,
            epochs=round_step,
            verbose=1,
        )

        return model


class GeneratorModel(KerasModel):
    def train(self, model, round_step, train):
        model.fit_generator(
            train,
            epochs=round_step,
            steps_per_epoch=train.n/self.batch_size,
            verbose=1,
        )

        return model

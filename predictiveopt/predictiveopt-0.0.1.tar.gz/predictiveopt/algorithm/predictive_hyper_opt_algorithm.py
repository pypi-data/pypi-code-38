import pandas as pd

from predictiveopt.models import KMeansModel
from predictiveopt.models.linear_regression import LinearRegressionModel


class PredictiveHyperOpt:

    def __init__(self, total_models_count, full_models_count, final_epoch, partial_epochs, batch_size=128, final_models_count=1):
        self.total_models_count = total_models_count
        self.full_models_count = full_models_count
        self.final_epoch = final_epoch
        self.partial_epochs = partial_epochs
        self.batch_size = batch_size
        self.final_models_count = final_models_count

    def simulate(self, data, total_runs=1000):

        best_accuracies = []

        x = data.iloc[:, 0]
        y = data.iloc[:, 1]

        for i in range(0, total_runs):
            train_index = self.cluster_selection(x.values.reshape(-1, 1))

            mask = x.index.isin(train_index)
            x_train = x[mask]
            y_train = y[mask]

            x_test = x[~mask]
            y_test = y[~mask]

            linear_model = LinearRegressionModel(x_train.values.reshape(-1, 1), y_train, x_test.values.reshape(-1, 1))
            predictions = linear_model.run()

            predictions.index = y_test.index

            predicted_sorted = predictions.sort_values(ascending=False).reset_index()
            predicted_sorted.columns = ['index', 'predicted_acc']

            top = y_test[predicted_sorted[0:self.final_models_count]['index']].max()
            training_max = y_train.max()

            best_accuracies.append(max(top, training_max))

            print(f'Simulation {i}')

        return round(pd.Series(best_accuracies).mean() * 100, ndigits=2)

    def run(self, generator, x_train, y_train, x_test, y_test):
        x_internal = list()
        y_internal_train = list()

        models_pool = list()

        for i in range(0, self.total_models_count):
            model = generator.create_mutated_model()

            stats = model.fit(x_train, y_train, self.partial_epochs[0], self.batch_size)
            x_internal.append(stats.history['loss'][self.partial_epochs[0] - 1] - stats.history['loss'][self.partial_epochs[1] - 1])

            models_pool.append(model)

        x_internal = pd.Series(x_internal)
        train_index = self.cluster_selection(x_internal.values.reshape(-1, 1))
        mask = x_internal.index.isin(train_index)

        x_internal_train = x_internal[mask]
        x_internal_test = x_internal[~mask]

        full_model_indexes = x_internal_train.index.values

        for i in full_model_indexes:
            model = models_pool[i]
            model.fit(x_train, y_train, self.final_epoch - self.partial_epochs[0], self.batch_size)
            validation_stats = model.evaluate(x_test, y_test)
            y_internal_train.append(validation_stats[1])

        y_internal_train = pd.Series(y_internal_train)
        y_internal_train.index = x_internal_train.index

        linear_model = LinearRegressionModel(x_internal_train.values.reshape(-1, 1), y_internal_train, x_internal_test.values.reshape(-1, 1))
        predictions = linear_model.run()

        predictions.index = x_internal_test.index
        predictions_sorted = predictions.sort_values(ascending=False).reset_index()

        final_accuracies = list()

        for i in range(0, self.final_models_count):
            evaluation_index = int(predictions_sorted.iloc[i, :]['index'])
            model = models_pool[evaluation_index]
            model.fit(x_train, y_train, self.final_epoch - self.partial_epochs[0], self.batch_size)
            validation_stats = model.evaluate(x_test, y_test)
            final_accuracies.append(validation_stats[1])

        final_accuracies = pd.Series(final_accuracies)
        final_accuracies.index = predictions_sorted['index'].values[0:self.final_models_count]

        fully_evaluated_models = final_accuracies.append(y_internal_train)
        fully_evaluated_models.idxmax()

        return round(fully_evaluated_models.max() * 100, ndigits=2), str(generator.mutation_history[fully_evaluated_models.idxmax()])

    def cluster_selection(self, x, samples_per_cluster=1):

        clustering = KMeansModel(x, self.full_models_count)
        clustering.run()

        train_index = clustering.sample_clusters(samples_per_cluster)

        return train_index

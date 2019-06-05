class Model:

    def __init__(self, model, type):
        self.model = model
        self.type = type

    def fit(self, x_train, y_train, epochs, batch_size):
        if self.type == 'keras':
            return self.model.fit(x_train, y_train, epochs=epochs, batch_size=batch_size)

    def predict(self, x_test):
        if self.type == 'keras':
            return self.model.predict(x_test)

    def evaluate(self, x_test, y_test):
        if self.type == 'keras':
            return self.model.evaluate(x_test, y_test)

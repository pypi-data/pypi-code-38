import pandas
import seaborn as sns
import matplotlib.pyplot as plt
import json
from forecastlib.genetics.pyga import GenerationRecord

class CorrelationCalculation:
    def __init__(self, genes: list, generations: list = None, source_file: str = None):
        self.generations = generations
        self.genes = genes
        self.source_file = source_file

    def get_generations(self):
        if self.source_file == None:
            return self.generations
        
        file = open(self.source_file, "r")
        text_data = file.read()
        data = json.loads(text_data)

        generations = []
        for ds in data:
            a = GenerationRecord(None, self.genes, None, None, None, dic=ds)
            #generation = json.loads(ds, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
            generations.append(a)

        return generations

    def render_corr(self, dest_image_file: str = None, dest_csv_file: str = None, show: bool = False):
        columns = self.genes + ['fitness']
        data = pandas.DataFrame(columns=(columns), dtype=int)
        generations = self.get_generations()
        
        index = 0        
        for generation in generations:
            row = list(generation.genom)
            row.append(generation.fitness)
            data.loc[index] = row
            index = index + 1

        corrmat = data.corr()

        top_corr_features = corrmat.index
        correlations = data[top_corr_features].corr()

        plt.figure(figsize=(len(columns),len(columns)))
        g=sns.heatmap(correlations,annot=True,cmap="RdYlGn")

        if(dest_image_file != None):
            plt.savefig(dest_image_file)

        if(dest_csv_file != None):
            f = open(dest_csv_file, "w")
            csv = correlations.to_csv()
            f.write(csv)
            f.close()

        if(show):
            plt.show()
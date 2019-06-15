import aspecd.tasks
import aspecd.io
import trepr.dataset
import trepr.plotting

dataset_factory_ = trepr.dataset.DatasetFactory()
recipe = aspecd.tasks.Recipe()
recipe.dataset_factory = dataset_factory_
recipe_importer = aspecd.io.RecipeYamlImporter('/home/jara/Dokumente/masterthesis/Rezepte/Simualtion1.yaml')
recipe_importer.import_into(recipe)
chef = aspecd.tasks.Chef(recipe)
chef.cook()

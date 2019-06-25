from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
   name='slipo-loci',
   version='0.1.2',
   description='A high-level library for analyzing Points and Areas of Interest',
   long_description=long_description,
   long_description_content_type="text/markdown",
   author='Panagiotis Kalampokis, Dimitris Skoutas',
   author_email='pkalampokis@imis.athena-innovation.gr, dskoutas@imis.athena-innovation.gr',
   url="https://github.com/SLIPO-EU/loci",
   packages=['loci'],
   install_requires=['geopandas', 'shapely', 'pandas', 'numpy', 'matplotlib', 'folium', 'scikit-learn', 'hdbscan',
                     'scipy', 'networkx', 'wordcloud', 'pysal', 'pyLDAvis', 'mlxtend']
)

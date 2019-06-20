import setuptools

from sri.common import config
from sri.common import entrypoints

setuptools.setup(
    name = config.PACKAGE_NAME,

    version = config.VERSION,

    description = 'Graph and PSL based TA1 primitive for D3M',
    long_description = 'Graph and PSL based TA1 primitive for D3M',
    keywords = 'd3m_primitive',

    maintainer_email = config.EMAIL,
    maintainer = config.MAINTAINER,

    # The project's main homepage.
    url = config.REPOSITORY,

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        'Programming Language :: Python :: 3.6',
    ],

    # packages = setuptools.find_packages(exclude = ['contrib', 'docs', 'tests']),
    packages = [
        'sri',
        'sri.autoflow',
        'sri.baseline',
        'sri.common',
        'sri.graph',
        'sri.pipelines',
        'sri.psl',
        'sri.psl.cli',
        'sri.tpot',
    ],

    include_package_data = True,
    package_data = {
        'sri.psl.cli': [
            'psl-cli-CANARY-2.1.5.jar',
            'link_prediction_template.data',
            'link_prediction_template.psl'
            'general_relational_template.data',
            'general_relational_template.psl',
            'relational_timeseries_template.data',
            'relational_timeseries_template.psl',
        ]
    },

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires = [
        # Base
        'd3m', 'psutil',
        # TPOT
        'pathos', 'sri_tpot',

        # Already provided by d3m (let d3m manage the exact versions):
        # 'networkx', 'numpy', 'pandas', 'scikit-learn',
    ],

    python_requires = '>=3.6',

    entry_points = entrypoints.get_entrypoints_definition()
)

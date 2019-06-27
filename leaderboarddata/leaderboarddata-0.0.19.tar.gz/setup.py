import setuptools

VERSION = "0.0.19"

setuptools.setup(
    name="leaderboarddata",
    packages=setuptools.find_packages(),
    version=VERSION,
    description="Back end service for SC2 ladder ranking leaderboard",
    author="Hugo Wainwright",
    author_email="wainwrighthugo@gmail.com",
    url="https://github.com/frugs/allin-data",
    keywords=["sc2", "MMR"],
    classifiers=[],
    install_requires=[
        "requests-toolbelt>=0.8.0",
        "sc2gamedata",
        "retryfallback",
        "flask",
        "google-cloud-datastore",
        "firebase-admin",
    ],
)

from setuptools import find_packages, setup

setup(
    name="fin-announcer",
    version="1.0",
    description="Discord bot to announce finishes/PBs for Kacky alike hunting/events in TM20 or TMNF.",
    author="djinn",
    packages=find_packages(),
    install_requires=[
        "discord-py" == "2.3.2",
        "namedtupled" == "0.3.3",
    ],
)

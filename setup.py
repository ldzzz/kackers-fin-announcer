from setuptools import find_packages, setup

setup(
    name="fin-announcer",
    version="0.1",
    description="Discord bot to announce finishes/PBs for Kacky alike hunting/events in TM20 or TMNF.",
    author="djinn",
    packages=find_packages(),
    install_requires=[
        "discord-py" == "2.1.0",
        "mariadb" == "1.1.5.post3",
        "namedtupled" == "0.3.3",
    ],
)

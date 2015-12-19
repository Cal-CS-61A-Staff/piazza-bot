from setuptools import setup

import piazza_moderator

setup(
    name='piazza-moderator',
    version=piazza_moderator.__version__,
    description='An automatic moderator for the Piazza Q&A forum.',
    url='https://github.com/brianhou/automatic-broccoli',
    author='Brian Hou',
    packages=['piazza_moderator'],
    install_requires=['piazza-api'],
)

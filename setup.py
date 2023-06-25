#!/usr/bin/env python
# write a setup.py file

from distutils.core import setup, find_packages

setup(
    name='transcribe and summarize',
    version='0.1',
    description='Uses OpenAI Whisper and GPT to transcribe and summarize audio files',
    author='Ryan Saul',
    author_email='giantryansaul@gmail.com',
    packages=find_packages(exclude=('tests', 'docs'))
)
from setuptools import setup

setup(
    name='snapshotalyzer-30000',
    version='0.1',
    author='Shubham Bhatia',
    description='shbhatia@syr.edu',
    liscence='GPLv3+',
    packages=['shotty'],
    url='https://github.com/shubhamb0002/snapshotanalyzer-30000',
    install_requires=[
        'click',
        'boto3',
        'datetime'
        ],
    entry_points='''
        [console_scripts]
        shotty=shotty.shotty:cli
        ''',


)

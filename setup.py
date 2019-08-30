from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='schedule-convert',
    version='1.0',
    author='Ilya Zverev',
    author_email='ilya@zverev.info',
    packages=['schedule_convert'],
    install_requires=[
        'vobject',
        'qrcode[pil]',
    ],
    url='https://github.com/Zverik/schedule-convert',
    license='MIT License',
    description='Converts and merges conference schedules, frab-compatible',
    long_description=open(path.join(here, 'README.rst')).read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Information Technology',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
    ],
    entry_points={
        'console_scripts': ['schedule_convert = schedule_convert.run:main']
    },
)

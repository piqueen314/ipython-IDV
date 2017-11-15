import setuptools

setuptools.setup(
    name="ipython-IDV",
    version="0.1.0",
    url="https://github.com/piqueen314/ipython-IDV.git",

    author="Cece Hedrick",
    author_email="cecehedrick@gmail.com",

    description="This project allows users to use Unidata's IDV with jupyter notebooks ",
    long_description=open('README.md').read(),

    packages=setuptools.find_packages(),

    install_requires=[],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)

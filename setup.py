from setuptools import setup

setup(
    name="pylint_pycharm",
    packages=["pylint_pycharm"],
    version="1.0.0",
    description="Pylint to Pycharm message converter",
    author="Wadim Ovcharenko",
    author_email="wadim@veles-soft.com",
    url="https://github.com/perses76/pylint-pycharm",
    keywords=["pylint", "pycharm"],
    install_requires=["pylint"],
    tests_require=["mock"],
    entry_points={
        'console_scripts': ['pylint-pycharm=pylint_pycharm.__main__:main']
    },
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Development Status :: Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT",
        "Operating System :: OS Independent",
    ],
    long_description=\
        """
        Pylint to Pycharm message converter.
        -------------------------------------
        
        Convert messages from Pylint report to Pycharm format.
        """,
    test_suite='tests',
    use_2to3=True,
    zip_safe=True
)

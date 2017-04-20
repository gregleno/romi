from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='rominet',
      version='0.1',
      description='A package to interact with a romi based robot',
      long_description=readme(),
      url='https://github.com/gregleno/romi',
      author='Gregory Lenoble',
      license='GPLv3',
      packages=['rominet'],
      install_requires=[
      ],
      test_suite='nose.collector',
      tests_require=['nose', 'nose-cover3'],
      zip_safe=False)

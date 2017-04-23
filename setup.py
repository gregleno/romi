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
      entry_points={
        'console_scripts': ['rominet-service=rominet.service:main']
      },
      install_requires=[
       'pytest-runner'
      ],
      test_suite='pytest',
      tests_require=['pytest'],
      zip_safe=False)

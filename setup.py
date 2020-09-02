from setuptools import setup, find_packages

__version__ = '0.1.0'


setup(name='ebrains-drive',
      version=__version__,
      license='Apache-2.0 License',
      description='Python client interface for HBP Collaboratory Seafile storage',
      author='Ebrains, CNRS',
      author_email='support@ebrains.eu',
      url='http://seafile.com',
      platforms=['Any'],
      packages=find_packages(),
      install_requires=['requests'],
      classifiers=['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'],
      )

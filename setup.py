from setuptools import setup, find_packages
from version_query import predict_version_str

__version__ = predict_version_str()


setup(name='ebrains-drive',
      version=__version__,
      license='Apache-2.0 License',
      description='Python client interface for EBRAINS Collaboratory Seafile storage',
      author='EBRAINS, CNRS',
      author_email='support@ebrains.eu',
      url='https://github.com/HumanBrainProject/ebrains-drive/',
      platforms=['Any'],
      packages=find_packages(),
      install_requires=['requests'],
      classifiers=['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python'],
      )

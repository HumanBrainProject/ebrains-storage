from setuptools import setup, find_packages
from version_query import predict_version_str

__version__ = predict_version_str()


setup(name='ebrains-drive',
      version=__version__,
      license='Apache-2.0 License',
      description='Python client interface for EBrains Collaboratory Seafile storage',
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

from setuptools import setup

setup(name='monicars',
      version='0.1',
      description='A simple car simulator',
      url='https://github.com/monicaMRL/MonicarS',
      author='Jana Pavlasek, Monica Patel',
      author_email='jana@cim.mcgill.ca',
      packages=['monicars'],
      package_dir={'monicars': 'monicars'},
      package_data={'monicars': ['media/*', 'maps/*', 'config/config.yaml', 'scripts/*']},
      install_requires=[
          'pygame',
          'numpy',
          'scipy',
          'pyyaml'
      ],
      zip_safe=False)

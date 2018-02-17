from setuptools import setup

setup(name='pritunlsdk',
      version='0.1',
      description='Unofficial Pritunl SDK written in Python that allows to easily intract with Pritunl API',
      url='http://github.com/chaordic/pritunl-python-sdk',
      author='Raphael P. Ribeiro',
      author_email='raphael.ribeiro@chaordicsystems.com',
      license='GPL',
      packages=['pritunlsdk'],
      install_requires=[
          'requests',
      ],
      zip_safe=False)

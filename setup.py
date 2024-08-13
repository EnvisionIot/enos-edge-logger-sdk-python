import setuptools
from setuptools.command.install import install
import os

class EdgeLoggerInstallCommand(install):
    def run(self):
        os.system('./deps/install.sh')
        install.run(self)

with open('README.md', 'r') as desc:
    long_description = desc.read()

setuptools.setup(
    name='edge-logger-sdk-python',
    version='1.0.1',
    author='Austen',
    author_email='',
    description='Edge Logger API for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',
    packages=setuptools.find_packages(),
    python_requires='>=3',
    include_package_data=True,
    # packages = ['edgelogger'],
    # data_files={'deps': ['*']},
    cmdclass= {
        'install': EdgeLoggerInstallCommand
    },
    install_requires=[
        'redis',
        'protobuf==3.2.0',
        'wheel',
        # 'pyzmq' # becase on HPU/DTU it cannot install via pip, using install.sh install manually
    ],
    classifiers=[
        # 3 - Alpha, 4 - Beta, 5- Production/Stable
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ]
)


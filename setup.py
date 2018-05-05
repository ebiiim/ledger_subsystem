import subprocess
import sys, os, shutil, site
from os import path
from setuptools import setup
from setuptools.command.install import install


here = path.abspath(path.dirname(__file__))

with open('README.rst') as f:
    readme = f.read()


class MyInstall(install):
    def _pre_install(self):
        sitedir = site.getsitepackages()[0]
        install_pkg_dir = os.path.join(sitedir, 'bbc1')
        target_dir = os.path.join(install_pkg_dir, 'core')
        ethereum_target_dir = os.path.join(target_dir, 'ethereum')
        if os.path.exists(ethereum_target_dir):
            shutil.rmtree(ethereum_target_dir)
        shutil.copytree('bbc1/core/ethereum', ethereum_target_dir)

    def run(self):
        try:
            self._pre_install()
            install.run(self)
        except Exception as e:
            print(e)
            exit(1)


bbc1_requires = [
                    'populus==2.1.0',
                    'rlp==0.6.0',
                    'eth-utils==0.7.4',
                    'web3==3.16.5',
                ]

bbc1_packages = ['bbc1', 'bbc1.core', 'bbc1.core.ethereum']

bbc1_commands = [
                    'utils/eth_subsystem_tool.py',
                ]

bbc1_classifiers = [
                    'Development Status :: 4 - Beta',
                    'Programming Language :: Python :: 3.5',
                    'Programming Language :: Python :: 3.6',
                    'Topic :: Software Development']

setup(
    name='ledger_subsystem',
    version='0.11.0',
    description='A ledger subsystem of Beyond Blockchain One',
    long_description=readme,
    url='https://github.com/beyond-blockchain/ledger_subsystem',
    author='beyond-blockchain.org',
    author_email='bbc1-dev@beyond-blockchain.org',
    license='Apache License 2.0',
    classifiers=bbc1_classifiers,
    cmdclass={'install': MyInstall},
    packages=bbc1_packages,
    scripts=bbc1_commands,
    install_requires=bbc1_requires,
    zip_safe=False)


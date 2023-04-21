from setuptools import setup, find_packages

setup(
    name='arb_launcher',
    author='arb',
    author_email='arb.trops@gmail.com',
    description='A package to launch and manage detached programs',
    url="https://github.com/Acid3croco/arb-trops-services",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    version='1.1.0',
    packages=find_packages(),
    install_requires=['setproctitle', 'arb_logger', 'psutil'],
    entry_points={
        'console_scripts': [
            'arb_launcher = arb_launcher.cli:main',
        ],
    },
)

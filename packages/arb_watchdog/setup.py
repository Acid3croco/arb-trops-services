from setuptools import setup, find_packages

setup(
    name='arb_watchdog',
    version='1.0.1',
    author='arb',
    author_email='arb.trops@gmail.com',
    description=
    'A process monitoring and alerting tool that keeps an up-to-date status of processes in Redis',
    packages=find_packages(),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Acid3croco/arb-trops-services',
    install_requires=[
        'watchdog', 'redis', 'tabulate', 'colorama', 'psutil', 'arb_logger'
    ],
    entry_points={
        'console_scripts': [
            'arb_watchdog = arb_watchdog.process_watcher:main',
            'arb_watchdog_cli = arb_watchdog.cli:main',
        ]
    },
)

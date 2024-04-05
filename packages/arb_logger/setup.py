from setuptools import setup, find_packages

setup(
    name='arb_logger',
    author='arb',
    author_email='arb.trops@gmail.com',
    description="A custom logger with Redis integration",
    url="https://github.com/Acid3croco/arb-trops-services",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    version='2.2.1',
    packages=find_packages(),
    install_requires=['coloredlogs', 'redis', 'pync'],
    entry_points={
        'console_scripts': [
            'arb_alerts = arb_logger.arb_alerts:main',
        ]
    },
)

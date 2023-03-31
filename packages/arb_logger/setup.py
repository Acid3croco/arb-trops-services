from setuptools import setup, find_packages

setup(
    name='arb_logger',
    author='arb',
    author_email='arb.trops@gmail.com',
    description="A custom logger with Redis integration",
    url="https://github.com/Acid3croco/arb-trops-services",
    version='1.1.1',
    packages=find_packages(),
    install_requires=['coloredlogs', 'redis', 'pync'],
    entry_points={
        'console_scripts': [
            'arb_alerts = arb_logger.redis_log_client:main',
        ]
    },
)

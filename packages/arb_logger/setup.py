from setuptools import setup, find_packages

setup(
    name='arb_logger',
    author='arb',
    author_email='arb.trops@gmail.com',
    description='arb_logger de ouf',
    version='1.0.0',
    packages=find_packages(),
    install_requires=['coloredlogs', 'redis'],
    entry_points={
        'console_scripts': [
            'arb_alerts = arb_logger.redis_log_client:main',
        ]
    },
)

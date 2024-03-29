from setuptools import setup, find_packages

setup(
    name='arb_sysload',
    author='arb',
    version='0.2.1',
    author_email='arb.trops@gmail.com',
    description="A package to monitor system load and send alerts to a redis server",
    url="https://github.com/Acid3croco/arb-trops-services",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=['arb_logger', 'flask', ' Flask-CORS', 'docker'],
    entry_points={
        'console_scripts': [
            'arb_sysload = arb_sysload.arb_sysload:main',
            'sysload_api = arb_sysload.sysload_api:main',
        ]
    },
)

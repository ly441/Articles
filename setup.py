from setuptools import setup, find_packages

setup(
    name="articles_project",
    version="0.1",
    packages=find_packages(include=['lib*']),
    install_requires=[
        'psycopg2-binary>=2.9.3',
        'pytest>=7.0.0',
    ],
    python_requires='>=3.8',
    package_dir={'': '.'},  # Tell setuptools that packages are in root
)
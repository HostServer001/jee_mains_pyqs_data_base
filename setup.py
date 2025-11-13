from setuptools import setup, find_packages

setup(
    name="jee_data_base",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sentence_transformers",
        "hdbscan",
        "pickle",
        "numpy",
        "requests",
        "tqdm"
        ],  # Example dependency
    description="JEE Mains PYQS data base",
    author="HostServer001",
    author_email="jarvisuserbot@gmail.com",
    url="https://github.com/HostServer001/jee_mains_pyqs_data_base",
    include_package_data=True
)

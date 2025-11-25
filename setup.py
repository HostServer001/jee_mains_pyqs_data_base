import sys
from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        # subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright>=1.56.0"])
        subprocess.check_call(["playwright","install","chromium"])

setup(
    name="jee_data_base",
    version="0.2.1.post2",
    packages=find_packages(),
    install_requires = [
    "playwright>=1.56.0",
    "hdbscan>=0.8.40",
    "numpy>=2.3.3",
    "requests>=2.32.5",
    "tqdm>=4.67.1",
    "PyPDF2>=3.0.1",
    "beautifulsoup4>=4.14.2"
    ],
    description="JEE Mains PYQS data base",
    author="HostServer001",
    author_email="jarvisuserbot@gmail.com",
    url="https://github.com/HostServer001/jee_mains_pyqs_data_base",
    include_package_data=True,
    cmdclass={
        "install":PostInstallCommand,
    }
)

import json
from pathlib import Path
from glob import glob
import setuptools

HERE = Path(__file__).parent.resolve()


name = "jupyterlab_vre"
labext_name = "jupyterlab_vre"
long_description = (HERE / "README.md").read_text()
pkg_json = json.loads((HERE / "package.json").read_bytes())
frontend_packages_path = "./dist/*.tgz"
jupyter_config_path = './jupyter-config/*.json'

setup_args = dict(
    name=name,
    version="0.1.0",
    url="https://github.com/QCDIS/NaaVRE",
    author="Riccardo Bianchi",
    author_email="riccardo.bianchi@lifewatch.eu",
    description="Jupyter Lab extension for virtual research environments",
    license="BSD-3-Clause",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    data_files=[('etc/jupyter/jupyter_server_config.d', glob(jupyter_config_path)),
                ('share/jupyter/lab/extensions', glob(frontend_packages_path))],
    install_requires=[
        "jupyterlab>=3.5.0",
        "autopep8",
        "pyflakes>=2.4.0",
        "nbformat>=5.7.0",
        "Jinja2",
        "colorhash>=1.0.4",
        "tinydb>=4.6.1",
        "PyYAML>=6.0",
        "PyGithub>=1.55",
        "setuptools_rust>=1.5.2",
        "requests",
        "tornado>=6.1",
        "notebook",
        "setuptools>=63.1.0",
        "distro"
    ],
    zip_safe=False,
    include_package_data=True,
    python_requires=">=3.8",
    platforms="Linux, Mac OS X, Windows",
    keywords=["Jupyter", "JupyterLab", "JupyterLab3"],
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Framework :: Jupyter",
    ],
)

if __name__ == "__main__":
    setuptools.setup(**setup_args)

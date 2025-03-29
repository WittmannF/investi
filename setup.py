from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="investi",
    version="0.1.0",
    author="Fernando Wittmann",
    author_email="fernando.wittmann@gmail.com",
    description="Biblioteca para simulação de investimentos em renda fixa",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/WittmannF/investi",
    packages=find_packages(include=["investi", "investi.*", "exemplos", "exemplos.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.0.0",
        "matplotlib>=3.0.0",
        "numpy>=1.18.0",
        "pytest>=6.0.0",
        "python-dateutil>=2.8.0",
    ],
    entry_points={
        "console_scripts": [
            "investi-cenarios=exemplos.simulacao_cenarios:main",
            "investi-aportes=exemplos.simulacao_aportes:main",
            "investi-tesouro=exemplos.simulacao_tesouro:main",
        ],
    },
) 
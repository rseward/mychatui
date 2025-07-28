from setuptools import setup, find_packages

setup(
    name="mychatui",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "customtkinter",
        "google-generativeai",
        "tkhtmlview",
        "markdown",
    ],
    entry_points={
        "gui_scripts": [
            "mychatui = mychatui.app:main",
        ],
    },
)

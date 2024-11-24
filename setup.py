from setuptools import setup, find_packages

setup(
    name="imgoptimize",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Pillow>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "imgoptimize=image_optimizer.optimize_images:main",
        ],
    },
    author="Tautvydas",
    description="Image optimization tool for web",
    python_requires=">=3.6",
)

import setuptools

setuptools.setup(
    name="response_tools_py",
    version="0.0.1",
    description="Software used for the FOXSI response files.",
    url="https://github.com/foxsi/response-tools",
    install_requires=[
            "setuptools",
            "numpy", 
            "scipy",
            "matplotlib",
            "pyyaml",
            "astropy",
            "pytest",
            "pandas",
        ],
    packages=setuptools.find_packages(),
    zip_safe=False,
)
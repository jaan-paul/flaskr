from setuptools import find_packages, setup

setup(
    name="flaskr",
    version="0.0.1",
    packages=find_packages(),
    # Include other non-Python files like templates and static files. See
    # MANIFEST.in to see what these other files are.
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask"],
)

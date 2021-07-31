"""Setup oaff-app"""

from setuptools import find_namespace_packages, setup  # type: ignore

with open("README.md") as f:
    long_description = f.read()

inst_reqs = [
    "pydantic==1.8.2",
    "pygeofilter",
]
extra_reqs = {
    "test": ["pytest"],
}

setup(
    name="oaff.app",
    version="0.0.1",
    description=u"Business logic for oaff",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_namespace_packages(exclude=["tests*"]),
    include_package_data=False,
    zip_safe=True,
    install_requires=inst_reqs,
    extras_require=extra_reqs,
)

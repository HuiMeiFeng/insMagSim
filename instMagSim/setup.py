# Copyright (c) 2026 Hui-Mei Feng
# Distributed under MIT License, see LICENSE file.

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    requirements = [
        req.strip()
        for req in f.readlines()
        if not req.startswith("#") and req.__contains__("==")
    ]

setuptools.setup(
    name='insMagSim',
    version='0.0.1',
    author='Hui-Mei Feng',
    author_email='fenghuimei21@mails.ucas.ac.cn',
    description='Instrument magnitude simulation tool',  # short description
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/HuiMeiFeng/insMagSim',
    project_urls={
        'Source': 'https://github.com/HuiMeiFeng/insMagSim',
    },
    packages=setuptools.find_packages(),
    license='MIT',
    classifiers=["Development Status :: 5 - Production/Stable",
                 "Intended Audience :: Science/Research",
                 "License :: OSI Approved :: MIT License",
                 "Operating System :: OS Independent",
                 "Programming Language :: Python :: 3.9",
                 "Topic :: Scientific/Engineering :: Physics",
                 "Topic :: Scientific/Engineering :: Astronomy"],
    # package_dir={'insMagSim': 'insMagSim'},
    # include_package_data=True,
    include_package_data=False,
    python_requires='>=3.9',
    install_requires=requirements,
)



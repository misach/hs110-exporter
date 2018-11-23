import os
from setuptools import setup

setup(
    name = "hs110_exporter",
    version = "0.0.1",
    author = "Michael Sauer",
    author_email = "msa@rzetera.ch",
    description = ("HS110 client for the Prometheus monitoring system."),
    long_description = ("HS110 client for energy monitoring of smart plug"),
    license = "Apache Software License 2.0",
    keywords = "prometheus exporter energy monitoring hs110",
    scripts = ["scripts/hs110_exporter"],
    packages=['hs110_exporter'],
    install_requires=["prometheus_client>=0.4.2"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Networking :: Monitoring",
        "License :: OSI Approved :: Apache Software License"
    ],
)

#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name                            = "autotrax-tools",
    version                         = "git",
    author                          = "Circuit Chaos",
    description                     = "A set of Python tools that aid in using DOS AutoTrax software.",
    url                             = "https://github.com/CircuitChaos/autotrax-tools",
    packages                        = ["pcbfile4"],
    scripts                         = ["pcb-bom", "pcb-drill", "pcb-mil2mm", "pcb-mm2mil", "pcb-psinvert"],
    zip_safe                        = False
)

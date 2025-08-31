"""
Smart Charter Party Generator - Main Package
"""

__version__ = "1.0.0"
__author__ = "Smart Charter Party Generator Team"
__description__ = "Automated Charter Party contract generation from recap documents"

from . import models, parsers, preprocessors, generators, utils, templates

__all__ = ["models", "parsers", "preprocessors", "generators", "utils", "templates"]

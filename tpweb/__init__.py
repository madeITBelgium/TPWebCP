# -*- coding: utf-8 -*-
# Part of TPWeb CP. See LICENSE file for full copyright and licensing details.

""" TPWeb CP core library."""

import sys
MIN_PY_VERSION = (3, 9)
MAX_PY_VERSION = (3, 12)
assert sys.version_info > MIN_PY_VERSION, f"Outdated python version detected, TPWeb CP requires Python >= {'.'.join(map(str, MIN_PY_VERSION))} to run."

from . import cli
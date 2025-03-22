#!/usr/bin/env python3
"""
Unit tests for the Vyom report generation functionality.
"""

import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import sys
# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import from the local vyom package
from vyom.viewer.viewer import launch_report_interface
from vyom.viewer.report import load_data, generate_markdown_report

# ... rest of the file remains the same ... 
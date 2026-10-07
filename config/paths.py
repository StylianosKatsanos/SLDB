# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 11:46:46 2026

@author: stkats
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_ROOT = PROJECT_ROOT / "ClientDatabase"
DATABASE_ROOT.mkdir(exist_ok=True)

CLIENT_DB = DATABASE_ROOT / "Projects_2025.db"

# Must match the folder name in the repository exactly (Linux and macOS are case-sensitive).
SLD_DB_ROOT = DATABASE_ROOT / "sld_databases"
SLD_DB_ROOT.mkdir(exist_ok=True)
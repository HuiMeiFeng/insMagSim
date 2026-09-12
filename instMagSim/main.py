# Copyright (c) 2026 Hui-Mei Feng
# Distributed under MIT License, see LICENSE file.

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from inst_mag_sim import insMagSim



if __name__ == "__main__":
    # Example usage
    dataPath = './data'
    outputPath = './output'
    insMagSim(dataPath, outputPath)
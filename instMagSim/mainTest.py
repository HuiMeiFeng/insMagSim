# Copyright (c) 2026 Hui-Mei Feng
# Distributed under MIT License, see LICENSE file.

import unittest
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from inst_mag_sim import insMagSim


class CsstfgsPolyMatch(unittest.TestCase):
    def test_ins_mag_sim(self):

        '''
        Aim
        --
        Test 'insMagSim' function.

        Criteria
        ---
        The input file created.

        Details
        -----
        Use 'insMagSim' function to output the file.
        If the file doesn't exist, then raise 'AssertionError'.
        '''
        dataPath = './data'
        outputPath = './output'

        numPool = 10
        insMagSim(dataPath, outputPath)
        self.assertTrue(os.path.exists(outputPath + '/colorIdx_fit.png'))
        self.assertTrue(os.path.exists(outputPath + '/colorIdx.csv'))


if __name__ == '__main__':
    unittest.main()

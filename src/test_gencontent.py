import unittest
from gencontent import *

class TestGenContent(unittest.TestCase):

    def test_extract_title(self):
        text=extract_title("#first\n## second\n# Title\n third # ")
        self.assertEqual(text, "Title")


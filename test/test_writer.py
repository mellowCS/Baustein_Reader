''' Tests funtions from the writer module. '''

import unittest

from src import writer


class WriterTests(unittest.TestCase):
    ''' Tests funtions from the writer module. '''

    def test_format_output_text(self):
        '''
            Tests that every 12th space
            is correctly replaced by a newline.
        '''

        self.assertEqual(
            writer.format_output_text(
                'a b c d e f g h i j k l m n.'
            ),
            'a b c d e f g h i j k l \nm n.'
        )

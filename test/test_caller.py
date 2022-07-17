''' Tests for the caller. '''

from unittest import TestCase
from unittest.mock import patch
from pathlib import Path
import sys

sys.path.append('..')

import caller # noqa


class CallerTests(TestCase):
    ''' Tests for the caller. '''

    def test_is_file(self):
        ''' Tests if the path is correctly validated.'''

        with patch.object(Path, 'is_file') as mock_is_file:
            mock_is_file.return_value = True
            self.assertEqual(
                Path('mock_file.pdf'),
                caller.is_file(
                    'mock_file.pdf'
                )
            )

    def test_is_file_error(self):
        ''' Tests if the path is correctly recognized as invalid. '''

        with self.assertRaises(ValueError):
            caller.is_file(
                'error.pdf'
            )

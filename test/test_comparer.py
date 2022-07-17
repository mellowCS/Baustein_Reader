'''
Tests the comparison between Anforderungen.
'''

import unittest

from src import comparer


class ComparerTests(unittest.TestCase):
    ''' Tests the comparison between Anforderungen. '''

    def setUp(self) -> None:
        self.requirements_old = {
            10: ('SYS.1.1.A10 title', 'some text'),
        }

        self.requirements_new = {
            10: ('SYS.1.1.A10 title', 'some changed text'),
            11: ('SYS.1.1.A11 title', 'some other text'),
        }

    def test_extract_additional_requirements(self):
        ''' Tests that additional requirements are correctly extracted. '''

        self.assertEqual(
            comparer.extract_additional_requirements(
                self.requirements_old,
                self.requirements_new,
            ),
            (
                {11: ('SYS.1.1.A11 title', 'some other text'), },
                {10: ('SYS.1.1.A10 title', 'some changed text'), },
            ),
        )

    def test_compare_requirements(self):
        ''' Tests that the comparison between two requirements is correct. '''

        result = comparer.compare_requirements(
            self.requirements_old[10],
            self.requirements_new[10],
        )

        self.assertEqual(result[0], 100)
        self.assertLess(result[1], 100)

        result = comparer.compare_requirements(
            self.requirements_old[10],
            self.requirements_new[11],
        )

        self.assertLess(result[1], 100)
        self.assertLess(result[1], 100)

    def test_additional_requirements_were_added(self):
        ''' Tests that it correctly identifies that additional requirements were added. '''

        self.assertTrue(comparer.additional_requirements_were_added(
            self.requirements_old,
            self.requirements_new
        ))

        self.requirements_new.popitem()

        self.assertFalse(comparer.additional_requirements_were_added(
            self.requirements_old,
            self.requirements_new
        ))

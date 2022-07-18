'''
Tests for the pdf reader.
'''

import re
import unittest
from pathlib import Path
from unittest.mock import patch

from src import reader


class ReaderTests(unittest.TestCase):
    ''' Tests for the pdf reader. '''

    def setUp(self):
        self.input_text_requirement =\
            'SYS.1.1.A11 Festlegung einer Sicherheitsrichtlinie für Server (S)\n' \
            'text.\n' \
            'SYS.1.1.A10 Protokollierung (S)'

        self.input_text_last_requirement_of_current_security_assessment =\
            'SYS.1.1.A11 Festlegung einer Sicherheitsrichtlinie für Server (B)\n' \
            'text.\n' \
            '3.2 Standard-Anforderungen' \
            'SYS.1.1.A10 Protokollierung (S)'

        self.input_text_last_requirement =\
            'SYS.1.1.A11 Festlegung einer Sicherheitsrichtlinie für Server (S)\n' \
            'text.\n' \
            '4. Weiterführende Informationen'

        self.output_text =\
            '\ntext.\n'

        self.title_match = re.search(r'.*', '-'*65)

        self.next_title_match = re.search(r'[^\-]+', '-'*72 + '(S)')

    def test_current_security_assessment_has_changed(self):
        ''' Tests if a change of the Schutzbedarf is correctly recognized. '''

        self.assertTrue(reader.current_security_assessment_has_changed('(B)', 'Title (S)'))
        self.assertFalse(reader.current_security_assessment_has_changed('(B)', 'Title (B)'))

    def test_get_security_assessment(self):
        ''' Tests if the Schutzbedarf is correctly extracted from the title. '''

        self.assertEqual(reader.get_security_assessment('Title (S)'), '(S)')

    def test_get_index_of_chapter_titles(self):
        '''
            Tests if the index of the first character
            of the chapter title is correctly returned.
        '''

        input_text = '123456789\n3.2. Standard-Anforderungen'

        self.assertEqual(10, reader.get_index_of_chapter_title('(S)', input_text))

    def test_remove_header_and_footer(self):
        ''' Test if the footer and header are correctly removed from the text.'''

        doc_title = 'SYS.1.1 Allgemeiner Server'

        input_text = 'mindestens:\nSYS.1.1 Allgemeiner Server\n' \
                     'Stand Februar 2022 Seite 5 von 9\n• Systemstarts und Reboots,'

        output_text = 'mindestens:\n• Systemstarts und Reboots,'

        self.assertEqual(reader.remove_header_and_footer(input_text, doc_title), output_text)

    def test_remove_whitespaces(self):
        ''' Tests that the text is correctly normalized. '''

        self.assertEqual(
            reader.remove_whitespaces('\n\nsome text\rsome more text\neven more text.\r'),
            'some text some more text even more text.'
        )

    def test_get_requirements(self):
        ''' Tests if the anforderungen are extracted from the file. '''

        input_text =\
            'SYS.1.1.A9 Protokollierung (B)\n' \
            'text.\n' \
            'SYS.1.1.A10 Protokollierung (B)\n' \
            'text.\n' \
            'SYS.1.1 Allgemeiner Server\n' \
            'Stand Februar 2022 Seite 5 von 9\n' \
            'more text.\n' \
            '3.2. Standard-Anforderungen\n' \
            'chapter intro.\n' \
            'SYS.1.1.A11 Festlegung einer Sicherheitsrichtlinie für Server (S)\n' \
            'even more text.\n' \
            '4. Weiterführende Informationen'

        output_dict = {
            9: (
                'SYS.1.1.A9 Protokollierung (B)',
                'text.',
            ),
            10: (
                'SYS.1.1.A10 Protokollierung (B)',
                'text. more text.',
            ),
            11: (
                'SYS.1.1.A11 Festlegung einer Sicherheitsrichtlinie für Server (S)',
                'even more text.',
            )
        }

        self.assertEqual(
            reader.get_requirements(input_text, 'SYS.1.1 Allgemeiner Server'),
            output_dict
        )

    def test_get_single_requirement(self):
        ''' Tests that an requirement is correctly extracted from the text. '''

        self.assertEqual(
            reader.get_single_requirement(
                text=self.input_text_requirement,
                requirement_titles=[self.title_match, self.next_title_match],
                current_security_assessment='(S)',
                index=0,
                title=self.title_match
            ),
            (self.output_text, '(S)'),
        )

        self.assertEqual(
            reader.get_single_requirement(
                text=self.input_text_last_requirement_of_current_security_assessment,
                requirement_titles=[self.title_match, self.next_title_match],
                current_security_assessment='(B)',
                index=0,
                title=self.title_match
            ),
            (self.output_text, '(S)'),
        )

        self.assertEqual(
            reader.get_single_requirement(
                text=self.input_text_last_requirement,
                requirement_titles=[self.title_match, self.next_title_match],
                current_security_assessment='(S)',
                index=1,
                title=self.title_match
            ),
            (self.output_text, '(S)'),
        )

    def test_get_last_requirement_of_current_security_assessment_from_document(self):
        '''
            Tests that the last requirement of the current
            security assessment is correctly returned
            from the document.
        '''

        self.assertEqual(
            reader.get_last_requirement_of_current_security_assessment_from_document(
                self.input_text_last_requirement_of_current_security_assessment,
                self.title_match,
                '(S)'
            ),
            self.output_text,
        )

    def test_get_requirement_from_document(self):
        ''' Tests that the requirement is correctly returned from the document. '''

        self.assertEqual(
            reader.get_requirement_from_document(
                self.input_text_requirement,
                self.title_match,
                self.next_title_match
            ),
            self.output_text,
        )

    def test_get_last_requirement_from_document(self):
        ''' Tests that the last requirement is correctly returned from the document.'''

        self.assertEqual(
            reader.get_last_requirement_from_document(
                self.input_text_last_requirement,
                self.title_match
            ),
            self.output_text,
        )

    def test_get_document_title(self):
        ''' Tests that the document title is correctly extracted from the filename.'''

        self.assertEqual(
            reader.get_document_title(
                'SYS.3.2: Tablet und Smartphone\r\n'
                'SYS.3.2.2: Mobile Device \r\n'
                'Management (MDM)\r\n'
                '1 Beschreibung'
            ),
            'SYS.3.2.2 Mobile Device Management (MDM)',
        )

    def test_get_text_from_file(self):
        ''' Tests if the text is correctly extracted from the file. '''

        with self.assertRaises((FileNotFoundError, SystemExit)):
            reader.get_text_from_file(Path('wrong_path.pdf'))

        with patch('builtins.open') as mock_file:
            mock_file.side_effect = ValueError
            with self.assertRaises((ValueError, SystemExit)):
                reader.get_text_from_file('filename')

            mock_file.side_effect = IOError()
            with self.assertRaises((IOError, SystemExit)):
                reader.get_text_from_file('filename')

'''
This module reads in the text from the Baustein and
parses the requirements.
'''

import sys
import re
from pathlib import Path
from typing import Tuple, Match

import pypdfium2 as pdfium

# Matches every requirement title. e.g. SYS.1.1.A1 Geeignete Aufstellung (B)
REQUIREMENTS_PATTERN =\
    r'^[A-Z]{3,}[\.\d]+A\d+[\w\-,\[\] ]*[\r\n]{,2}[\w\-,\[\] ]*\((?:B|S|H)\)'

# Retrieves the number of the requirement from the title.
# e.g. SYS.1.1.A1 Geeignete Aufstellung (B) -> 1
REQUIREMENT_NUMBER_PATTERN = r'.*A(\d{,2}) .*'

# Part of the pattern that matches every header in the document.
# For instance, the header can either be
# "IT-Grundschutz | SYS.1.1 Allgemeiner Server" for 2021 or
# "SYS.1.1 Allgemeiner Server" for 2022
# The other part is parsed from the document title dynamically.
HEADER_SUB_PATTERN =\
    r'\n(?:IT-Grundschutz \| )?'

# Matches every footer in the document.
# e.g Stand Februar 2022 Seite 4 von 9
FOOTER_PATTERN =\
    r'\nStand[\w ]+ Seite \d von \d'

# Matches the chapter titles between requirements with different security assessments.
REQUIREMENT_CHAPTERS = {
    '(S)': r'3.2(?:\.)? Standard-Anforderungen',
    '(H)': r'3.3(?:\.)? Anforderungen bei erhöhtem Schutzbedarf'
}

# Matches the chapter title after requirements with the highest security assessment.
INFORMATION_CHAPTER_PATTERN = r'4(?:\.)? Weiterführende Informationen'

# Is used to parse the document title from the filename.
# e.g. SYS_1_1_Allgemeiner_Server -> SYS.1.1 Allgemeiner Server
SUB_UNDERSCORE_FOR_SPACE_PATTERN = r'(?<=\w)(?:\_)(?=[A-Za-z])'
SUB_UNDERSCORE_FOR_DOT_PATTERN = r'(?<=\w)(?:\_)(?=\d)'

# Matches all whitespace characters. Is used to normalize any given text.
WHITESPACE_PATTERN = r'\s+'

BASIS = '(B)'


def current_security_assessment_has_changed(current_security_assessment: str, title: str) -> bool:
    ''' Checks whether the current security assessment has changed. '''

    if current_security_assessment not in title:
        return True

    return False


def get_security_assessment(title: str) -> str:
    ''' Get the security assessment from the title. '''

    return title[len(title)-3:]


def get_index_of_chapter_title(current_security_assessment: str, text: str) -> int:
    ''' Returns the index of the chapter title of the current security assessment in the pdf. '''

    return re.search(REQUIREMENT_CHAPTERS[current_security_assessment], text).start(0)


def remove_header_and_footer(text: str, doc_title: str) -> str:
    ''' Sanitizes the text and removes unnecessary information. '''

    text = re.sub(HEADER_SUB_PATTERN + re.escape(doc_title), '', text)

    text = re.sub(FOOTER_PATTERN, '', text)

    return text.strip()


def remove_whitespaces(requirement: str) -> str:
    '''
        Normalizes the text and subs all newlines, carriage returns etc.
        with horizontal single spaces.
    '''

    return re.sub(WHITESPACE_PATTERN, ' ', requirement).strip()


def get_requirements(text: str, doc_title: str) -> dict[int, Tuple[str, str]]:
    ''' Sanitizes the texts returned from the pdf to remove unnecessary information. '''

    text = remove_header_and_footer(text, doc_title)
    requirement_titles = list(re.finditer(REQUIREMENTS_PATTERN, text, re.MULTILINE))
    current_security_assessment = BASIS

    requirements = {}
    for index, title in enumerate(requirement_titles):
        requirement, current_security_assessment = get_single_requirement(
            text,
            requirement_titles,
            current_security_assessment,
            index,
            title
        )

        title_text = remove_whitespaces(title.group(0))
        requirements[int(re.search(REQUIREMENT_NUMBER_PATTERN, title_text).group(1))] =\
            (title_text, remove_whitespaces(requirement))

    return requirements


def get_single_requirement(
    text: str,
    requirement_titles: list[Match[str]],
    current_security_assessment: str,
    index: int,
    title: Match[str],
) -> Tuple[str, str]:
    ''' Extracts a single requirement from the text with the appropriate index. '''

    if index < len(requirement_titles)-1:
        next_title_match = requirement_titles[index+1]
        if current_security_assessment_has_changed(
                current_security_assessment,
                next_title_match.group(0)
        ):
            current_security_assessment = get_security_assessment(next_title_match.group(0))
            requirement =\
                get_last_requirement_of_current_security_assessment_from_document(
                    text,
                    title,
                    current_security_assessment
                )
        else:
            requirement =\
                get_requirement_from_document(text, title, next_title_match)
    else:
        requirement = get_last_requirement_from_document(text, title)

    return requirement, current_security_assessment


def get_last_requirement_of_current_security_assessment_from_document(
    text: str,
    title: Match[str],
    current_security_assessment: str
):
    '''
        Gets the last requirement of the current
        security assessment from the document.
    '''

    return text[
        title.end(0):get_index_of_chapter_title(
            current_security_assessment,
            text
        )
    ]


def get_requirement_from_document(
    text: str,
    title: Match[str],
    next_title_match: Match[str]
):
    ''' Gets a requirement from the document. '''

    return text[title.end(0):next_title_match.start(0)]


def get_last_requirement_from_document(text: str, title: Match[str]):
    '''
        Returns the last requirement from the
        requirement list in the document.
    '''

    return text[
        title.end(0):re.search(INFORMATION_CHAPTER_PATTERN, text).start(0)
    ]


def get_document_title(filename: str) -> str:
    ''' Extracts the document title from the filename. '''

    doc_title = filename[:-17]
    doc_title = re.sub(SUB_UNDERSCORE_FOR_SPACE_PATTERN, ' ', doc_title)
    doc_title = re.sub(SUB_UNDERSCORE_FOR_DOT_PATTERN, '.', doc_title)

    return doc_title


def get_text_from_file(filepath: Path) -> str:
    ''' Collects the text from all pages of a given pdf file. '''

    try:
        with pdfium.PdfDocument(str(filepath)) as pdf:
            return '\n'.join(
                    [
                        pdf.get_page(index).get_textpage().get_text()
                        for index in range(0, len(pdf))
                    ]
            )
    except FileNotFoundError:
        print(f'File at {filepath} not found.', file=sys.stderr)
    except pdfium.PdfiumError as pdf_err:
        print(pdf_err, file=sys.stderr)
    except IOError as io_err:
        print(io_err, file=sys.stderr)

    sys.exit(1)

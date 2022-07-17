''' This modules contains functions for writing the results to a file. '''

import re
from typing import Tuple
from collections import OrderedDict

TITLE = 0
TEXT = 1

# Matches every 12th horizontal whitespace character.
SPACE_12_PATTERN = r'(?:[^ ]*( )){12}'

# Contains an overview about the comparison file.
TITLE_INFO =\
    '#############################################################' \
    '#############################################################\n' \
    '#\n' \
    '#\tResults for the comparison of the modules {} ' \
    'of the years 2022 and 2021\n' \
    '#\tThis list indicates where differences between requirements were made.\n' \
    '#\tIt also shows which requirements were added and which were removed.\n' \
    '#\n' \
    '#############################################################' \
    '#############################################################\n\n' \
    '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ CHANGED REQUIREMENTS ' \
    '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'

# Contains the text for the display of the comparison between two requirements.
REQUIREMENT_COMPARE_TEXT =\
    '\nRESULT:\n'\
    '  Requirement {},\n' \
    '  Title Similarity: {}%,\n' \
    '  Text Similarity: {}%\n\n' \
    '######## Requirement 2022 ########\n\n' \
    '{}\n' \
    '{}' \
    '\n\n######## Requirement 2021 ########\n\n' \
    '{}\n' \
    '{}' \
    '\n\n---------------------------------------------------------' \
    '----------------------------------------------------------------\n'

# Contains the title text for additional requirements.
ADDITIONAL_REQUIREMENTS_TITLE =\
    '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ADDITIONAL REQUIREMENTS ' \
    '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n'


def format_output_text(text) -> str:
    ''' Replace every 12th occurrence of space with a newline. '''

    for counter, space in enumerate(re.finditer(SPACE_12_PATTERN, text)):
        text = text[:space.start(1)+counter] + ' \n' + text[space.start(1)+counter+1:]

    return text


def write_results_to_file(
    doc_title: str,
    results: list[Tuple[int, int, int]],
    sorted_requirements_old: OrderedDict[int, Tuple[str, str]],
    sorted_requirements_new: OrderedDict[int, Tuple[str, str]],
    additional_requirements: OrderedDict[int, Tuple[str, str]],
) -> None:
    ''' Writes the results of the module comparison to a text file. '''

    try:
        with open(f'{doc_title} - differences.txt', 'w', encoding="utf-8") as file:
            file.write(TITLE_INFO.format(doc_title) + '\n')

            for requirement_number, title_result, text_result in results:
                if title_result < 100 or text_result < 100:
                    file.write(REQUIREMENT_COMPARE_TEXT.format(
                        requirement_number,
                        title_result,
                        text_result,
                        sorted_requirements_new[requirement_number][TITLE],
                        format_output_text(sorted_requirements_new[requirement_number][TEXT]),
                        sorted_requirements_old[requirement_number][TITLE],
                        format_output_text(sorted_requirements_old[requirement_number][TEXT])
                    ))

            if additional_requirements:
                file.write(ADDITIONAL_REQUIREMENTS_TITLE)
                for title, text in additional_requirements.values():
                    file.write(
                        f'{title}\n'
                        f'{format_output_text(text)}\n\n'
                    )
    except IOError as io_err:
        print(io_err)

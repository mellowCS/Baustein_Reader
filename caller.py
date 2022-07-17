''' This module combines the functions of the reader, comparer and writer module. '''

import argparse
from pathlib import Path
from typing import Tuple
from collections import OrderedDict

from src import (
    reader,
    comparer,
    writer
)


def is_file(path: str) -> Path:
    ''' Checks whether the given path is valid and if so, returns it as a Path object. '''

    file = Path(path)
    if file.is_file():
        return file

    raise ValueError(f'File could not be found at {path}.')


def parse_args() -> argparse.Namespace:
    ''' Parses the arguments given by the user. '''

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--file-old', '-fo',
        dest='file_old',
        required=True,
        help='The path to the old PDF file to read',
        metavar='PATH',
        type=is_file,
    )

    parser.add_argument(
        '--file-new', '-fn',
        dest='file_new',
        required=True,
        help='The path to the new PDF file to read',
        metavar='PATH',
        type=is_file,
    )

    return parser.parse_args()


def main() -> None:
    ''' Main function '''

    args = parse_args()

    doc_title = reader.get_document_title(str(args.file_old).rsplit('/')[1])

    requirements_old = reader.get_requirements(
        reader.get_text_from_file(args.file_old),
        doc_title
    )
    requirements_new = reader.get_requirements(
        reader.get_text_from_file(args.file_new),
        doc_title
    )

    additional_requirements: dict[int, Tuple[str, str]] = {}
    if comparer.additional_requirements_were_added(requirements_old, requirements_new):
        additional_requirements, requirements_new =\
            comparer.extract_additional_requirements(
                requirements_old,
                requirements_new,
            )

    sorted_requirements_old = OrderedDict(sorted(requirements_old.items()))
    sorted_requirements_new = OrderedDict(sorted(requirements_new.items()))

    results = comparer.compare_modules(sorted_requirements_old, sorted_requirements_new)

    writer.write_results_to_file(
        doc_title,
        results,
        sorted_requirements_old,
        sorted_requirements_new,
        additional_requirements
    )


if __name__ == '__main__':
    main()

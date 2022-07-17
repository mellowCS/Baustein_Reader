'''
Compares the requirements of two Grundschutz Check modules
for differences in the wording.
The Comparison is based on the Levenshtein Distance:
    https://en.wikipedia.org/wiki/Levenshtein_distance
'''

from typing import Tuple, OrderedDict

from fuzzywuzzy import fuzz

TITLE = 0
TEXT = 1


def extract_additional_requirements(
    requirements_old: dict[int, Tuple[str, str]],
    requirements_new: dict[int, Tuple[str, str]]
) -> Tuple[dict[int, Tuple[str, str]], dict[int, Tuple[str, str]]]:
    ''' Extracts additional requirements from the new requirements. '''

    additional_requirements = {}

    for number in set(requirements_new.keys()).difference(
        set(requirements_old.keys())
    ):
        additional_requirements[number] = requirements_new.pop(number)

    return additional_requirements, requirements_new


def compare_requirements(
    requirements_old: Tuple[str, str],
    requirements_new: Tuple[str, str]
) -> Tuple[int, int]:
    ''' Compares two requirements for differences in the wording. '''

    return (
        fuzz.ratio(requirements_old[TITLE], requirements_new[TITLE]),
        fuzz.ratio(requirements_old[TEXT], requirements_new[TEXT])
    )


def additional_requirements_were_added(
    requirements_old: dict[int, Tuple[str, str]],
    requirements_new: dict[int, Tuple[str, str]]
) -> bool:
    ''' Checks whether the additional requirements were added. '''

    if len(requirements_old) < len(requirements_new):
        return True

    return False


def compare_modules(
    requirements_old: OrderedDict[int, Tuple[str, str]],
    requirements_new: OrderedDict[int, Tuple[str, str]]
) -> list[Tuple[int, int, int]]:
    ''' Compares two modules for differences in their requirements. '''

    comparison_results: list[Tuple[int, int]] = []

    for number, old, new in zip(
        requirements_old.keys(),
        requirements_old.values(),
        requirements_new.values()
    ):
        comparison_results.append((number,) + compare_requirements(old, new))

    return comparison_results

""" Utilities for groups """

import re


NUMBER_PATTERN = r'[^0-9]'


def normalize_number(number):
    """ Strip all non-numeric characters from phone numbers """
    return re.sub(NUMBER_PATTERN, '', number)

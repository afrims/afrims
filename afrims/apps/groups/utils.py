""" Utilities for groups """

import re
from django.conf import settings


NUMBER_PATTERN = r'[^0-9]'


def normalize_number(number):
    """ Strip all non-numeric characters from phone numbers """
    normalized_number = re.sub(NUMBER_PATTERN, '', number)
    if len(normalized_number) == 10:
        # missing country code
        if (hasattr(settings, 'COUNTRY_CODE') and settings.COUNTRY_CODE):
            normalized_number = '{0}{1}'.format(settings.COUNTRY_CODE,
                                                normalized_number)
    return normalized_number

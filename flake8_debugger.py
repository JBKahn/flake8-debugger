import pep8
import re

__version__ = '1.1'

DEBUGGER_REGEX = re.compile(r'(import i?pdb|i?pdb.set_trace())')


def check_debug_statements(physical_line):
    if pep8.noqa(physical_line):
        return
    match = DEBUGGER_REGEX.search(physical_line)
    if match:
        return match.start(), 'T000 pdb/ipdb found.'


check_debug_statements.name = name = 'flake8-debugger'
check_debug_statements.version = __version__

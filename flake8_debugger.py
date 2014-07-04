import pep8
import re

__version__ = '1.2'

DEBUGGER_REGEX = re.compile(r'(import i?pdb|i?pdb.set_trace())')
DEBUGGER_ERROR_CODE = 'T002'
DEBUGGER_ERROR_MESSAGE = 'pdb/ipdb found.'


def check_debug_statements(physical_line):
    if pep8.noqa(physical_line):
        return
    physical_line = re.sub(r'\"\"\"(.+?)\"\"\"', "", physical_line)
    physical_line = re.sub(r'\"(.+?)\"', "", physical_line)
    physical_line = re.sub(r'\'\'\'(.+?)\'\'\'', "", physical_line)
    physical_line = re.sub(r'\'(.+?)\'', "", physical_line)
    physical_line = re.sub(r'#(.+)', "#", physical_line)
    match = DEBUGGER_REGEX.search(physical_line)
    if match:
        return match.start(), '{} {}'.format(DEBUGGER_ERROR_CODE, DEBUGGER_ERROR_MESSAGE)


check_debug_statements.name = name = 'flake8-debugger'
check_debug_statements.version = __version__

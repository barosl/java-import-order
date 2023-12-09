#!/usr/bin/env python3

import argparse
from pathlib import Path
import re
from functools import reduce

def conv(text):
    lines = text.splitlines()
    import_start_line_num = None
    import_end_line_num = None
    for line_num, line in enumerate(lines):
        if re.search(r'^/*import\b', line):
            if import_start_line_num is None:
                import_start_line_num = line_num
            import_end_line_num = line_num + 1
    if import_start_line_num is None or import_end_line_num is None:
        return None, 'No import statements'

    groups_of_imports = {x: [] for x in ['others', 'javax', 'java', 'static']}
    for line in lines[import_start_line_num:import_end_line_num]:
        if re.search(r'\bimport\s+java\.', line):
            groups_of_imports['java'].append(line)
        elif re.search(r'\bimport\s+javax\.', line):
            groups_of_imports['javax'].append(line)
        elif re.search(r'\bimport\s+static', line):
            groups_of_imports['static'].append(line)
        elif re.search(r'\bimport\s+', line):
            groups_of_imports['others'].append(line)
        elif re.search(r'^\s*$', line):
            pass
        else:
            return None, 'Unrecognizable import statement: ' + line
    for cur_lines in groups_of_imports.values():
        cur_lines.sort()
    imports_separated_by_blank_line = [groups_of_imports['others'], groups_of_imports['javax'] + groups_of_imports['java'], groups_of_imports['static']]
    imports_separated_by_blank_line = [x for x in imports_separated_by_blank_line if x]
    imports_separated_by_blank_line = reduce(lambda a, b: a + [''] + b, imports_separated_by_blank_line)
    new_lines = lines[:import_start_line_num] + imports_separated_by_blank_line + lines[import_end_line_num:]
    if lines == new_lines:
        return None, 'Already sorted'
    new_text = ''.join(x + '\n' for x in new_lines)
    return new_text, None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('file', nargs='+')
    args = ap.parse_args()

    for fpath in args.file:
        print(fpath, end=': ')
        text = Path(fpath).read_text()
        new_text, err = conv(text)
        if err:
            print(err)
        else:
            print('OK')
            Path(fpath).write_text(new_text)

if __name__ == '__main__':
    main()

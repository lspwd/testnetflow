#!/usr/bin/env python

import re
import argparse
import sys
import logging



log_ok = []
log_ko = []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--logFile', action='store')
    args = parser.parse_args()
    log_file = open(args.logFile, 'r')
    try:
        for row in log_file.readlines():
            ok = re.match(".*are enabled", row)
            ko = re.match(".*are not enabled", row)
            if ok is not None:
                log_ok.append(row)
            if ko is not None:
                log_ko.append(row)
    finally:
        log_file.close()
        sys.stdout.writelines(log_ok)
        # print(50 * '#')
        if len(log_ko) > 0:
            sys.stderr.writelines(log_ko)
            sys.exit(1)


if __name__ == '__main__':
    main()

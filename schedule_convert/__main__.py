#!/usr/bin/env python3
import argparse
from .importers import importers
from .exporters import exporters


parser = argparse.ArgumentParser(description='Converts any schedule to a frab-compatible XML')
parser.add_argument('input', nargs='+', type=argparse.FileType('r'), help='Input file, one or more')
parser.add_argument('-o', '--output', type=argparse.FileType('w'), help='Output file')
parser.add_argument('-f', '--format', default='xml', help='Output format (default=xml)')
options = parser.parse_args()

schedule = None
for i in options.input:
    head = i.read(5000)
    i.seek(0)
    conf = None
    for imp in importers:
        if imp.check(head):
            conf = imp.parse(i)
    if not conf:
        print('Error: could not determine format for {}'.format(i.name))
    elif schedule is None:
        if conf.needs_data:
            print('Cannot instantiate the schedule, it needs base data like title')
        else:
            schedule = conf
    else:
        schedule.merge(conf)

if schedule is None:
    print('No schedule to export')
else:
    exporters[options.format].write(options.output, schedule)

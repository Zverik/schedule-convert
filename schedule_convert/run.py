import argparse
import sys
import logging
from .model import SimpleTZ
from .importers import importers
from .exporters import exporters
from .landing import make_schedule_name, make_landing_page


def main():
    parser = argparse.ArgumentParser(description='Converts any schedule to a frab-compatible XML')
    parser.add_argument('input', nargs='+', type=argparse.FileType('r'),
                        help='Input file, one or more')
    parser.add_argument('-z', '--tz', help='Override timezone (as +NN/-NN or pNN/mNN)')
    parser.add_argument('-o', '--output', type=argparse.FileType('w'),
                        default=sys.stdout, help='Output file')
    parser.add_argument('-f', '--format', default='xml', help='Output format (default=xml)')
    parser.add_argument('-l', '--landing', nargs=2, help='Generate landing page with QR codes; '
                        'specify an output path and a base URL for schedules, '
                        'e.g. -l output http://conf.ru/schedule. Needs input: also '
                        'generates schedules')
    options = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(message)s')

    schedule = None
    for i in options.input:
        head = i.read(5000)
        i.seek(0)
        conf = None
        for imp in importers:
            if imp.check(head):
                conf = imp.parse(i)
                if options.tz:
                    conf.timezone = SimpleTZ(options.tz)
                conf.prepare()
        if conf is None:
            logging.error('Error: could not determine format for %s', i.name)
        elif schedule is None:
            if conf.needs_data:
                logging.error('Cannot instantiate the schedule, it needs base data like title')
            else:
                schedule = conf
        else:
            schedule.merge(conf)

    if schedule is None:
        logging.warning('No schedule to export')
    elif schedule.is_empty():
        logging.warning('Schedule is empty')
    else:
        if options.landing:
            for fmt in ('xml', 'ical'):
                exp = exporters[fmt]
                with open(make_schedule_name(*options.landing, ext=exp.extension), 'w') as f:
                    exp.write(f, schedule)
            make_landing_page(schedule, *options.landing)
        else:
            exporters[options.format].write(options.output, schedule)


if __name__ == '__main__':
    main()

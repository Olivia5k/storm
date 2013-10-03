import re
import subprocess as sub
import logbook
import datetime

INTERVALS = [1, 60, 3600, 86400, 604800, 2419200, 29030400]
NAMES = (
    ('second', 'seconds'),
    ('minute', 'minutes'),
    ('hour', 'hours'),
    ('day', 'days'),
    ('week', 'weeks'),
    ('month', 'months'),
    ('year', 'years')
)


class LoggedClass():
    """
    Abstract class that provdies a configured self.log

    """

    def __init__(self, *args, **kwargs):
        name = self.__class__.__name__
        self.log = logbook.Logger(name)
        # self.log.debug('Loaded logger for {0}', name)


class AcpiBattery(LoggedClass):
    def __init__(self, line):
        self.line = line
        super(AcpiBattery, self).__init__()

    def parse(self):
        rxp = (
            r'Battery (?P<id>\d+): '
            r'(?P<status>\S+), '
            r'(?P<percent>\d+)%'
            r'(, (?P<time>\d\d:\d\d:\d\d) \S+)?'
        )

        match = re.search(rxp, self.line)
        if match:
            data = match.groupdict()

            data['id'], data['percent'] = int(data['id']), int(data['percent'])

            # If we have some time, make something useful out of it
            hrs, mins, secs = 0, 0, 0
            if data['time']:
                hrs, mins, secs = (int(x) for x in data['time'].split(':'))

            data['time'] = datetime.timedelta(
                hours=hrs, minutes=mins, seconds=secs
            )

            self.__dict__.update(data)
        else:
            self.log.error('Bad ACPI line: {0}', self.line)


def humanize_time(amount, units):
    """
    Divide `amount` in time periods.
    Useful for making time intervals more human readable.

    http://stackoverflow.com/questions/6574329/

    """
    result = []

    unit = list(map(lambda a: a[1], NAMES)).index(units)
    # Convert to seconds
    amount = amount * INTERVALS[unit]

    for i in range(len(NAMES)-1, -1, -1):
        a = int(amount / INTERVALS[i])
        if a > 0:
            result.append((a, NAMES[i][1 % a]))
            amount -= a * INTERVALS[i]

    return result


def time_left(seconds):
    if seconds == 0:
        return ""

    items = humanize_time(seconds, 'seconds')
    s = '00:{0:02d}'

    if len(items) == 3:
        # Has hours
        s = '{0}:{1:02d}:{2:02d}'
    elif len(items) == 2:
        # Only has minutes and seconds
        s = '{0:02d}:{1:02d}'

    return s.format(*(int(x[0]) for x in items))


def get_screen_size():
    """
    Use xrandr to get the screen size.

    It would be preferrable to use some kind of library, such as python-xlib,
    but it is too old to work in Python3, and it is non-trivial to port it.
    This will do for now.

    """

    args = ['xrandr', '--display', ':0']
    out = sub.Popen(args, stdout=sub.PIPE).communicate()[0].decode()
    size = re.search(r'\bconnected\b (\d+)x(\d+)', out)
    return int(size.group(1))

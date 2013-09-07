import re
import subprocess as sub
import logbook


class LoggedClass():
    """
    Abstract class that provdies a configured self.log

    """

    def __init__(self, *args, **kwargs):
        name = self.__class__.__name__
        self.log = logbook.Logger(name)
        self.log.debug('Loaded logger for {0}', name)


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

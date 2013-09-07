import re
import subprocess as sub


def get_screen_size():
    """
    Use xrandr to get the screen size.

    It would be preferrable to use some kind of library, such as python-xlib,
    but it is too old to work in Python3, and it is non-trivial to port it.
    This will do for now.

    """

    out = sub.Popen('xrandr', stdout=sub.PIPE).communicate()[0].decode()
    size = re.search(r'\bconnected\b (\d+)x(\d+)', out)
    return int(size.group(1))

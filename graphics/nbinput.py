"""
Most of this code came from this page:
http://code.activestate.com/recipes/134892/#c5
"""

import sys
import select


class NonBlockingInput:
    """
    Gets a single character from standard input. Does not echo to the
        screen.
    """
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            try:
                self.impl = _GetchMacCarbon()
            except (AttributeError, ImportError):
                self.impl = _GetchUnix()

    def char(self):
        return self.impl.char()

    def __enter__(self):
        return self.impl.enter()

    def __exit__(self, type_, value, traceback):
        return self.impl.exit(type_, value, traceback)


class _GetchUnix:
    def __init__(self):
        # Import termios now or else you'll get the Unix version on the Mac.
        import tty
        import termios
        self.tty = tty
        self.termios = termios

    def enter(self):
        self.old_settings = self.termios.tcgetattr(sys.stdin)
        self.tty.setcbreak(sys.stdin.fileno())
        return self

    def exit(self, type_, value, traceback):
        self.termios.tcsetattr(sys.stdin,
            self.termios.TCSADRAIN, self.old_settings)

    def char(self):
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            return sys.stdin.read(1)
        return None


class _GetchWindows:
    def __init__(self):
        import msvcrt
        self.msvcrt = msvcrt

    def enter(self):
        return self

    def exit(self, type_, value, traceback):
        pass

    def char(self):
        return self.msvcrt.getch()


class _GetchMacCarbon:
    """
    A function which returns the current ASCII key that is down;
    if no ASCII key is down, the null string is returned.  The
    page http://www.mactech.com/macintosh-c/chap02-1.html was
    very helpful in figuring out how to do this.
    """
    def __init__(self):
        # See if teminal has this (in Unix, it doesn't)
        import Carbon
        self.Carbon = Carbon
        self.Carbon.Evt

    def enter(self):
        return self

    def exit(self, type_, value, traceback):
        pass

    def char(self):
        if self.Carbon.Evt.EventAvail(0x0008)[0] == 0:  # 0x0008 is the keyDownMask
            return ''
        else:
            # The event contains the following info:
            # (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
            #
            # The message (msg) contains the ASCII char which is
            # extracted with the 0x000000FF charCodeMask; this
            # number is converted to an ASCII character with chr() and
            # returned.

            _, msg, _, _, _ = self.Carbon.Evt.GetNextEvent(0x0008)[1]
            return chr(msg & 0x000000FF)


def main():
    import time
    with NonBlockingInput() as nbi:
        while True:

            if nbi.char() == ' ':
                print('A')
            else:
                print('B')
            time.sleep(.1)


if __name__ == '__main__':
    main()

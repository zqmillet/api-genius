import sys

from pdb import Pdb
from os import fdopen

class ForkablePdb(Pdb):
    """
    this is pdb for forked process.
    """
    _original_stdin_fd = sys.stdin.fileno()
    _original_stdin = None

    def __init__(self):
        Pdb.__init__(self, nosigint=True)

    def _cmdloop(self):
        current_stdin = sys.stdin
        try:
            if not self._original_stdin:
                self._original_stdin = fdopen(self._original_stdin_fd)
            sys.stdin = self._original_stdin
            self.cmdloop()
        finally:
            sys.stdin = current_stdin

def set_trace(*, header=None):
    """
    this is advanced pdb, which can be used in forked pdb.
    """
    pdb = ForkablePdb()
    if header is not None:
        pdb.message(header)
    pdb.set_trace(sys._getframe().f_back) # pylint: disable = protected-access

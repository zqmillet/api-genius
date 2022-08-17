from fastapi import APIRouter
from fastapi import Request

import pdb
import sys
import os

class ForkablePdb(pdb.Pdb):

    _original_stdin_fd = sys.stdin.fileno()
    _original_stdin = None

    def __init__(self):
        pdb.Pdb.__init__(self, nosigint=True)

    def _cmdloop(self):
        current_stdin = sys.stdin
        try:
            if not self._original_stdin:
                self._original_stdin = os.fdopen(self._original_stdin_fd)
            sys.stdin = self._original_stdin
            self.cmdloop()
        finally:
            sys.stdin = current_stdin

class Router(APIRouter):
    def add_tabulate_api(self, session_class, model):
        @self.get('/')
        def get(request: Request) -> str:
            ForkablePdb().set_trace()
            return 'hello world'

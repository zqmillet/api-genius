from fastapi import APIRouter
from fastapi import Request

class Router(APIRouter):
    def add_tabulate_api(self, session_class, model):
        @self.get('/')
        def get(request: Request) -> str:
            return 'hello world'

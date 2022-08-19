from fastapi import APIRouter
from fastapi import Request
from action_words.set_trace import set_trace

class Router(APIRouter):
    """
    this class is a subclass of the class APIRouter of fastapi module.
    it provides additional method for auto api generation.
    """
    def add_tabulate_api(self, session_class, model):
        """
        this method is used to generate tabulate api of a model.
        """
        @self.get('/')
        def get(request: Request) -> str:
            set_trace()
            return 'hello world'

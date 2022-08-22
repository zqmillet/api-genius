from fastapi import APIRouter
from fastapi import Request
from action_words.set_trace import set_trace

class Router(APIRouter):
    """
    this class is a subclass of the class APIRouter of fastapi module.
    it provides additional method for auto api generation.
    """
    def add_tabulate_api(self, path, session_class, model):
        """
        this method is used to generate tabulate api of a model.
        """
        set_trace()

        @self.get(path)
        def get(request: Request) -> str:
            set_trace()
            return 'hello world'

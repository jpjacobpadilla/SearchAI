from .filters import Filters

class AsyncSearchAI:
    def __init__(self, proxy: str):
        self.proxy = proxy

    async def search(
            self,
            query: str,
            operators: Filters | None = None,
            length: int = 10,
            offset: int = 0,
            unique: bool = False,
            lang: str = 'en',
            region: str | None = None
    ):
        pass

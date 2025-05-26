from typing import Literal, Optional
from pydantic import BaseModel, Field


class Proxy(BaseModel):
    protocol: Literal['http', 'https', 'socks4', 'socks5'] = Field(..., description='Proxy protocol')
    host: str = Field(..., description='Proxy server host or IP')
    port: int = Field(..., ge=1, le=65535, description='Proxy server port')
    username: Optional[str] = Field(None, description='Username for proxy auth')
    password: Optional[str] = Field(None, description='Password for proxy auth')

    def to_httpx_proxy_url(self) -> str:
        auth = f'{self.username}:{self.password}@' if self.username and self.password else ''
        return f'{self.protocol}://{auth}{self.host}:{self.port}'

    def to_playwright_proxy(self) -> dict:
        proxy = {'server': f'{self.protocol}://{self.host}:{self.port}'}

        if self.username:
            proxy['username'] = self.username
        if self.password:
            proxy['password'] = self.password

        return proxy

import aiohttp
from aiohttp import web

from src.config import config
from src.logger import setup_logger

logger = setup_logger()

class ProxyService:
    def __init__(self):
        self.session = None  # Отложенная инициализация сессии

    async def init_session(self):
        """Инициализирует сессию aiohttp.ClientSession."""
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def proxy_request(self, method, url_path, headers, body):
        """Proxy the request to the target host."""
        if self.session is None:
            raise RuntimeError("Session is not initialized. Call 'init_session' first.")

        target_url = f"http://{config.target_host}{url_path}"
        try:
            async with self.session.request(
                method=method,
                url=target_url,
                headers=headers,
                data=body
            ) as proxy_resp:
                proxied_body = await proxy_resp.read()
                return web.Response(
                    status=proxy_resp.status,
                    headers={k: v for k, v in proxy_resp.headers.items() if k.lower() != "transfer-encoding"},
                    body=proxied_body
                )
        except aiohttp.ClientError as e:
            logger.error(f"Error while proxying request to {target_url}: {e}")
            return web.Response(status=502, text="Bad Gateway")

    async def close(self):
        """Закрывает сессию aiohttp.ClientSession."""
        if self.session:
            await self.session.close()

proxy_service = ProxyService()
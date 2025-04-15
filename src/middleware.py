from aiohttp import web
import aiohttp
import os

import aiohttp_jinja2

from src.logger import setup_logger
from src.config import config
from src.security.regular import detect_payloads
from src.security.utils import url_decode, red_detected_print, green_detected_print

logger = setup_logger()


async def handle_request(request: web.Request) -> web.Response:
    """Processes an incoming request and proxies it to the target server."""
    try:
        method, url_path, headers, body, client_ip = await extract_request_data(request)

        regular_check = detect_payloads(url_path)
        if regular_check:
            detected = await red_detected_print(" ".join(regular_check))
            logger.warning(f"{client_ip} - {method} |{detected}|{url_path} ")
            return web.HTTPFound(location="/error")
        
        if config.machine_sec:
            # Placeholder for machine learning security checks
            pass


        text = await green_detected_print("clean")
        log_request(client_ip, method, url_path, text)
        
        return await proxy_request(method, url_path, headers, body)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return web.Response(status=500, text="Internal Server Error")
    

async def error_handler(request: web.Request) -> web.Response:
    """Handles requests to /error and returns an HTML response."""
    client_ip = request.headers.get('X-Forwarded-For', request.remote)
    context = {
        "message": "request error", 
        "client_ip": client_ip
    }

    return aiohttp_jinja2.render_template("error.html", request, context)


async def extract_request_data(request: web.Request):
    """Extracts data from the incoming request."""
    method = request.method
    url_path = await url_decode(request.path_qs)
    headers = dict(request.headers)
    body = await request.read()
    client_ip = request.headers.get('X-Forwarded-For', request.remote)
    return method, url_path, headers, body, client_ip


def log_request(client_ip, method, url_path, regular_check):
    """Logs information about the request."""
    logger.info(f"{client_ip} - {method} |{regular_check}|{url_path} ")


async def proxy_request(method, url_path, headers, body):
    """Proxy the request to the target host."""
    target_url = f"http://{config.target_host}{url_path}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(
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
import os
import time
import aiohttp
import aiohttp_jinja2
from aiohttp import web

from src.logger import setup_logger
from src.config import config
from src.security.regular import detect_payloads
from src.security.utils import url_decode, red_detected_print, green_detected_print
from src.classifire.request import BaseRequest
from src.classifire import ThreatClassifire
from src.proxy import proxy_service
from src.security.rate_limit import RateClientBucket
from src.exceptions import firebox_exceptions


logger = setup_logger()


async def handle_request(request: web.Request) -> web.Response:
    """Processes an incoming request and proxies it to the target server."""
    try:
        method, url_path, headers, body, client_ip = await extract_request_data(request)
        
        request_data = BaseRequest(
            id_=os.urandom(16).hex(),
            timestamp=request.headers.get('Date', None),
            origin=client_ip,
            host=config.target_host,
            request=url_path,
            body=body.decode('utf-8', errors='ignore'),
            headers=headers,
            method=method,
        )
        current_time = int(time.time())

        if config.rate_limit:
            bucket = RateClientBucket()
            bucket.add_client(
                client_ip,
                current_time
            )
            bucket.removed_expired_client(
                ip_address=client_ip,
                ttl=int(config.rate_limit.split(":")[0]),
            )
            if len(bucket.client_bucket[client_ip]) >= int(config.rate_limit.split(":")[1]):
                return web.HTTPFound(location="/error?sc=66f8fb0d-517b-4e09-8d2f-ef04fcf47396")


        if config.signature_sec:
            regular_check = detect_payloads(url_path)
            if regular_check:
                detected = await red_detected_print(" ".join(regular_check))
                logger.warning(f"{client_ip} - {method} |SIG[{detected}]|{url_path} ")
                return web.HTTPFound(location="/error?sc=c737d556-b06b-4b7a-bf12-df5308a439db")
        
        if config.machine_sec:
            # Placeholder for machine learning security checks
            processed_request = ThreatClassifire().classify_request(request_data)
            detected = list(processed_request.threats.keys())

            if "valid" not in detected:
                detected = await red_detected_print(" ".join(detected))
                logger.warning(f"{client_ip} - {method} |ML[{detected}]|{url_path} ")
                return web.HTTPFound(location="/error?sc=c737d556-b06b-4b7a-bf12-df5308a439db")

        text = await green_detected_print("clean")
        log_request(client_ip, method, url_path, text)
        
        return await proxy_service.proxy_request(method, url_path, headers, body)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return web.Response(status=500, text="Internal Server Error")
    

async def error_handler(request: web.Request) -> web.Response:
    """Handles requests to /error and returns an HTML response."""
    client_ip = request.headers.get('X-Forwarded-For', request.remote)

    status_code = firebox_exceptions.get(
        request.query.get('sc', 'error'),
        firebox_exceptions.get('error')
    )
    detected = await red_detected_print("blocked")
    url = await url_decode(request.path_qs)
    logger.info(f"{client_ip} - {request.method} |{detected}| {url}")

    context = {
        "message": status_code["status"], 
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


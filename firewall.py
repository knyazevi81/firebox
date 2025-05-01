import argparse
from aiohttp import web
import aiohttp_jinja2
import jinja2


from src.config import config
from src.logger import setup_logger
from src.middleware import handle_request, error_handler
from src.proxy import proxy_service


def setup_argparse() -> argparse.ArgumentParser:
    """Configures and returns a command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Firewall management tool for monitoring and configuring rules"
    )

    parser.add_argument(
        "-p", "--port",
        type=int,
        default=8080,
        help="Port for reverse proxy"
    )

    parser.add_argument(
        "-tp", "--target-host",
        type=str,
        required=True,
        help="Target application port"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output for debugging"
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout for requests in seconds (default: 30)"
    )

    parser.add_argument(
        "-ml", "--machine-sec",
        action="store_true",
        default=False,
        help="Enable machine learning security (default: False)"
    )

    parser.add_argument(
        "-sg", "--signature-sec",
        action="store_true",
        default=False,
        help="Enable signature security (default: False)"
    )
    
    """
    Example of a rate limit argument
       --rate-limit 60:50 -> ttl:max_req_len
    """
    parser.add_argument(
        "-rt", "--rate-limit",
        type=str, 
        default=None,
        help="Enable ddos rate-limit security (default: False)\n Expl 60:50 -> ttl:max_req_len"
    )
    return parser

async def on_startup(app):
    """Инициализация сессии при старте приложения."""
    await proxy_service.init_session()

async def on_shutdown(app):
    """Закрытие сессии при завершении приложения."""
    await proxy_service.close()


def create_reverse_proxy_app() -> web.Application:
    """Creates and returns the reverse proxy application."""
    app = web.Application()

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("src/templates"))

    app.router.add_route("*", "/{tail:.*}", handle_request)
    app.router.add_route("GET", "/error", error_handler)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    app.router.add_static('/src/templates/static/', path='src/templates/static', name='static')
    return app


def main():
    parser = setup_argparse()
    args = parser.parse_args()

    config.port = args.port
    config.target_host = args.target_host
    config.verbose = args.verbose
    config.machine_sec = args.machine_sec
    config.signature_sec = args.signature_sec
    config.rate_limit = args.rate_limit
    #config.timeout = args.timeout

    logger = setup_logger()

    app = create_reverse_proxy_app()
    try:
        logger.info(f"Starting proxy server on port {config.port}")
        web.run_app(app, port=config.port)
    except Exception as e:
        logger.exception(f"Failed to start the server: {e}")


if __name__ == "__main__":
    main()
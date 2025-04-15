import argparse
from aiohttp import web
import aiohttp_jinja2
import jinja2


from src.config import config
from src.logger import setup_logger
from src.middleware import handle_request, error_handler


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
        type=bool,
        default=False,
        help="Enable machine learning security (default: False)"
    )

    return parser


def create_reverse_proxy_app() -> web.Application:
    """Creates and returns the reverse proxy application."""
    app = web.Application()

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("src/templates"))

    app.router.add_route("*", "/{tail:.*}", handle_request)
    app.router.add_route("GET", "/error", error_handler)

    app.router.add_static('/src/templates/static/', path='src/templates/static', name='static')
    return app


def main():
    parser = setup_argparse()
    args = parser.parse_args()

    config.port = args.port
    config.target_host = args.target_host
    config.verbose = args.verbose
    config.machine_sec = args.machine_sec

    logger = setup_logger()

    app = create_reverse_proxy_app()
    try:
        logger.info(f"Starting proxy server on port {config.port}")
        web.run_app(app, port=config.port)
    except Exception as e:
        logger.exception(f"Failed to start the server: {e}")


if __name__ == "__main__":
    main()
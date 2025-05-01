import re

from src.security.signature import waf_patterns
from src.logger import setup_logger

logger = setup_logger()

def detect_payloads(url_or_param: str):
    """
    Checks a string for malicious patterns.
    
    Args:
        url_or_param (str): URL or parameter to check.

    Returns:
        list: List of vulnerability types found in the line.
    """
    compiled_patterns = {
        vuln_type: [re.compile(pattern) for pattern in patterns]
        for vuln_type, patterns in waf_patterns.items()
    }
    
    if not isinstance(url_or_param, str):
        logger.error("Input must be a string")
        return []

    findings = []
    for vuln_type, patterns in compiled_patterns.items():
        if any(pattern.search(url_or_param) for pattern in patterns):
            findings.append(vuln_type)
    
    return findings
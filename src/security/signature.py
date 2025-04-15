import re

waf_patterns = {
    "xss": [
        r"(?i)<script.*?>.*?</script.*?>",
        r"(?i)on\w+\s*=\s*['\"][^'\"]+['\"]",  # onerror=, onload=
        r"(?i)javascript:",
        r"(?i)<.*?src\s*=\s*['\"]javascript:.*?['\"]",
        r"(?i)<iframe.*?>",
        r"(?i)<img.*?onerror\s*=.*?>",
        r"(?i)alert\s*\(",
        r"(?i)document\.cookie",
        r"(?i)document\.location",
        r"(?i)<svg.*?on\w+="
    ],
    "sqli": [
        r"(?i)(union.*select.*from)",
        r"(?i)(select.*from.*where)",
        r"(?i)(\bor\b\s+\d+=\d+)",
        r"(?i)(\band\b\s+\d+=\d+)",
        r"(?i)('.+--|--\s|#|\*/|\*/|/\*|%27|%23)",
        r"(?i)(sleep\()",
        r"(?i)(benchmark\()",
        r"(?i)(load_file\()",
        r"(?i)(into\s+outfile)"
    ],
    "lfi": [
        r"\.\./",                # ../ traversal
        r"/etc/passwd",
        r"boot.ini",
        r"windows/win.ini",
        r"/proc/self/environ",
        r"input=.*&?file="
    ],
    "rfi": [
        r"(http|https|ftp):\/\/[^'\"]+",
        r"(php:\/\/input|data:\/\/text|expect:\/\/)",
        r"((gopher|dict|file):\/\/)"
    ],
    "command_injection": [
        r"(;|\|\||&&)",             # command chaining
        r"(\bcat\b|\bwhoami\b|\bid\b|\buname\b)",
        r"(`.*?`)",
        r"\$\(.*?\)",
        r"\|\s*(nc|curl|wget|python|bash|sh)",
        r"(curl|wget)\s+[^\s]+"
    ],
    "ssti": [
        r"\{\{.*?\}\}",            # Jinja2, Twig
        r"<%.*?%>",                # JSP/ASP/ERB
        r"\$\{.*?\}",              # Spring EL
        r"#\{.*?\}",               # Ruby ERB
    ],
    "ssrf": [
        r"(http|https|ftp):\/\/(127\.0\.0\.1|localhost|0\.0\.0\.0|169\.254\.\d+\.\d+)",
        r"(internal-api|metadata\.google|169\.254\.169\.254)",
        r"(unix:\/\/)",
    ],
    "path_traversal": [
        r"\.\./",
        r"\.\.\\",
        r"%2e%2e%2f",      # Encoded ../
        r"%252e%252e%252f",
        r"([a-zA-Z]:\\)",
        r"/[a-zA-Z0-9_\-]+/(\.\./)+"
    ],
    "open_redirect": [
        r"(?:https?:)?//[^\s]+",
        r"(?:%2f%2f|%252f%252f)"
    ]
}

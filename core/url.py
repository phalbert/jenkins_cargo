from urllib.parse import urlparse, urlunparse


def sanitize_url(url):
    # Parse the URL
    parsed_url = urlparse(url)

    # Remove leading and trailing whitespaces from components
    sanitized_scheme = parsed_url.scheme.strip()
    sanitized_netloc = parsed_url.netloc.strip()
    sanitized_path = parsed_url.path.strip()
    sanitized_params = parsed_url.params.strip()
    sanitized_query = parsed_url.query.strip()
    sanitized_fragment = parsed_url.fragment.strip()

    # Reconstruct the sanitized URL
    sanitized_url = urlunparse((
        sanitized_scheme,
        sanitized_netloc,
        sanitized_path,
        sanitized_params,
        sanitized_query,
        sanitized_fragment
    ))

    return sanitized_url

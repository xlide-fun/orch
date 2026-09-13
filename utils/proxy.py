def parse_proxy(proxy_url: str) -> dict:
    if not proxy_url:
        return None
    return {"server": proxy_url}

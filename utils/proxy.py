from typing import Optional

def parse_proxy(proxy_url: Optional[str]) -> Optional[dict]:
    if not proxy_url:
        return None
    # Format: http://user:pass@host:port or socks5://...
    return {"server": proxy_url}

def get_proxy_for_platform(config: dict, platform: str) -> Optional[str]:
    proxies = config.get("proxies", {})
    return proxies.get(platform) or proxies.get("default")

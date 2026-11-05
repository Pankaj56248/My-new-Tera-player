import httpx
import asyncio
import re

# In sabhi player sites ke backend API endpoints ka pool
RESOLVER_POOL = [
    {
        "name": "TeraDownloader",
        "url": "https://teradownloader.com/api/get-info",
        "method": "POST",
        "payload_type": "json",
        "key": "url",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": "https://teradownloader.com/terabox-player-online"
        }
    },
    {
        "name": "LinkPlay",
        "url": "https://linkplay.in/api/resolve",
        "method": "POST",
        "payload_type": "json",
        "key": "link",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": "https://linkplay.in/"
        }
    },
    {
        "name": "FlowVideoPlayer",
        "url": "https://flowvideoplayer.com/api/video/stream",
        "method": "POST",
        "payload_type": "json",
        "key": "url",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": "https://flowvideoplayer.com/"
        }
    },
    {
        "name": "ITeraPlay-Com",
        "url": "https://iteraplay.com/api/get-stream",
        "method": "POST",
        "payload_type": "form",
        "key": "url",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": "https://iteraplay.com/"
        }
    },
    {
        "name": "ITeraPlay-In",
        "url": "https://iteraplay.in/api/get-stream",
        "method": "POST",
        "payload_type": "form",
        "key": "url",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": "https://iteraplay.in/"
        }
    }
]

async def resolve_terabox_link(target_url: str) -> dict:
    """
    Diye gaye 5 player platforms par baari-baari check karta hai.
    """
    async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
        for source in RESOLVER_POOL:
            name = source["name"]
            api_url = source["url"]
            key = source["key"]
            headers = source.get("headers", {})

            try:
                if source["payload_type"] == "json":
                    res = await client.post(api_url, json={key: target_url}, headers=headers)
                else:
                    res = await client.post(api_url, data={key: target_url}, headers=headers)

                if res.status_code == 200:
                    data = res.json()

                    # Alag-alag platforms se common stream URL keys nikalna
                    stream_url = (
                        data.get("stream_url") or 
                        data.get("stream") or 
                        data.get("direct_link") or 
                        data.get("download_link") or 
                        data.get("url") or 
                        (data.get("data", {}).get("stream_url") if isinstance(data.get("data"), dict) else None) or
                        (data.get("list", [{}])[0].get("dlink") if isinstance(data.get("list"), list) and len(data.get("list")) > 0 else None)
                    )

                    if stream_url:
                        return {
                            "success": True,
                            "stream_url": stream_url,
                            "title": data.get("title") or data.get("file_name") or "TeraBox Stream",
                            "resolver_name": name
                        }
            except Exception:
                # Timeout ya error aane par agli site par switch karein
                continue

    return {"success": False, "error": "Saare 5 resolvers fail ho gaye."}
              

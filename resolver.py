import httpx
import asyncio
import json

# Desktop Browser ke authentic headers taaki websites block na karein
COMMON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://iteraplay.com",
    "Referer": "https://iteraplay.com/"
}

RESOLVER_POOL = [
    {
        "name": "ITeraPlay-Com",
        "url": "https://iteraplay.com/api/get-stream",
        "method": "POST",
        "type": "json",
        "payload": lambda url: {"url": url},
        "headers": {**COMMON_HEADERS, "Referer": "https://iteraplay.com/"}
    },
    {
        "name": "ITeraPlay-In",
        "url": "https://iteraplay.in/api/get-stream",
        "method": "POST",
        "type": "json",
        "payload": lambda url: {"url": url},
        "headers": {**COMMON_HEADERS, "Referer": "https://iteraplay.in/"}
    },
    {
        "name": "TeraDownloader",
        "url": "https://teradownloader.com/api/get-info",
        "method": "POST",
        "type": "json",
        "payload": lambda url: {"url": url},
        "headers": {**COMMON_HEADERS, "Referer": "https://teradownloader.com/terabox-player-online"}
    },
    {
        "name": "LinkPlay",
        "url": "https://linkplay.in/api/resolve",
        "method": "POST",
        "type": "json",
        "payload": lambda url: {"link": url},
        "headers": {**COMMON_HEADERS, "Referer": "https://linkplay.in/"}
    },
    {
        "name": "FlowVideo",
        "url": "https://flowvideoplayer.com/api/video/stream",
        "method": "POST",
        "type": "json",
        "payload": lambda url: {"url": url},
        "headers": {**COMMON_HEADERS, "Referer": "https://flowvideoplayer.com/"}
    }
]

async def resolve_terabox_link(target_url: str) -> dict:
    print(f"\n--- [RESOLVER START] URL: {target_url} ---", flush=True)

    # 10 second timeout per resolver
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        for source in RESOLVER_POOL:
            name = source["name"]
            api_url = source["url"]
            headers = source["headers"]
            payload = source["payload"](target_url)

            print(f"Testing {name} -> Sending request...", flush=True)

            try:
                if source["type"] == "json":
                    res = await client.post(api_url, json=payload, headers=headers)
                else:
                    res = await client.post(api_url, data=payload, headers=headers)

                print(f"[{name}] Status Code: {res.status_code}", flush=True)

                if res.status_code == 200:
                    try:
                        data = res.json()
                        print(f"[{name}] Response: {str(data)[:200]}...", flush=True)

                        # Different keys search
                        stream_url = (
                            data.get("stream_url") or 
                            data.get("stream") or 
                            data.get("direct_link") or 
                            data.get("download_link") or 
                            data.get("url") or 
                            (data.get("data", {}).get("stream_url") if isinstance(data.get("data"), dict) else None) or
                            (data.get("data", {}).get("url") if isinstance(data.get("data"), dict) else None) or
                            (data.get("list", [{}])[0].get("dlink") if isinstance(data.get("list"), list) and len(data.get("list")) > 0 else None)
                        )

                        if stream_url:
                            print(f"✅ [{name}] Success! Stream link extracted.", flush=True)
                            return {
                                "success": True,
                                "stream_url": stream_url,
                                "title": data.get("title") or data.get("file_name") or "TeraBox Stream",
                                "resolver_name": name
                            }
                        else:
                            print(f"⚠️ [{name}] 200 OK aaya lekin stream URL key nahi mili.", flush=True)
                    except Exception as json_err:
                        print(f"⚠️ [{name}] Response JSON parse nahi hua: {json_err}", flush=True)
                else:
                    print(f"❌ [{name}] Failed with status: {res.status_code} | Text: {res.text[:150]}", flush=True)

            except httpx.TimeoutException:
                print(f"⏳ [{name}] Request Timeout ho gayi (10s).", flush=True)
            except Exception as e:
                print(f"❌ [{name}] Error: {str(e)}", flush=True)

    print("--- [RESOLVER END] All failed ---\n", flush=True)
    return {"success": False, "error": "Saare 5 resolvers ne request reject/timeout kar di."}
    

import httpx
import asyncio
import re

# Cloudflare bypass aur working open-source TeraBox instances
RESOLVER_POOL = [
    {
        "name": "TeraDL-Fast",
        "url": "https://teradl-api.dapuntaratya.com/generate",
        "method": "POST",
        "type": "json",
        "payload": lambda url: {"url": url}
    },
    {
        "name": "TeraBox-Worker-API",
        "url": "https://terabox.hnn.workers.dev/api/get-info",
        "method": "GET",
        "type": "query",
        "param_key": "url"
    },
    {
        "name": "TeraDownloader-Public",
        "url": "https://yt-video-production.up.railway.app/terabox",
        "method": "GET",
        "type": "query",
        "param_key": "url"
    },
    {
        "name": "Open-TeraBox-API",
        "url": "https://terabox-api.ashlynn.workers.dev/",
        "method": "GET",
        "type": "query",
        "param_key": "url"
    }
]

async def resolve_terabox_link(target_url: str) -> dict:
    print(f"\n--- [RESOLVER START] Target URL: {target_url} ---", flush=True)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }

    async with httpx.AsyncClient(timeout=12.0, follow_redirects=True, headers=headers) as client:
        for source in RESOLVER_POOL:
            name = source["name"]
            api_url = source["url"]
            print(f"Testing {name}...", flush=True)

            try:
                if source["method"] == "GET":
                    res = await client.get(api_url, params={source["param_key"]: target_url})
                else:
                    payload = source["payload"](target_url)
                    res = await client.post(api_url, json=payload)

                print(f"[{name}] HTTP Status: {res.status_code}", flush=True)

                if res.status_code == 200:
                    try:
                        data = res.json()
                        print(f"[{name}] Response JSON snippet: {str(data)[:250]}", flush=True)

                        # Multiple response formats se link dhoondhna
                        stream_url = None

                        # Pattern 1: Direct key
                        for k in ["stream_url", "direct_link", "download_link", "url", "fast_download_link"]:
                            if data.get(k):
                                stream_url = data[k]
                                break

                        # Pattern 2: Nested data dict
                        if not stream_url and isinstance(data.get("data"), dict):
                            stream_url = data["data"].get("stream_url") or data["data"].get("url") or data["data"].get("download_link")

                        # Pattern 3: Nested list (Array of files)
                        if not stream_url:
                            file_list = data.get("list") or (data.get("data") if isinstance(data.get("data"), list) else None)
                            if isinstance(file_list, list) and len(file_list) > 0:
                                first_item = file_list[0]
                                stream_url = (
                                    first_item.get("stream_url") or 
                                    first_item.get("dlink") or 
                                    first_item.get("direct_link") or 
                                    first_item.get("url")
                                )

                        if stream_url:
                            title = data.get("title") or (data.get("data", {}).get("title") if isinstance(data.get("data"), dict) else None) or "TeraBox Video"
                            print(f"✅ [{name}] SUCCESS! Extracted stream URL.", flush=True)
                            return {
                                "success": True,
                                "stream_url": stream_url,
                                "title": title,
                                "resolver_name": name
                            }
                        else:
                            print(f"⚠️ [{name}] 200 mila par stream key extract nahi hui.", flush=True)
                    except Exception as parse_err:
                        print(f"⚠️ [{name}] JSON parse failed: {parse_err}", flush=True)
                else:
                    print(f"❌ [{name}] Response code: {res.status_code}", flush=True)

            except httpx.TimeoutException:
                print(f"⏳ [{name}] Timeout (12s).", flush=True)
            except Exception as e:
                print(f"❌ [{name}] Error: {str(e)}", flush=True)

    print("--- [RESOLVER END] All failed ---\n", flush=True)
    return {"success": False, "error": "Saare working resolvers fail ho gaye ya block ho gaye."}
    

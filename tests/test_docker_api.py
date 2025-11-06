import asyncio
import json

from deploy.docker.api import handle_crawl_request
from deploy.docker.utils import load_config

config = load_config()

payload = {
    "urls": ["https://assets.avm.de/files/docs/fritzbox/fritzbox-7690/fritzbox-7690_qig_en.pdf"],
    #"urls": ["https://www.divino-wein.de/weine/franconia-riesling/3346-231"],
    "browser_config": {
        "type": "BrowserConfig",
        "params": {"headless": True}
    },
    "crawler_config": {
        "type": "CrawlerRunConfig",
        "params": {"cache_mode": "bypass"}
    }
}

async def test_crawl_pdf_job():
    result = await handle_crawl_request(
        urls=payload["urls"],
        browser_config=payload["browser_config"],
        crawler_config=payload["crawler_config"],
        config=config,
    )
    json_result = json.dumps(result)


if __name__ == "__main__":
    asyncio.run(test_crawl_pdf_job())

    print("\nTests completed!")
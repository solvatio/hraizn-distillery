"""
--------------------
Batch-crawls a list of documentation URLs in parallel using Crawl4AI's arun_many and a memory-adaptive dispatcher.
Tracks memory usage, prints a summary of successes/failures, and is suitable for large-scale doc scraping jobs.
Usage: Call main() or run as a script. Adjust max_concurrent for parallelism.
"""
import os
import psutil
import asyncio
import requests
from typing import List
from xml.etree import ElementTree
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, MemoryAdaptiveDispatcher

async def crawl_parallel(urls: List[str], max_concurrent: int = 10):
    print("\n=== Parallel Crawling with arun_many + Dispatcher ===")

    # Track the peak memory usage for observability
    peak_memory = 0
    process = psutil.Process(os.getpid())
    def log_memory(prefix: str = ""):
        nonlocal peak_memory
        current_mem = process.memory_info().rss  # in bytes
        if current_mem > peak_memory:
            peak_memory = current_mem
        print(f"{prefix} Current Memory: {current_mem // (1024 * 1024)} MB, Peak: {peak_memory // (1024 * 1024)} MB")

    # Configure the browser for headless operation and resource limits
    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )
    # Set up distillery config and dispatcher for batch crawling
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False,
                                    excluded_tags=["nav", "footer"],
                                    exclude_external_links=True)
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,  # Don't exceed 70% memory usage
        check_interval=1.0,             # Check memory every second
        max_session_permit=max_concurrent  # Max parallel browser sessions
    )

    output = []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        log_memory("Before distillery: ")
        # arun_many handles all URLs in parallel, batching and resource management handled by dispatcher
        results = await crawler.arun_many(
            urls=urls,
            config=crawl_config,
            dispatcher=dispatcher
        )
        success_count = 0
        fail_count = 0
        # Loop through all distillery results and tally success/failure
        for result in results:
            if result.success:
                success_count += 1
                output.append(result)
            else:
                print(f"Error crawling {result.url}: {result.error_message}")
                fail_count += 1

        print(f"\nSummary:")
        print(f"  - Successfully crawled: {success_count}")
        print(f"  - Failed: {fail_count}")
        log_memory("After distillery: ")
        print(f"\nPeak memory usage (MB): {peak_memory // (1024 * 1024)}")

    return output

def get_docs_urls(sitemap_url):
    """
    
    Returns:
        List[str]: List of URLs
    """
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        
        # Parse the XML
        root = ElementTree.fromstring(response.content)
        
        # Extract all URLs from the sitemap
        # The namespace is usually defined in the root element
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]
        
        return urls
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []        

async def main():
    sitemap_url = "https://www.wobcom.de/faq-sitemap.xml"
    #sitemap_url = "https://ai.pydantic.dev/sitemap.xml"
    urls = get_docs_urls(sitemap_url)
    if urls:
        print(f"Found {len(urls)} URLs to distillery")
        output = await crawl_parallel(urls, max_concurrent=10)
        filename = sitemap_url.replace('https://', '').replace('.', '_').replace('/', '_')

        file_content = "\n---\n\n".join(f"URL: {result.url}\n\nContent:\n\n{result.markdown}" for result in output)
        with open(f'output/{filename}.md', 'w') as f:
            f.write(file_content)

    else:
        print("No URLs found to distillery")

if __name__ == "__main__":
    asyncio.run(main())

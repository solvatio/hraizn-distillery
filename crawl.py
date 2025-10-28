import asyncio
from pathlib import Path

from distillery.parallel import get_docs_urls, crawl_parallel
from distillery.recursive import crawl_recursive_batch, crawl_recursive


async def crawl(url, depth):
    urls = []
    #if url.endswith(".xml"):
    #    urls = get_docs_urls(url)
    if urls:
        print(f"Found {len(urls)} URLs to crawl")
        output = await crawl_parallel(urls, max_concurrent=10)
    else:
        print("No sitemap URLs found to crawl")
        print(f"Crawling recursively with depth {depth}")
        output = await crawl_recursive(url, max_depth=depth, max_concurrent=10)

    filename = url.replace('https://', '').replace('.', '_').replace('/', '_')

    await write_markdown_file(output, filename)


async def write_markdown_file(crawl_results, filename):

    file_content = "\n---\n\n".join(f"URL: {result.url}\n\nContent:\n\n{result.markdown}" for result in crawl_results)

    Path("output").mkdir(parents=True, exist_ok=True)
    with open(f"output/{filename}.md", "w") as f:
        f.write(file_content)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Crawls URLs and writes markdown files.')

    parser.add_argument('-d', '--depth', default=3, help='Max depth for recursive crawling (default 3)')
    parser.add_argument('-u', '--urls', nargs='+', default=[], help='List of website or sitemap URLs to crawl')

    args = parser.parse_args()

    #sitemap_url = "https://ai.pydantic.dev/sitemap.xml"
    #sitemap_url = "https://www.wobcom.de/faq-sitemap.xml"
    for url_ in args.urls:
        print(f"Crawling {url_}")
        asyncio.run(crawl(url_, int(args.depth)))
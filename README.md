# hraizn-distillery

Based on https://github.com/unclecode/crawl4ai

## Quick Start 
1. Create and activate python env:
```bash
# Create python env
python3 -m venv .venv

# Activate python env
source .venv/bin/activate
```
2. Install Crawl4AI:
```bash
# Install the package
pip install -U crawl4ai

# Run post-installation setup
crawl4ai-setup
```

## Crawl URLs
Crawl URLs and write results to output Folder:
```bash
# Activate python env (if not already activated)
source .venv/bin/activate

# Crawl list of website and sitemap urls
python crawl.py -d 1 -u https://solvatio.ai https://solvatio.ai/page-sitemap.xml
```

```
usage: crawl.py [-h] [-d DEPTH] [-u URLS [URLS ...]]

Crawls URLs and writes markdown files.

options:
  -h, --help            show this help message and exit
  -d DEPTH, --depth DEPTH
                        Max depth for recursive crawling (default 3).
  -u URLS [URLS ...], --urls URLS [URLS ...]
                        List of website or sitemap URLs to crawl.
```

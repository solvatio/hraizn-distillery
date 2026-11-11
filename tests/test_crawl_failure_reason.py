"""Failure classification tests without a browser or optional crawler dependencies."""
import importlib.util
from pathlib import Path
import unittest


spec = importlib.util.spec_from_file_location(
    "antibot_detector", Path(__file__).parents[1] / "crawl4ai" / "antibot_detector.py"
)
detector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(detector)


class CrawlFailureReasonTests(unittest.TestCase):
    def test_cloudflare_challenge_after_redirect_has_a_reason(self):
        html = '<html><head><title>Just a moment...</title></head><body>Checking your browser</body></html>'
        reason = detector.crawl_failure_reason(301, html, 'Checking your browser')
        self.assertIn('Crawl blocked:', reason)
        self.assertIn('Cloudflare', reason)

    def test_challenge_in_cached_content_is_still_a_failure(self):
        html = '<html><head><title>Just a moment...</title></head><body>Waiting</body></html>'
        self.assertIn('Crawl blocked:', detector.crawl_failure_reason(200, html))

    def test_empty_content_has_a_reason(self):
        self.assertEqual(detector.crawl_failure_reason(200, ''), 'Crawl returned no HTML content')

    def test_legitimate_markdown_is_not_replaced_with_a_fixed_sample(self):
        text = 'A real status report with enough useful text to be returned successfully.'
        html = f'<html><body><article><h1>Status</h1><p>{text}</p></article></body></html>'
        self.assertEqual(detector.crawl_failure_reason(200, html, text), '')

    def test_markdown_object_is_supported(self):
        class Markdown:
            def __str__(self):
                return 'A real status report with enough useful text to be returned successfully.'
        html = '<html><body><article><h1>Status</h1><p>A real status report with enough useful text to be returned successfully.</p></article></body></html>'
        self.assertEqual(detector.crawl_failure_reason(200, html, Markdown()), '')

    def test_link_only_text_does_not_count_as_useful_content(self):
        html = '<html><body><article><h1>Status</h1><p>A real status report with enough useful text to be returned successfully.</p></article></body></html>'
        self.assertEqual(
            detector.crawl_failure_reason(200, html, 'https://example.com/very-long-path-without-any-status-data'),
            'Crawl returned insufficient text content',
        )


if __name__ == '__main__':
    unittest.main()

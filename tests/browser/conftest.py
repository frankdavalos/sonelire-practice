"""Shared fixtures for the browser scenarios.

Pages load from the working tree at their published URL; nothing contacts a host.
Each test gets fresh devices (browser contexts), so localStorage never leaks
between scenarios. A page error anywhere fails the test that caused it.

SONELIRE_COVERAGE=1 also reports how much of each page's inline script ran.
"""
import os
from pathlib import Path
from urllib.parse import urlsplit
import pytest
from playwright.sync_api import sync_playwright
from steps import MAIN, SITE

ROOT = Path(__file__).resolve().parents[2]
COVERAGE = os.getenv('SONELIRE_COVERAGE') == '1'
covered = {}  # page file -> (script length, set of offsets that ran)


def serve(route):
    """Fulfil requests under the published site from the working tree; abort everything else (e.g. web fonts)."""
    url = route.request.url
    f = ROOT / urlsplit(url).path.removeprefix(urlsplit(SITE).path)
    if url.startswith(SITE) and f.is_file():
        route.fulfill(path=f)
    else:
        route.abort()


class Device:
    """One device: its own browser context, so its own localStorage."""

    def __init__(self, browser, viewport, errors, **options):
        self.context = browser.new_context(viewport=viewport, **options)
        self.context.route('**/*', serve)
        self.errors = errors
        self.profilers = {}  # page -> CDP session collecting its coverage

    def open(self, url=MAIN):
        page = self.context.new_page()
        page.on('pageerror', lambda e: self.errors.append(str(e)))
        if COVERAGE:
            cdp = self.context.new_cdp_session(page)
            cdp.send('Profiler.enable')
            cdp.send('Profiler.startPreciseCoverage', {'callCount': True, 'detailed': True})
            self.profilers[page] = cdp
        page.goto(url)
        return page

    def close_page(self, page):
        """Close one page mid-scenario, keeping its coverage."""
        self._record(page)
        page.close()

    def close(self):
        for page in list(self.profilers):
            self._record(page)
        self.context.close()

    def _record(self, page):
        cdp = self.profilers.pop(page, None)
        if cdp:
            record_coverage(cdp.send('Profiler.takePreciseCoverage')['result'])


def record_coverage(scripts):
    """Union the bytes of each page's inline script that ran with a non-zero count."""
    for script in scripts:
        name = urlsplit(script['url']).path.rsplit('/', 1)[-1]
        if not name.endswith('.html'):
            continue
        ranges = [r for f in script['functions'] for r in f['ranges']]
        length = max(r['endOffset'] for r in ranges)
        ran = [False] * length
        for r in sorted(ranges, key=lambda r: (r['startOffset'], -r['endOffset'])):
            ran[r['startOffset']:r['endOffset']] = [r['count'] > 0] * (r['endOffset'] - r['startOffset'])
        old_length, offsets = covered.setdefault(name, (length, set()))
        assert old_length == length, f'{name}: inline script changed length during the run'
        offsets.update(i for i, x in enumerate(ran) if x)


def pytest_terminal_summary(terminalreporter):
    for name, (length, offsets) in sorted(covered.items()):
        terminalreporter.write_line(f'inline script coverage {name}: {100 * len(offsets) / length:.1f}% of {length} bytes')


@pytest.fixture(scope='session')
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.getenv('CHROMIUM', '/usr/bin/chromium'), args=['--no-sandbox'])
        yield b
        b.close()


@pytest.fixture
def page_errors():
    errors = []
    yield errors
    assert not errors, errors


@pytest.fixture
def device(browser, page_errors):
    """Factory for extra devices: device(width, height, **context options)."""
    made = []

    def make(width, height, **options):
        d = Device(browser, {'width': width, 'height': height}, page_errors, **options)
        made.append(d)
        return d
    yield make
    for d in made:
        d.close()


@pytest.fixture
def ipad(device):
    return device(1366, 1024)


@pytest.fixture
def phone(device):
    return device(390, 844)


@pytest.fixture
def page(ipad):
    """The main page, freshly loaded on the iPad."""
    return ipad.open()

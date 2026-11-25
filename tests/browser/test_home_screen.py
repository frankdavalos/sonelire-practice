"""Home Screen install: the web app manifest, icons and head tags, no service worker, and persistent storage (docs/adr/0003)."""
from steps import MAIN, SITE, text

COUNT_PERSIST = 'navigator.storage.persist = () => { window.persistCalls = (window.persistCalls || 0) + 1; return Promise.resolve(true) }'
NO_STORAGE_MANAGER = "Object.defineProperty(navigator, 'storage', {value: undefined})"


def image_size(page, url):
    return page.evaluate('''url => new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve([img.naturalWidth, img.naturalHeight]);
      img.onerror = () => reject(new Error('icon did not load: ' + url));
      img.src = url;
    })''', url)


def meta(page, name):
    return page.get_attribute(f'meta[name="{name}"]', 'content')


def test_main_page_links_a_standalone_manifest_that_starts_at_the_main_page(page):
    url, manifest = page.evaluate('''async () => {
      const response = await fetch(document.querySelector('link[rel=manifest]').href);
      return [response.url, await response.json()];
    }''')
    resolve = lambda relative: page.evaluate('([r, base]) => new URL(r, base).href', [relative, url])
    assert manifest['name'] == 'Sonelire Practice'
    assert manifest['display'] == 'standalone'
    assert resolve(manifest['start_url']) == MAIN
    assert resolve(manifest['scope']) == SITE
    sizes = {icon['sizes']: image_size(page, resolve(icon['src'])) for icon in manifest['icons']}
    assert sizes == {'192x192': [192, 192], '512x512': [512, 512]}


def test_main_page_has_a_180px_apple_touch_icon_and_opens_full_screen_on_ios(page):
    icon = page.evaluate('document.querySelector("link[rel=apple-touch-icon]").href')
    assert image_size(page, icon) == [180, 180]
    assert meta(page, 'apple-mobile-web-app-capable') == 'yes'
    assert meta(page, 'apple-mobile-web-app-title') == 'Sonelire'
    assert meta(page, 'apple-mobile-web-app-status-bar-style') == 'default'


def test_main_page_registers_no_service_worker(page):
    page.wait_for_load_state('load')
    assert page.evaluate('navigator.serviceWorker.getRegistrations().then(r => r.length)') == 0


def test_every_page_open_asks_the_browser_once_to_keep_its_data(ipad):
    ipad.context.add_init_script(COUNT_PERSIST)
    page = ipad.open()
    assert page.evaluate('window.persistCalls') == 1
    page.reload()
    assert page.evaluate('window.persistCalls') == 1


def test_page_loads_without_error_where_the_browser_cannot_keep_data(ipad):
    ipad.context.add_init_script(NO_STORAGE_MANAGER)
    console_errors = []
    ipad.context.on('console', lambda m: m.type == 'error' and console_errors.append(m.text))
    page = ipad.open()
    page.click('#next')
    assert text(page, '#counter') == '2 / 26'
    assert all(e.startswith('Failed to load resource') for e in console_errors), 'only the aborted web font fails'

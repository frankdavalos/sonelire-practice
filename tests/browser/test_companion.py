"""Companion: the phone's private scoring sheet for one Form."""
from playwright.sync_api import expect
from steps import COMPANION, UPPER, accept_next_dialog, pressed, text

FORM = 'SON1A.F1.name.upper.' + UPPER
LINK = COMPANION + '#form=' + FORM


def test_previous_next_and_jumping_move_between_items(phone):
    page = phone.open(LINK)
    assert text(page, '#position') == 'Item 1 of 26'
    assert page.locator('#prev').is_disabled()
    page.click('#next')
    assert (text(page, '#position'), text(page, '#letter')) == ('Item 2 of 26', 'B')
    page.click('#prev')
    assert text(page, '#letter') == 'A'
    page.click('#overview button[aria-label^="Item 26,"]')
    assert (text(page, '#position'), text(page, '#letter')) == ('Item 26 of 26', 'Z')
    assert page.locator('#next').is_disabled()


def test_undo_reverses_the_last_change_and_returns_to_its_item(phone):
    page = phone.open(LINK)
    assert page.locator('#undo').is_disabled()
    page.click('[data-score=incorrect]')
    assert (text(page, '#letter'), text(page, '#progress')) == ('B', '1 marked'), 'marking advances'
    page.click('#undo')
    assert (text(page, '#letter'), text(page, '#progress')) == ('A', '0 marked')
    assert text(page, '#current') == 'Not marked'
    assert page.locator('#undo').is_disabled()


def test_clear_this_mark_unmarks_the_current_item_and_hides_a_prepared_transfer(phone):
    page = phone.open(LINK)
    page.click('[data-score=correct]')
    page.click('#prev')
    page.click('#transfer')
    assert page.locator('#output').is_visible()
    page.click('#clear')
    assert text(page, '#current') == 'Not marked'
    assert not page.locator('#output').is_visible(), 'the prepared code no longer matches the marks'
    assert page.locator('#clear').is_disabled()
    assert page.locator('#transfer').is_disabled()


def test_clear_this_companion_session_forgets_every_mark_on_this_phone(phone):
    page = phone.open(LINK)
    page.click('[data-score=correct]')
    page.click('#reset')  # unanswered confirm is dismissed: nothing changes
    assert text(page, '#progress') == '1 marked'
    accept_next_dialog(page)
    page.click('#reset')
    assert (text(page, '#progress'), text(page, '#position')) == ('0 marked', 'Item 1 of 26')
    page.reload()
    assert text(page, '#progress') == '0 marked'


def test_an_invalid_link_shows_an_error_instead_of_the_sheet(phone):
    page = phone.open(COMPANION + '#form=SON1A.F1.name.upper.ABC')
    assert page.locator('#error').is_visible()
    assert text(page, '#error') == 'Invalid assessment form. Open a new companion QR from the iPad.'
    assert not page.locator('#app').is_visible()


def test_copy_puts_the_results_code_on_the_clipboard(device):
    phone = device(390, 844, permissions=['clipboard-read', 'clipboard-write'])
    page = phone.open(LINK)
    page.click('[data-score=correct]')
    page.click('#transfer')
    page.click('#copy')
    expect(page.locator('#copyStatus')).to_contain_text('Copied on this device')
    assert page.evaluate('navigator.clipboard.readText()') == page.locator('#code').input_value()


def test_copy_without_clipboard_access_selects_the_code_for_manual_copying(phone):
    page = phone.open(LINK)
    page.click('[data-score=correct]')
    page.click('#transfer')
    page.evaluate("() => { navigator.clipboard.writeText = () => Promise.reject(new Error('denied')) }")
    page.click('#copy')
    expect(page.locator('#copyStatus')).to_have_text('Select and copy the code manually.')
    assert page.evaluate('document.activeElement.id') == 'code'


def test_save_code_file_downloads_the_results_code(phone):
    page = phone.open(LINK)
    page.click('[data-score=incorrect]')
    page.click('#transfer')
    with page.expect_download() as download:
        page.click('#download')
    assert download.value.suggested_filename == 'sonelire-results-F1.txt'
    assert open(download.value.path()).read() == 'SON1R.F1.name.upper.' + UPPER + '.I' + '-' * 25


def test_v1_record_with_miss_marks_restores(phone):
    page = phone.open(LINK)
    page.evaluate('([k, v]) => localStorage.setItem(k, JSON.stringify(v))',
                  ['sonelire-companion-v1:' + FORM, {'scores': {'0': 'miss', '2': 'unsure'}, 'index': 1}])
    page.reload()
    assert (text(page, '#position'), text(page, '#progress')) == ('Item 2 of 26', '2 marked')
    assert page.locator('#overview button[aria-label^="Item 1,"]').get_attribute('aria-label') == 'Item 1, A, Incorrect'
    page.click('#prev')
    assert pressed(page, '[data-score=incorrect]')

"""The two-device Companion round trip, end to end: iPad presents, phone marks, QR link brings the Marks back."""
import io
from steps import FILE_SHARING, accept_next_dialog, prepare, stat, text

try:
    from PIL import Image
    from pyzbar.pyzbar import decode
except ImportError:  # optional: pyzbar needs the system zbar library
    decode = None


def qr_text(locator):
    return decode(Image.open(io.BytesIO(locator.screenshot())))[0].data.decode()


def test_companion_round_trip(ipad, phone):
    a = ipad.open()
    a.click('#tabAssess')
    a.click('#assessCase [data-value=mixed]')
    a.click('#prepare')
    a.click('#showCompanion')
    url = a.locator('#companionLink').get_attribute('href')
    assert a.locator('#companionQR svg').count() == 1
    if decode:
        assert qr_text(a.locator('#companionQR svg')) == url

    b = phone.open(url)
    a.click('#begin')
    assert not a.locator('#scoring').is_visible()
    assert not a.locator('#showCompanion').is_visible()
    for i in range(52):
        assert text(a, '#stimulusLetter') == text(b, '#letter')
        b.click('[data-score=incorrect]' if i == 1 else '[data-score=correct]')
        a.keyboard.press('ArrowRight')
    assert a.locator('#scoring').is_visible()

    b = phone.open(url)  # the phone reloads the page: its Companion record survives
    assert text(b, '#progress') == '52 marked'
    b.click('#transfer')
    code = b.locator('#code').input_value()
    assert b.locator('#resultQR svg').count() == 1
    link = b.evaluate('CompanionProtocol.resultUrl(document.getElementById("code").value, location.href)')
    if decode:
        assert qr_text(b.locator('#resultQR svg')) == link

    ipad.close_page(a)  # c shares a's localStorage; an open a would reload on c's writes
    c = ipad.open(link)
    assert c.locator('#importCode').input_value() == code
    c.click('#importButton')
    assert text(c, '#scoredCount') == '52 / 52 marked'
    assert c.locator('#scoreList [data-index="1"] [data-value=incorrect]').get_attribute('aria-pressed') == 'true'
    c.click('#saveScores')
    assert c.locator('#results').is_visible()
    assert '1 needs practice' in text(c, '#glanceCounts')
    c.click('#practiceWeak')
    assert text(c, '#counter') == '1 / 1'

    # Learner 2 on paper: a code from another Form is refused, then a manual Mark is saved.
    c.select_option('#learner', '2')
    c.click('#tabAssess')
    c.click('#prepare')
    c.click('#begin')
    c.click('#pause')
    accept_next_dialog(c)
    c.click('#finishEarly')
    c.locator('#importPanel summary').click()
    c.fill('#importCode', code)
    c.click('#importButton')
    assert 'different assessment' in text(c, '#importMessage')
    assert text(c, '#scoredCount') == '0 / 1 marked'
    c.click('#scoreList [data-index="0"] [data-value=correct]')
    c.click('#saveScores')
    assert stat(c, 'Correct') == 1
    c.select_option('#learner', '1')
    c.click('#resultCase [data-value=mixed]')
    assert stat(c, 'Correct') == 51, 'Learners keep separate Results'


def test_shared_results_file_imports_on_the_ipad_with_the_marks_the_qr_carries(ipad, phone):
    a = ipad.open()
    prepare(a)
    a.click('#showCompanion')
    phone.context.add_init_script(FILE_SHARING)
    b = phone.open(a.locator('#companionLink').get_attribute('href'))
    for score in ('correct', 'incorrect', 'unsure', 'skip'):
        b.click(f'[data-score={score}]')
    b.click('#transfer')
    b.click('#share')
    shared = b.wait_for_function('window.shared').json_value()[0]
    assert shared['text'] == b.locator('#code').input_value(), 'the QR link carries this same Results code'

    a.click('#begin')
    for _ in range(3):
        a.keyboard.press('ArrowRight')
    a.click('#pause')
    accept_next_dialog(a)
    a.click('#finishEarly')
    a.locator('#importPanel summary').click()
    a.set_input_files('#importFile', files=[{'name': shared['name'], 'mimeType': shared['type'], 'buffer': shared['text'].encode()}])
    a.click('#importButton')
    assert text(a, '#scoredCount') == '4 / 4 marked'
    assert a.eval_on_selector_all('#scoreList [aria-pressed=true]', 'bs => bs.map(b => b.dataset.value)') == ['correct', 'incorrect', 'unsure', 'skip']

"""Assess tab: setting up a Check and its Presentation."""
from steps import UPPER, prepare, pressed, swipe, text


def test_letter_sounds_prepares_a_sounds_check(page):
    page.click('#tabAssess')
    page.click('#assessSkill [data-value=sound]')
    assert 'familiar sound' in text(page, '#protocol')
    page.click('#prepare')
    assert text(page, '#preparedTitle') == 'Uppercase · Letter sounds'


def test_alphabetical_order_presents_letters_a_to_z(page):
    prepare(page, order='alpha')
    assert text(page, '#orderPreview').replace(' ', '').split('·') == list(UPPER)
    page.click('#begin')
    assert text(page, '#stimulusLetter') == 'A'


def test_check_again_from_results_sets_up_the_same_skill_and_case(page):
    page.click('#tabResults')
    page.click('#resultCase [data-value=lower]')
    page.click('#resultSkill [data-value=sound]')
    page.click('#assessAgain')
    assert page.locator('#setup').is_visible()
    assert pressed(page, '#assessCase [data-value=lower]')
    assert pressed(page, '#assessSkill [data-value=sound]')


def test_presentation_advances_and_goes_back_by_key_tap_and_swipe(page):
    prepare(page)
    page.click('#begin')
    page.click('#present', position={'x': 100, 'y': 300})
    assert text(page, '#stimulusLetter') == 'B'
    page.keyboard.press('Space')
    assert text(page, '#stimulusLetter') == 'C'
    page.keyboard.press('ArrowLeft')
    assert text(page, '#stimulusLetter') == 'B'
    swipe(page, '#present', 150)
    assert text(page, '#stimulusLetter') == 'A'
    page.keyboard.press('ArrowLeft')
    assert text(page, '#stimulusLetter') == 'A', 'cannot go back before the first letter'


def test_escape_pauses_and_resume_returns_to_the_same_letter(page):
    prepare(page)
    page.click('#begin')
    page.keyboard.press('ArrowRight')
    page.keyboard.press('Escape')
    assert page.locator('#paused').is_visible()
    assert 'Letter 2 of 26' in text(page, '#pauseInfo')
    page.click('#continueCheck')
    assert text(page, '#stimulusLetter') == 'B'


def test_pause_screen_shows_the_phone_companion_qr_again(page):
    prepare(page)
    page.click('#begin')
    page.click('#pause')
    assert not page.locator('#resumeQR').is_visible()
    page.click('#reopenCompanion')
    assert page.locator('#resumeQR svg').count() == 1
    assert page.locator('#resumeQR svg').is_visible()

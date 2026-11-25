"""Practice view: moving through a Practice deck."""
from steps import swipe


def test_next_and_previous_move_through_the_deck(page):
    first = page.locator('#letter').inner_text()
    assert page.locator('#counter').inner_text() == '1 / 26'
    assert page.locator('#prev').is_disabled()
    page.click('#next')
    assert page.locator('#counter').inner_text() == '2 / 26'
    assert page.locator('#letter').inner_text() != first
    page.click('#prev')
    assert page.locator('#counter').inner_text() == '1 / 26'
    assert page.locator('#letter').inner_text() == first


def test_shuffle_off_gives_alphabetical_order(page):
    assert page.locator('#shuffle').get_attribute('aria-pressed') == 'true'
    page.click('#shuffle')
    assert page.locator('#shuffle').inner_text() == 'Shuffle: off'
    assert page.locator('#shuffle').get_attribute('aria-pressed') == 'false'
    seen = []
    for _ in range(3):
        seen.append(page.locator('#letter').inner_text())
        page.click('#next')
    assert seen == ['A', 'B', 'C']
    page.click('#shuffle')
    assert page.locator('#shuffle').inner_text() == 'Shuffle: on'
    assert page.locator('#counter').inner_text() == '1 / 26'


def test_practice_again_at_the_end_of_the_deck_starts_a_new_deck(page):
    page.click('#shuffle')
    for _ in range(25):
        page.click('#next')
    assert page.locator('#counter').inner_text() == '26 / 26'
    assert page.locator('#next').inner_text() == 'Practice again ↻'
    page.click('#next')
    assert page.locator('#counter').inner_text() == '1 / 26'
    assert page.locator('#letter').inner_text() == 'A'
    assert page.locator('#next').inner_text() == 'Next →'


def test_focus_mode_taps_advance_and_exit_returns(page):
    page.click('#focus')
    assert 'focus' in page.locator('body').get_attribute('class')
    page.click('#card')
    assert page.locator('#counter').inner_text() == '2 / 26'
    page.click('#exitFocus')
    assert 'focus' not in page.locator('body').get_attribute('class')
    page.click('#card')
    assert page.locator('#counter').inner_text() == '2 / 26', 'outside focus mode a tap does not advance'
    page.click('#focus')
    page.keyboard.press('Escape')
    assert 'focus' not in page.locator('body').get_attribute('class')


def test_keyboard_moves_through_the_deck(page):
    page.keyboard.press('ArrowRight')
    assert page.locator('#counter').inner_text() == '2 / 26'
    page.keyboard.press('Space')
    assert page.locator('#counter').inner_text() == '3 / 26'
    page.keyboard.press('ArrowLeft')
    assert page.locator('#counter').inner_text() == '2 / 26'


def test_swipes_on_the_card_move_through_the_deck(page):
    swipe(page, '#card', -120)
    assert page.locator('#counter').inner_text() == '2 / 26'
    swipe(page, '#card', 120)
    assert page.locator('#counter').inner_text() == '1 / 26'


def test_sounds_skill_changes_the_help_text(page):
    assert page.locator('#practiceHelp').inner_text().startswith('Ask for the letter name')
    page.click('#skillGroup [data-skill=sound]')
    assert page.locator('#practiceHelp').inner_text().startswith('Ask for the target letter sound')


def test_needs_practice_with_no_results_shows_an_empty_deck_message(page):
    page.click('#filterGroup [data-filter=weak]')
    assert page.locator('#counter').inner_text() == '0 letters'
    assert page.locator('#practiceMessage').is_visible()
    assert 'No letters currently marked as needing practice' in page.locator('#practiceMessage').inner_text()
    assert page.locator('#next').is_disabled()
    assert page.locator('#focus').is_disabled()

"""Practice view: moving through a Practice deck."""
from steps import pressed, save_check, saved_data, seed, swipe, text


def needing_practice(letters, learner='1', skill='name'):
    """Saved data where each given letter's Result is Incorrect."""
    return saved_data(results={(learner, skill, letter): 'miss' for letter in letters})


def deck(page):
    """Every letter in the current deck, in order, from its first card; leaves the deck on its last card."""
    seen = [text(page, '#letter')]
    while text(page, '#next') != 'Practice again ↻':
        page.click('#next')
        seen.append(text(page, '#letter'))
    return seen


def set_buttons(page):
    return page.locator('#setGroup button')


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


def test_needs_practice_with_more_than_five_letters_practises_one_set_at_a_time(page):
    seed(page, needing_practice('ABCDEFGHIJK'))  # 11 letters: sets [A B C D] [E F G H] [I J K]
    assert not page.locator('#setGroup').is_visible(), 'All letters has no sets'
    page.click('#filterGroup [data-filter=weak]')
    assert page.locator('#setGroup').is_visible()
    assert set_buttons(page).all_inner_texts() == ['1', '2', '3']
    assert set_buttons(page).first.get_attribute('aria-label') == 'Set 1 of 3'
    assert pressed(page, '#setGroup [data-set="1"]')
    assert text(page, '#counter') == '1 / 4'
    assert sorted(deck(page)) == list('ABCD')
    page.click('#setGroup [data-set="2"]')
    assert pressed(page, '#setGroup [data-set="2"]') and not pressed(page, '#setGroup [data-set="1"]')
    assert text(page, '#counter') == '1 / 4', 'a chosen set starts from its first card'
    assert sorted(deck(page)) == list('EFGH')


def test_practice_again_at_the_end_of_a_set_repeats_the_same_set(page):
    seed(page, needing_practice('ABCDEFGHIJK'))
    page.click('#filterGroup [data-filter=weak]')
    page.click('#setGroup [data-set="3"]')
    first_round = deck(page)
    page.click('#next')
    assert text(page, '#counter') == '1 / 3'
    assert pressed(page, '#setGroup [data-set="3"]'), 'never moves on to the next set'
    assert sorted(deck(page)) == sorted(first_round) == list('IJK')
    assert text(page, '#counter') == '3 / 3'
    page.click('#shuffle')
    assert text(page, '#counter') == '1 / 3', 'toggling Shuffle starts the set from its first card'
    assert pressed(page, '#setGroup [data-set="3"]') and deck(page) == list('IJK'), 'with Shuffle off the set keeps its order'


def test_changing_learner_case_skill_or_filter_goes_back_to_set_1(page):
    seed(page, saved_data(results={(who, skill, letter): 'miss' for who in '12' for skill in ('name', 'sound')
                                   for letter in 'ABCDEFGHIJKabcdefghijk'}))
    page.click('#filterGroup [data-filter=weak]')
    for change in (lambda: page.select_option('#learner', '2'), lambda: page.click('#skillGroup [data-skill=sound]'),
                   lambda: page.click('#caseGroup [data-case=lower]'),
                   lambda: (page.click('#filterGroup [data-filter=all]'), page.click('#filterGroup [data-filter=weak]'))):
        page.click('#setGroup [data-set="2"]')
        change()
        assert pressed(page, '#setGroup [data-set="1"]') and not pressed(page, '#setGroup [data-set="2"]')


def test_needs_practice_with_five_letters_or_fewer_has_no_set_choice(page):
    seed(page, needing_practice('BDFHK'))
    page.click('#filterGroup [data-filter=weak]')
    assert not page.locator('#setGroup').is_visible()
    assert text(page, '#counter') == '1 / 5'
    assert sorted(deck(page)) == list('BDFHK')


def test_a_check_that_shrinks_the_sets_falls_back_to_set_1(page):
    seed(page, needing_practice('ABCDEFGHIJK'))
    page.click('#filterGroup [data-filter=weak]')
    page.click('#setGroup [data-set="3"]')
    save_check(page, 'cccccccc')  # A to H now Correct: one set [I J K] is left
    page.click('#tabPractice')
    assert not page.locator('#setGroup').is_visible()
    assert text(page, '#counter') == '1 / 3' and sorted(deck(page)) == list('IJK')

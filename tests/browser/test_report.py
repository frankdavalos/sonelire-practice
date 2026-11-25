"""Report: what a Learner struggled with before, and each letter's history, from the Check log."""
from steps import save_check


def letters(page, selector):
    return page.locator(f'{selector} button').all_inner_texts()


def struggled_twice(page):
    """Check 1 marks A and B Incorrect, C Correct; Check 2 marks A Correct, B Incorrect again."""
    save_check(page, 'iic')
    save_check(page, 'ci')


def test_struggled_before_lists_letters_still_needing_practice_and_letters_that_improved(page):
    struggled_twice(page)
    assert letters(page, '#stillNeedsPractice') == ['B']
    [improved] = page.locator('#improved li').all_inner_texts()
    assert improved.startswith('A') and 'correct since' in improved


def history(page):
    return page.locator('#historyList li').all_inner_texts()


def test_tapping_a_letter_in_the_today_grid_opens_its_history_newest_first(page):
    struggled_twice(page)
    page.click('#matrix [data-letter=A]')
    assert page.locator('#letterHistory').is_visible()
    assert page.locator('#historyTitle').inner_text().startswith('A')
    assert [row.rsplit(' · ', 1)[1] for row in history(page)] == ['Correct', 'Incorrect']
    page.click('#closeHistory')
    assert not page.locator('#letterHistory').is_visible()
    assert page.evaluate('document.activeElement.dataset.letter') == 'A', 'focus returns to the letter'


def test_letters_in_the_struggled_before_lists_open_their_history_too(page):
    struggled_twice(page)
    page.click('#stillNeedsPractice [data-letter=B]')
    assert [row.rsplit(' · ', 1)[1] for row in history(page)] == ['Incorrect', 'Incorrect']
    page.keyboard.press('Escape')
    page.click('#improved [data-letter=A]')
    assert page.locator('#historyTitle').inner_text().startswith('A')


def test_struggled_before_says_so_when_nothing_was_missed_and_follows_the_learner(page):
    save_check(page, 'cc')
    assert page.locator('#strugglesEmpty').is_visible()
    assert not page.locator('#struggles').is_visible()
    save_check(page, 'i')
    assert letters(page, '#stillNeedsPractice') == ['A']
    page.select_option('#learner', '2')
    assert page.locator('#strugglesEmpty').is_visible(), "Child 1's struggles never show for Child 2"

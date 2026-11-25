"""Report: which letters Improved after a struggle, and each letter's history, from the Check log."""
from steps import save_check, show_full_history


def improved(page):
    show_full_history(page)
    return page.locator('#improved li button').all_inner_texts()


def struggled_twice(page):
    """Check 1 marks A and B Incorrect, C Correct; Check 2 marks A Correct, B Incorrect again."""
    save_check(page, 'iic')
    save_check(page, 'ci')


def test_struggled_before_lists_letters_that_improved_with_their_dates(page):
    struggled_twice(page)
    show_full_history(page)
    [line] = page.locator('#improved li').all_inner_texts()
    assert line.startswith('A') and 'correct since' in line
    assert page.locator('#stillNeedsPractice').count() == 0, 'At a glance already names letters that need practice'


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


def test_letters_in_the_improved_list_open_their_history_too(page):
    struggled_twice(page)
    show_full_history(page)
    page.click('#improved [data-letter=A]')
    assert page.locator('#historyTitle').inner_text().startswith('A')
    assert [row.rsplit(' · ', 1)[1] for row in history(page)] == ['Correct', 'Incorrect']


def test_struggled_before_says_so_until_a_letter_improves_and_follows_the_learner(page):
    save_check(page, 'cc')
    show_full_history(page)
    assert page.locator('#strugglesEmpty').is_visible() and not page.locator('#struggles').is_visible()
    save_check(page, 'i')
    assert improved(page) == [] and page.locator('#strugglesEmpty').is_visible(), 'slipping back is not improving'
    save_check(page, 'c')
    assert improved(page) == ['A']
    page.select_option('#learner', '2')
    assert page.locator('#strugglesEmpty').is_visible(), "Child 1's letters never show for Child 2"


def test_struggled_before_follows_the_case_and_skill_selection(page):
    save_check(page, 'ii')
    save_check(page, 'c')
    save_check(page, 'i', case='lower', skill='sound')
    save_check(page, 'c', case='lower', skill='sound')
    page.click('#resultCase [data-value=upper]')
    page.click('#resultSkill [data-value=name]')
    assert improved(page) == ['A']
    page.click('#resultCase [data-value=lower]')
    assert improved(page) == [] and page.locator('#strugglesEmpty').is_visible()
    page.click('#resultSkill [data-value=sound]')
    assert improved(page) == ['a']
    page.click('#resultCase [data-value=upper]')
    assert improved(page) == []
    page.click('#resultCase [data-value=mixed]')
    assert improved(page) == ['a'], 'a mixed selection spans both Cases of this Skill'
    page.click('#resultSkill [data-value=name]')
    assert improved(page) == ['A']

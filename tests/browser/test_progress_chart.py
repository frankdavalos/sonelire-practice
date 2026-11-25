"""Progress chart: letters Correct after each Check, drawn above the Check list from the second Check."""
from steps import check_list, save_check, stat


def chart(page):
    return page.locator('#progressChart')


def chart_label(page):
    return chart(page).get_attribute('aria-label')


def test_one_check_shows_the_check_list_and_a_note_instead_of_a_chart(page):
    save_check(page, 'ci')
    assert len(check_list(page)) == 1
    assert not chart(page).is_visible()
    assert page.locator('#progressNote').is_visible()


def test_from_the_second_check_a_step_chart_of_letters_correct_is_drawn_above_the_check_list(page):
    save_check(page, 'ci')
    save_check(page, 'ccc')
    assert chart(page).is_visible() and not page.locator('#progressNote').is_visible()
    assert chart(page).locator('svg').count() == 1, 'inline SVG'
    assert chart_label(page).endswith('1, 3 of 26')
    assert chart_label(page).endswith(f'{stat(page, "Correct")} of 26'), "the last point is the Today grid's Correct total"
    assert chart(page).bounding_box()['y'] < page.locator('#checkList').bounding_box()['y']


def test_the_chart_follows_the_learner_case_and_skill_selection_and_counts_mixed_checks(page):
    save_check(page, 'cc', case='mixed')
    save_check(page, 'ic')
    page.click('#resultCase [data-value=upper]')
    assert chart_label(page).endswith('1, 1 of 26'), 'the mixed Check marked A Correct; the uppercase Check then marked A Incorrect and B Correct'
    page.click('#resultCase [data-value=mixed]')
    assert chart_label(page).endswith('2, 2 of 52')
    page.click('#resultCase [data-value=lower]')
    assert not chart(page).is_visible() and page.locator('#progressNote').is_visible()
    page.click('#resultCase [data-value=upper]')
    page.click('#resultSkill [data-value=sound]')
    assert not chart(page).is_visible()
    page.click('#resultSkill [data-value=name]')
    assert chart(page).is_visible()
    page.select_option('#learner', '2')
    assert not chart(page).is_visible(), "Child 1's Checks never chart for Child 2"

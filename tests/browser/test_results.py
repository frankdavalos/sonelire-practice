"""Results view: what is shown, and permanently clearing it."""
from steps import accept_next_dialog, saved_data, seed, stat


def seeded_results(page):
    seed(page, saved_data(results={
        ('1', 'name', 'A'): 'miss', ('1', 'name', 'a'): 'miss', ('1', 'name', 'B'): 'correct',
        ('1', 'sound', 'A'): 'miss', ('2', 'name', 'A'): 'miss'}))
    page.click('#tabResults')


def test_clear_these_results_removes_only_that_learner_skill_and_case(page):
    seeded_results(page)
    assert (stat(page, 'Correct'), stat(page, 'Needs practice')) == (1, 1)
    page.click('#resetResults')  # unanswered confirm is dismissed: nothing changes
    assert stat(page, 'Needs practice') == 1
    messages = accept_next_dialog(page)
    page.click('#resetResults')
    assert messages == ['Clear uppercase letter names results for Child 1? This cannot be undone.']
    assert (stat(page, 'Correct'), stat(page, 'Needs practice'), stat(page, 'Not assessed')) == (0, 0, 26)
    page.reload()
    page.click('#tabResults')
    assert stat(page, 'Not assessed') == 26, 'the clear is saved'
    page.click('#resultCase [data-value=lower]')
    assert stat(page, 'Needs practice') == 1, 'lowercase is a different Case'
    page.click('#resultSkill [data-value=sound]')
    page.click('#resultCase [data-value=upper]')
    assert stat(page, 'Needs practice') == 1, 'sounds is a different Skill'
    page.select_option('#learner', '2')
    page.click('#resultSkill [data-value=name]')
    assert stat(page, 'Needs practice') == 1, 'Child 2 is a different Learner'


def test_clearing_mixed_case_results_clears_both_cases(page):
    seeded_results(page)
    page.click('#resultCase [data-value=mixed]')
    assert stat(page, 'Needs practice') == 2
    accept_next_dialog(page)
    page.click('#resetResults')
    assert stat(page, 'Not assessed') == 52
    for case in ['upper', 'lower']:
        page.click(f'#resultCase [data-value={case}]')
        assert stat(page, 'Correct') + stat(page, 'Needs practice') == 0

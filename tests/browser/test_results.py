"""Results view: what is shown, and permanently clearing it."""
from steps import accept_next_dialog, check_list, saved_data, seed, stat

LOG_KEY = 'sonelire-check-log-v1'


def seeded_results(page):
    seed(page, saved_data(results={
        ('1', 'name', 'A'): 'miss', ('1', 'name', 'a'): 'miss', ('1', 'name', 'B'): 'correct',
        ('1', 'sound', 'A'): 'miss', ('2', 'name', 'A'): 'miss'}))
    page.click('#tabResults')


def check_record(form_id, day, marks, learner='1', skill='name', case='upper'):
    """A stored Check record saved on 2026-11-<day>; marks maps letter to Mark."""
    return {'date': f'2026-11-{day:02d}T09:00:00.000Z', 'learner': learner, 'skill': skill, 'case': case,
            'formId': form_id, 'shownCount': len(marks), 'marks': [{'letter': l, 'mark': m} for l, m in marks.items()]}


def seeded_history(page):
    """Child 1 names: A and B Incorrect on 1 Nov, A Correct and a Incorrect (mixed) on 3 Nov, B Incorrect on 5 Nov; plus Child 2 and sounds."""
    checks = [check_record('UP-1', 1, {'A': 'incorrect', 'B': 'incorrect'}),
              check_record('MIX', 3, {'A': 'correct', 'a': 'incorrect'}, case='mixed'),
              check_record('UP-2', 5, {'B': 'incorrect'}),
              check_record('CHILD-2', 6, {'A': 'incorrect'}, learner='2'),
              check_record('SOUND', 7, {'A': 'incorrect'}, skill='sound')]
    page.evaluate('([k, log]) => localStorage.setItem(k, JSON.stringify(log))', [LOG_KEY, {'version': 1, 'lastBackup': None, 'checks': checks}])
    seed(page, saved_data(results={('1', 'name', 'A'): 'correct', ('1', 'name', 'B'): 'miss', ('1', 'name', 'a'): 'miss',
                                   ('2', 'name', 'A'): 'miss', ('1', 'sound', 'A'): 'miss'}))
    page.click('#tabResults')


def test_the_clear_confirmation_names_the_check_records_affected_and_dismissing_it_changes_nothing(device):
    page = device(1366, 1024, locale='en-GB', timezone_id='UTC').open()
    seeded_history(page)
    before = check_list(page)
    messages = []
    page.once('dialog', lambda d: (messages.append(d.message), d.dismiss()))
    page.click('#resetResults')
    assert messages == ['Clear uppercase letter names results for Child 1?\n\n'
                        'This also removes these letters from 3 saved checks (1 Nov 2026 – 5 Nov 2026). '
                        'Export a backup first if you might want them back.\n\nThis cannot be undone.']
    assert check_list(page) == before and stat(page, 'Needs practice') == 1
    page.reload()
    page.click('#tabResults')
    assert check_list(page) == before, 'nothing was saved'


def report_is_empty(page):
    return (stat(page, 'Not assessed') == 26 and page.locator('#strugglesEmpty').is_visible()
            and check_list(page) == [] and page.locator('#checkListEmpty').is_visible() and not page.locator('#progressChart').is_visible())


def test_confirming_clears_those_letters_from_today_struggled_before_and_progress_and_survives_a_reload(page):
    seeded_history(page)
    assert len(check_list(page)) == 3 and page.locator('#progressChart').is_visible()
    accept_next_dialog(page)
    page.click('#resetResults')
    assert report_is_empty(page)
    page.reload()
    page.click('#tabResults')
    assert report_is_empty(page), 'the clear is saved'
    page.click('#resultCase [data-value=lower]')
    [mixed] = check_list(page)
    assert 'Form MIX' in mixed and '1 letter shown' in mixed, 'the mixed Check keeps its lowercase letter'
    assert page.locator('#stillNeedsPractice button').all_inner_texts() == ['a']
    page.click('#resultCase [data-value=upper]')
    page.click('#resultSkill [data-value=sound]')
    assert len(check_list(page)) == 1, 'sounds is a different Skill'
    page.select_option('#learner', '2')
    page.click('#resultSkill [data-value=name]')
    assert len(check_list(page)) == 1, 'Child 2 is a different Learner'


LOG_WRITES_CAN_FAIL = """const setItem = Storage.prototype.setItem;
Storage.prototype.setItem = function (key, value) {
  if (key === 'sonelire-check-log-v1' && window.logWritesFail) throw new DOMException('full', 'QuotaExceededError');
  return setItem.call(this, key, value);
};"""


def test_a_clear_that_cannot_be_saved_changes_nothing_and_says_so(device):
    ipad = device(1366, 1024)
    ipad.context.add_init_script(LOG_WRITES_CAN_FAIL)
    page = ipad.open()
    seeded_history(page)
    before = check_list(page)
    page.evaluate('window.logWritesFail = true')
    messages = []
    page.on('dialog', lambda d: (messages.append(d.message), d.accept()))
    page.click('#resetResults')
    assert messages[1:] == ['These results could not be cleared on this device. Nothing was changed.']
    assert page.locator('#storageNotice').is_visible()
    assert check_list(page) == before and stat(page, 'Needs practice') == 1
    page.reload()
    page.click('#tabResults')
    assert check_list(page) == before and stat(page, 'Needs practice') == 1, 'nothing was saved'


def cell(page, letter):
    """The lines shown in one letter's cell of the Results grid."""
    return page.locator(f'#matrix [data-letter={letter}]').inner_text().split('\n')


def test_clear_these_results_removes_only_that_learner_skill_and_case(page):
    seeded_results(page)
    assert (stat(page, 'Correct'), stat(page, 'Needs practice')) == (1, 1)
    page.click('#resetResults')  # unanswered confirm is dismissed: nothing changes
    assert stat(page, 'Needs practice') == 1
    messages = accept_next_dialog(page)
    page.click('#resetResults')
    assert messages == ['Clear uppercase letter names results for Child 1?\n\nNo saved checks hold these letters. '
                        'Export a backup first if you might want them back.\n\nThis cannot be undone.']
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


def test_each_letter_shows_when_it_was_last_checked_and_unchecked_letters_show_none(device):
    page = device(1366, 1024, locale='en-GB', timezone_id='UTC').open()
    saved = saved_data(results={('1', 'name', 'A'): 'correct', ('1', 'name', 'B'): 'skip'})
    saved['results']['1']['name']['A']['date'] = '2026-11-12T18:45:09.123Z'
    seed(page, saved)
    page.click('#tabResults')
    assert cell(page, 'A') == ['A', 'Correct', '12 Nov 2026']
    assert cell(page, 'B') == ['B', 'Skipped', '1 Jan 2026']
    assert cell(page, 'C') == ['C', 'Not checked']

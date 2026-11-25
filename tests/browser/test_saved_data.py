"""Saved data: return links, unavailable storage, other tabs, and data saved before the refactor (docs/adr/0001)."""
from steps import MAIN, check_list, UPPER, accept_next_dialog, pressed, results_code, saved_data, seed, stat, text

NO_STORAGE = "Object.defineProperty(window, 'localStorage', {get() { throw new DOMException('denied', 'SecurityError') }})"


def test_return_link_with_no_check_in_marking_alerts_and_drops_the_code(ipad):
    page = ipad.open('about:blank')
    messages = accept_next_dialog(page)
    page.goto(MAIN + '#sonelire-result=' + results_code('F1', 'C'))
    assert messages and messages[0].startswith('No matching scoring session is open here.')
    assert page.url == MAIN, 'the Results code is removed from the address and history entry'
    assert page.locator('#practice').is_visible()


def test_unavailable_storage_shows_a_notice_and_the_app_still_works(device):
    ipad = device(1366, 1024)
    ipad.context.add_init_script(NO_STORAGE)
    page = ipad.open()
    assert page.locator('#storageNotice').is_visible()
    page.click('#next')
    assert text(page, '#counter') == '2 / 26'


def test_a_change_saved_in_another_tab_reloads_this_one(ipad):
    here, other = ipad.open(), ipad.open()
    with here.expect_navigation():
        other.select_option('#learner', '2')
    assert here.locator('#learner').input_value() == '2'


def v1_draft(status, position, shown, scores, learner='2'):
    return {'learner': learner, 'case': 'upper', 'skill': 'name', 'seq': list(UPPER), 'id': 'V1-FORM',
            'position': position, 'shown': shown, 'status': status, 'scores': scores}


def test_v1_paused_draft_resumes_presentation_at_its_letter(page):
    seed(page, saved_data(draft=v1_draft('paused', position=3, shown=4, scores={})))
    assert text(page, '#draftMessage') == 'Unfinished check for Child 2: Uppercase letter names.'
    page.click('#resumeDraft')
    assert page.locator('#learner').input_value() == '2'
    assert 'Letter 4 of 26' in text(page, '#pauseInfo')
    page.click('#continueCheck')
    assert text(page, '#stimulusLetter') == 'D'


def test_v1_scoring_draft_with_miss_marks_resumes_marking_and_saves_incorrect(page):
    seed(page, saved_data(draft=v1_draft('scoring', position=2, shown=3, scores={'0': 'miss', '1': 'correct'})))
    page.click('#resumeDraft')
    assert page.locator('#scoring').is_visible()
    assert pressed(page, '#scoreList [data-index="0"] [data-value=incorrect]')
    assert text(page, '#scoredCount') == '2 / 3 marked'
    page.click('#scoreList [data-index="2"] [data-value=skip]')
    page.click('#saveScores')
    assert (stat(page, 'Correct'), stat(page, 'Needs practice')) == (1, 1)
    saved = page.evaluate('JSON.parse(localStorage.getItem("sonelire-practice-v2"))')
    assert saved['results']['2']['name']['A']['status'] == 'miss', 'Incorrect is still stored as v1 "miss"'
    assert saved['draft'] is None


def test_saved_data_with_no_check_log_key_shows_no_history_in_the_report(page):
    seed(page, saved_data(results={('1', 'name', 'A'): 'miss', ('1', 'name', 'B'): 'correct'}))
    assert page.evaluate('localStorage.getItem("sonelire-check-log-v1")') is None
    page.click('#tabResults')
    assert (stat(page, 'Correct'), stat(page, 'Needs practice')) == (1, 1), 'the saved Results still load'
    assert check_list(page) == [] and page.locator('#checkListEmpty').is_visible()
    assert not page.locator('#progressChart').is_visible()
    assert not page.locator('#struggles').is_visible() and page.locator('#strugglesEmpty').is_visible()
    assert page.locator('#stillNeedsPractice button, #improved li').count() == 0

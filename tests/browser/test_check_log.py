"""Check log: every saved Check is kept as a Check record and listed under Progress on the Results tab."""
from steps import accept_next_dialog, check_list, present, save_check, stat


def test_saving_a_check_lists_it_under_progress_and_it_survives_a_reload(page):
    form_id = save_check(page, 'cins')
    [entry] = check_list(page)
    for part in (form_id, 'Uppercase', '4 letters shown', '1 correct', '2 need practice', '1 skipped'):
        assert part in entry
    page.reload()
    page.click('#tabResults')
    assert check_list(page) == [entry]


LOG_WRITE_FAILS = """const setItem = Storage.prototype.setItem;
Storage.prototype.setItem = function (key, value) {
  if (key === 'sonelire-check-log-v1') throw new DOMException('full', 'QuotaExceededError');
  return setItem.call(this, key, value);
};"""


def test_a_check_log_that_cannot_be_written_keeps_the_check_in_marking_and_results_unchanged(device):
    ipad = device(1366, 1024)
    ipad.context.add_init_script(LOG_WRITE_FAILS)
    page = ipad.open()
    present(page, shown=1)
    page.click('#scoreList [data-index="0"] [data-value=correct]')
    messages = accept_next_dialog(page)
    page.click('#saveScores')
    assert messages == ['Your marks could not be saved on this device. They are still here — try Save again.']
    assert page.locator('#scoring').is_visible(), 'still in Marking, so the Marks can be saved again'
    assert page.locator('#storageNotice').is_visible()
    page.reload()
    assert page.locator('#draftNotice').is_visible(), 'the Unfinished check is still saved'
    page.click('#tabResults')
    assert stat(page, 'Correct') == 0
    assert check_list(page) == []


def test_the_check_list_follows_the_learner_case_and_skill_selection(page):
    mixed = save_check(page, 'cc', case='mixed')
    upper = save_check(page, 'c')
    page.click('#resultCase [data-value=upper]')
    assert [upper in e for e in check_list(page)] == [True, False], 'newest first'
    assert mixed in check_list(page)[1] and 'Mixed case' in check_list(page)[1], 'a mixed Check counts for uppercase'
    page.click('#resultCase [data-value=lower]')
    assert len(check_list(page)) == 1 and mixed in check_list(page)[0]
    page.click('#resultSkill [data-value=sound]')
    assert check_list(page) == []
    assert page.locator('#checkListEmpty').is_visible()
    page.click('#resultSkill [data-value=name]')
    page.select_option('#learner', '2')
    assert check_list(page) == [], "Child 1's Checks never show for Child 2"


def test_discarding_an_unfinished_check_adds_no_check_record(page):
    present(page, shown=2)
    page.click('#scoreLater')
    accept_next_dialog(page)
    page.click('#discardDraft')
    page.click('#tabResults')
    assert check_list(page) == []


def test_with_storage_unavailable_from_the_start_a_check_still_saves_for_this_visit(device):
    ipad = device(1366, 1024)
    ipad.context.add_init_script("Object.defineProperty(window, 'localStorage', {get() { throw new DOMException('denied', 'SecurityError') }})")
    page = ipad.open()
    save_check(page, 'ci')
    assert page.locator('#results').is_visible()
    assert stat(page, 'Correct') == 1 and len(check_list(page)) == 1


def test_unreadable_saved_data_is_replaced_by_the_next_saved_check(page):
    page.evaluate('localStorage.setItem("sonelire-practice-v2", "not json"); localStorage.setItem("sonelire-check-log-v1", "{")')
    page.reload()
    assert page.locator('#storageNotice').is_visible()
    save_check(page, 'c')
    page.reload()
    assert not page.locator('#storageNotice').is_visible()
    page.click('#tabResults')
    assert stat(page, 'Correct') == 1 and len(check_list(page)) == 1

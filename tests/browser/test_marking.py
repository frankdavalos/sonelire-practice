"""Marking: entering, importing and discarding Marks for an Unfinished check."""
from playwright.sync_api import expect
from steps import accept_next_dialog, present, pressed, results_code, saved_data, seed, stat, text


def row_mark(page, index, value):
    return pressed(page, f'#scoreList [data-index="{index}"] [data-value={value}]')


def test_keyboard_marks_the_focused_row_and_moves_to_the_next(page):
    present(page, shown=4)
    page.focus('#scoreList [data-index="0"]')
    for key in 'cins':
        page.keyboard.press(key)
    assert [row_mark(page, i, v) for i, v in enumerate(['correct', 'incorrect', 'unsure', 'skip'])] == [True] * 4
    assert page.evaluate('document.activeElement.dataset.index') == '3', 'focus stays on the last shown row'
    assert text(page, '#scoredCount') == '4 / 4 marked'
    assert page.locator('#saveScores').is_enabled()


def test_mark_remaining_as_correct_fills_only_unmarked_shown_letters(page):
    present(page, shown=3)
    page.click('#scoreList [data-index="1"] [data-value=incorrect]')
    page.click('#fillCorrect')  # unanswered confirm is dismissed: nothing changes
    assert text(page, '#scoredCount') == '1 / 3 marked'
    accept_next_dialog(page)
    page.click('#fillCorrect')
    assert [row_mark(page, 0, 'correct'), row_mark(page, 1, 'incorrect'), row_mark(page, 2, 'correct')] == [True] * 3
    assert page.locator('#scoreList [data-index="3"] button').first.is_disabled(), 'letters not shown cannot be marked'


def test_clear_marks_removes_every_mark(page):
    present(page, shown=2)
    page.click('#scoreList [data-index="0"] [data-value=correct]')
    page.click('#scoreList [data-index="1"] [data-value=skip]')
    accept_next_dialog(page)
    page.click('#clearMarks')
    assert text(page, '#scoredCount') == '0 / 2 marked'
    assert not row_mark(page, 0, 'correct')
    assert page.locator('#saveScores').is_disabled()


def test_discarding_an_unfinished_check_keeps_results_and_frees_the_assess_tab(page):
    seed(page, saved_data(results={('1', 'name', 'A'): 'miss'}))
    present(page, shown=1)
    page.click('#scoreLater')
    assert page.locator('#draftNotice').is_visible()
    assert text(page, '#draftMessage') == 'Unfinished check for Child 1: Uppercase letter names.'
    accept_next_dialog(page)
    page.click('#discardDraft')
    assert not page.locator('#draftNotice').is_visible()
    page.click('#tabAssess')
    assert page.locator('#setup').is_visible(), 'with no Unfinished check, Assess opens setup instead of resuming'
    page.reload()
    assert not page.locator('#draftNotice').is_visible()
    page.click('#tabResults')
    assert stat(page, 'Needs practice') == 1, 'previously saved Results are kept'


def test_results_code_file_is_loaded_and_imported(page):
    form_id = present(page, shown=2)
    page.locator('#importPanel summary').click()
    code = results_code(form_id, 'CI')
    page.set_input_files('#importFile', files=[{'name': 'r.txt', 'mimeType': 'text/plain', 'buffer': f'{code}\n'.encode()}])
    expect(page.locator('#importCode')).to_have_value(code)
    expect(page.locator('#importMessage')).to_contain_text('Code loaded')
    page.click('#importButton')
    assert text(page, '#scoredCount') == '2 / 2 marked'
    assert row_mark(page, 1, 'incorrect')


def test_results_code_file_over_4_kb_is_refused(page):
    present(page, shown=1)
    page.locator('#importPanel summary').click()
    page.set_input_files('#importFile', files=[{'name': 'big.txt', 'mimeType': 'text/plain', 'buffer': b'S' * 4097}])
    expect(page.locator('#importMessage')).to_have_text('Results file is too large.')
    assert page.locator('#importCode').input_value() == ''


def test_import_over_different_marks_asks_before_replacing_them_naming_the_letters(page):
    form_id = present(page, shown=3)
    page.click('#scoreList [data-index="0"] [data-value=incorrect]')
    page.click('#scoreList [data-index="2"] [data-value=correct]')
    page.locator('#importPanel summary').click()
    page.fill('#importCode', results_code(form_id, 'CCC'))
    messages = []
    page.once('dialog', lambda d: (messages.append(d.message), d.dismiss()))
    page.click('#importButton')
    assert messages == ['Replace existing entries for A with the phone marks?']
    assert row_mark(page, 0, 'incorrect'), 'declining keeps the existing marks'
    accept_next_dialog(page)
    page.click('#importButton')
    assert row_mark(page, 0, 'correct')
    assert text(page, '#importMessage') == 'Imported 3 marks. Review the entries, then select Save results.'

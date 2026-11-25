"""Backup file: export everything saved from the Results tab, and restore it after a preview."""
import json
from datetime import datetime
from pathlib import Path
from steps import check_list, present, save_check, stat, text


def export_backup(page):
    """Export a backup from the Results tab; returns (file name, parsed file)."""
    page.click('#tabResults')
    with page.expect_download() as download:
        page.click('#exportBackup')
    d = download.value
    return d.suggested_filename, json.loads(Path(d.path()).read_text())


def test_export_downloads_both_learners_results_and_check_log_and_records_the_last_backup(page):
    first = save_check(page, 'ci')
    page.select_option('#learner', '2')
    second = save_check(page, 'c', skill='sound')
    present(page, shown=1)
    page.click('#scoreLater')
    page.click('#tabResults')
    assert text(page, '#lastBackup') == 'Last backup: never'
    name, backup = export_backup(page)
    exported_on = datetime.fromisoformat(backup['exportedAt']).astimezone().date()
    assert name == f'sonelire-backup-{exported_on.isoformat()}.json', 'named for the local date'
    assert set(backup) == {'format', 'version', 'exportedAt', 'results', 'checks'}, 'no Unfinished check or selected Learner'
    assert (backup['format'], backup['version']) == ('sonelire-backup', 1)
    assert backup['results']['1']['name']['B']['status'] == 'miss' and backup['results']['2']['sound']['A']['status'] == 'correct'
    assert [c['formId'] for c in backup['checks']] == [first, second]
    assert text(page, '#lastBackup').startswith('Last backup: ') and 'never' not in text(page, '#lastBackup')
    shown = text(page, '#lastBackup')
    page.reload()
    page.click('#tabResults')
    assert text(page, '#lastBackup') == shown


def choose_file(page, backup):
    body = backup if isinstance(backup, bytes) else json.dumps(backup).encode()
    page.set_input_files('#restoreFile', files=[{'name': 'backup.json', 'mimeType': 'application/json', 'buffer': body}])


def choose_backup(page, backup, confirm=True):
    """Choose a backup file to restore and answer its confirmation; returns the confirmation's message."""
    with page.expect_event('dialog') as dialog:
        choose_file(page, backup)
    message = dialog.value.message
    if confirm:
        dialog.value.accept()
        page.locator('#backupMessage', has_text='Restored').wait_for()
    else:
        dialog.value.dismiss()
    return message


def test_restore_previews_the_backup_then_replaces_results_and_check_log_and_keeps_the_unfinished_check(page):
    kept = save_check(page, 'cc')
    _, backup = export_backup(page)
    page.select_option('#learner', '2')
    save_check(page, 'iii')
    unfinished = present(page, shown=1, case='lower')
    page.click('#scoreLater')
    page.click('#tabResults')
    message = choose_backup(page, backup)
    assert 'Child 1: 1 saved check' in message and 'Child 2: 0 saved checks' in message
    assert 'Latest check: ' in message
    page.reload()
    assert page.locator('#learner').input_value() == '2', 'the selected Learner is kept'
    assert 'Child 2: Lowercase letter names' in text(page, '#draftMessage'), 'the Unfinished check is kept'
    page.click('#tabResults')
    assert check_list(page) == [], "Child 2's Check was replaced"
    page.select_option('#learner', '1')
    assert len(check_list(page)) == 1 and kept in check_list(page)[0]
    assert 'never' not in text(page, '#lastBackup')
    page.click('#resumeDraft')
    assert unfinished in text(page, '#scoreInfo')


def test_cancelling_a_restore_changes_nothing(page):
    _, backup = export_backup(page)
    form_id = save_check(page, 'c')
    page.click('#tabResults')
    message = choose_backup(page, backup, confirm=False)
    assert 'Child 1: 0 saved checks' in message
    page.reload()
    page.click('#tabResults')
    assert len(check_list(page)) == 1 and form_id in check_list(page)[0]


def test_a_damaged_wrong_or_oversized_file_is_refused_with_saved_data_unchanged(page):
    _, backup = export_backup(page)
    form_id = save_check(page, 'c')
    page.click('#tabResults')
    confirmations = []
    page.on('dialog', lambda d: (confirmations.append(d.message), d.dismiss()))
    damaged = {**backup, 'checks': [{'learner': '3'}]}
    for file, reason in [(b'{', 'not JSON'), (json.dumps({**backup, 'format': 'other'}).encode(), 'not a Sonelire backup'),
                         (json.dumps(damaged).encode(), 'check record'), (b' ' * (5 * 1024 * 1024 + 1), 'over 5 MB')]:
        choose_file(page, file)
        message = page.locator('#backupMessage')
        message.filter(has_text=reason).wait_for()
        assert message.inner_text().startswith('Nothing was restored.')
    assert confirmations == []
    page.reload()
    page.click('#tabResults')
    assert len(check_list(page)) == 1 and form_id in check_list(page)[0]
    assert text(page, '#lastBackup') != 'Last backup: never'


def short_date(page, iso):
    """A date as the page shows it."""
    return page.evaluate("iso => new Date(iso).toLocaleDateString(undefined, {day: 'numeric', month: 'short', year: 'numeric'})", iso)


def test_the_restore_preview_names_the_date_of_the_latest_check_in_the_backup(page):
    save_check(page, 'c')
    save_check(page, 'c')
    _, backup = export_backup(page)
    older, newer = '2026-03-14T12:00:00.000Z', '2026-05-02T12:00:00.000Z'
    backup['checks'][0]['date'], backup['checks'][1]['date'] = newer, older
    message = choose_backup(page, backup, confirm=False)
    assert f'Latest check: {short_date(page, newer)}\n' in message
    assert short_date(page, older) not in message


def cells(page):
    """Each letter cell of the Today grid: (letter, shows a last-checked date, mark class)."""
    return page.locator('#matrix .cell').evaluate_all(
        "els => els.map(e => [e.dataset.letter, !!e.querySelector('.when'), e.className.replace('cell ', '')])")


def test_restore_replaces_the_results_in_the_today_grid_and_they_survive_a_reload(page):
    save_check(page, 'cc')
    _, backup = export_backup(page)
    save_check(page, 'iic')
    page.select_option('#learner', '2')
    save_check(page, 'cc')
    page.click('#tabResults')
    choose_backup(page, backup)
    assert (stat(page, 'Correct'), stat(page, 'Needs practice')) == (0, 0), "Child 2's newer Results are replaced at once"
    page.reload()  # straight away: no later interaction re-saves the Results
    page.click('#tabResults')
    assert page.locator('#learner').input_value() == '2'
    assert (stat(page, 'Correct'), stat(page, 'Needs practice')) == (0, 0), "Child 2's newer Results stay replaced"
    assert not any(has_date for _, has_date, _ in cells(page))
    page.select_option('#learner', '1')
    assert (stat(page, 'Correct'), stat(page, 'Needs practice')) == (2, 0), "Child 1 is back to the backup's Results"
    assert cells(page)[:3] == [['A', True, 'correct'], ['B', True, 'correct'], ['C', False, 'not-assessed']]

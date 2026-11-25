"""At a glance: the Results tab's summary of letters Correct, the Latest change and its groups (CONTEXT.md)."""
from steps import pressed, save_check, saved_data, seed, text


def headline(page):
    return text(page, '#glanceRing'), text(page, '#glanceChange'), text(page, '#glanceCounts')


def test_with_no_checks_the_summary_says_nothing_yet_and_offers_a_check(page):
    page.click('#tabResults')
    assert page.locator('#glanceEmpty').is_visible() and not page.locator('#glance').is_visible()
    assert not page.locator('#glanceLines').is_visible()
    page.click('#checkFirst')
    assert page.locator('#setup').is_visible()


def test_the_headline_counts_letters_correct_and_says_how_that_changed_since_the_previous_check(page):
    save_check(page, 'ic')  # A Incorrect, B Correct
    ring, change, counts = headline(page)
    assert ring.split() == ['1', 'of', '26']
    assert change.startswith('First check · ')
    assert counts == '1 needs practice · 24 not checked yet'
    assert text(page, '#lastCheck').startswith('Last check: ')

    save_check(page, 'cc')
    ring, change, counts = headline(page)
    assert ring.split()[0] == '2' and change.startswith('↗ 1 more letter correct · compared with ')
    assert 'gain' in page.locator('#glanceChange').get_attribute('class')
    assert counts == '0 need practice · 24 not checked yet'

    save_check(page, 'ii')
    ring, change, _ = headline(page)
    assert ring.split()[0] == '0' and change.startswith('2 fewer letters correct than ')
    assert 'gain' not in page.locator('#glanceChange').get_attribute('class'), 'a drop is never shown as a gain'

    save_check(page, 'i')
    assert headline(page)[1].startswith('Same as ')


def lines(page):
    return page.locator('#glanceLines p:visible').all_inner_texts()


def test_summary_lines_name_recent_wins_slipped_back_and_still_learning_letters_and_open_their_history(page):
    save_check(page, 'icic')  # A Incorrect, B Correct, C Incorrect, D Correct
    assert lines(page) == ['Still learning: A C'], 'with one Check every struggle is Still learning'
    save_check(page, 'cii')   # A Correct (win), B Incorrect (slipped), C Incorrect (still)
    assert lines(page) == ['Recent wins: A', 'Slipped back: B', 'Still learning: C']
    page.click('#glanceLines [data-letter=B]')
    assert page.locator('#historyTitle').inner_text().startswith('B')
    page.keyboard.press('Escape')
    save_check(page, 'ccc')
    assert lines(page) == ['Recent wins: B C'], 'a line with no letters is left out'


def test_the_practice_button_names_practice_set_1_and_starts_its_deck(page):
    page.click('#tabResults')
    assert page.locator('#practiceWeak').is_disabled(), 'nothing Needs practice yet'
    assert text(page, '#practiceWeak') == 'Nothing needs practice'
    save_check(page, 'icin')  # A, C Incorrect; D Unsure
    assert text(page, '#practiceWeak') == 'Practice A, C, D →'
    page.click('#practiceWeak')
    assert text(page, '#counter') == '1 / 3'
    save_check(page, 'iiiiii')  # B Slipped back, so it leads set 1 of [B A C] [D E F]
    assert text(page, '#practiceWeak') == 'Practice B, A, C →'



def test_the_practice_button_opens_set_1_with_the_results_tabs_case_and_skill(page):
    seed(page, saved_data(results={('1', skill, letter): 'miss' for skill in ('name', 'sound') for letter in 'ABCDEFGHIJKabcdefghijk'}))
    page.click('#filterGroup [data-filter=weak]')
    page.click('#setGroup [data-set="3"]')
    page.click('#tabResults')
    page.click('#resultCase [data-value=lower]')
    page.click('#resultSkill [data-value=sound]')
    assert text(page, '#practiceWeak') == 'Practice a, b, c, d →'
    page.click('#practiceWeak')
    assert page.locator('#practice').is_visible()
    for chosen in ('#filterGroup [data-filter=weak]', '#caseGroup [data-case=lower]', '#skillGroup [data-skill=sound]', '#setGroup [data-set="1"]'):
        assert pressed(page, chosen), chosen
    assert text(page, '#counter') == '1 / 4' and text(page, '#letter') in ('a', 'b', 'c', 'd')

def cell(page, letter):
    return page.locator(f'#matrix [data-letter={letter}]')


def test_grid_cells_show_direction_since_the_previous_check_with_words_not_colour_alone(page):
    save_check(page, 'ic')  # A Incorrect, B Correct
    assert page.locator('#matrix .badge').count() == 0, 'no direction after only one Check'
    save_check(page, 'ci')  # A Correct (Recent win), B Incorrect (Slipped back)
    assert cell(page, 'A').locator('.badge').inner_text() == '↑'
    assert cell(page, 'B').locator('.badge').inner_text() == '↓'
    assert cell(page, 'A').locator('.badge').get_attribute('aria-hidden') == 'true'
    label = cell(page, 'B').get_attribute('aria-label')
    assert label.startswith('B, Incorrect, checked ') and label.endswith(', slipped back. Show history.')
    assert cell(page, 'A').get_attribute('aria-label').endswith(', recent win. Show history.')
    assert cell(page, 'C').get_attribute('aria-label') == 'C, not checked yet. Show history.'
    assert cell(page, 'C').inner_text().split('\n') == ['C', 'Not checked yet']
    assert '↑ Recent win · ↓ Slipped back' in text(page, '#legend')
    assert page.locator('#stats').count() == 0, 'the headline card replaces the stats row'


def test_the_full_history_is_folded_away_and_struggled_before_keeps_only_improved_letters(page):
    save_check(page, 'ii')
    save_check(page, 'ci')  # A improved; B still Incorrect
    for detail in ('#struggles', '#progressChart', '#checkList', '#resetResults'):
        assert not page.locator(detail).is_visible(), f'{detail} starts folded away'
    assert page.locator('#exportBackup').is_visible(), 'Backup stays visible'
    page.click('#fullHistory summary')
    assert page.locator('#progressChart').is_visible() and page.locator('#resetResults').is_visible()
    assert page.locator('#stillNeedsPractice').count() == 0, 'Slipped back and Still learning already name these letters'
    assert page.locator('#improved li').all_inner_texts()[0].startswith('A')
    save_check(page, 'ii')
    page.click('#tabResults')
    assert text(page, '#strugglesEmpty') == 'No letter in this selection has improved yet.'


def test_at_a_glance_follows_the_learner_case_and_skill_selection(page):
    save_check(page, 'ii')
    save_check(page, 'ci')                                  # uppercase names: A Recent win, B Still learning
    save_check(page, 'c', case='lower', skill='sound')       # lowercase sounds: a, first Check
    page.click('#resultCase [data-value=upper]')
    page.click('#resultSkill [data-value=name]')
    assert lines(page) == ['Recent wins: A', 'Still learning: B'] and text(page, '#glanceRing').split()[0] == '1'
    page.click('#resultCase [data-value=lower]')
    assert page.locator('#glanceEmpty').is_visible(), 'no lowercase name Checks'
    page.click('#resultSkill [data-value=sound]')
    assert lines(page) == [] and text(page, '#glanceChange').startswith('First check · ')
    page.click('#resultCase [data-value=mixed]')
    assert text(page, '#glanceRing').split() == ['1', 'of', '52']
    page.select_option('#learner', '2')
    assert page.locator('#glanceEmpty').is_visible(), "Child 1's Checks never show for Child 2"

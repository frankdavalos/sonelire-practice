"""Progress chart: letters Correct after each Check, drawn above the Check list from the second Check."""
import re
from steps import check_list, save_check, stat, text


def chart(page):
    return page.locator('#progressChart')


def chart_label(page):
    return chart(page).get_attribute('aria-label')


def test_one_check_shows_the_check_list_and_a_note_instead_of_a_chart(page):
    save_check(page, 'ci')
    assert len(check_list(page)) == 1
    assert not chart(page).is_visible()
    assert page.locator('#progressNote').is_visible()
    assert 'after the second check' in text(page, '#progressNote').lower()


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


def test_the_chart_is_a_step_line_of_horizontal_and_vertical_segments_in_inline_svg_with_no_chart_library(page):
    scripts = []
    page.on('request', lambda r: r.resource_type == 'script' and scripts.append(r.url))
    save_check(page, 'c')
    save_check(page, 'cc')
    save_check(page, 'ccc')
    d = chart(page).locator('svg path').get_attribute('d')
    assert re.fullmatch(r'M[\d.]+,[\d.]+(H[\d.]+V[\d.]+){2}', d), f'a start point then one step per later Check, no diagonals: {d}'
    xs = [float(x) for x in re.findall(r'H([\d.]+)', d)]
    ys = [float(y) for y in re.findall(r'V([\d.]+)', d)]
    y0 = float(re.match(r'M[\d.]+,([\d.]+)', d).group(1))
    assert xs == sorted(xs) and len(set(xs)) == 2, 'time moves left to right'
    assert [y0] + ys == sorted([y0] + ys, reverse=True) and len({y0, *ys}) == 3, 'each Check with more letters Correct steps up'
    assert chart(page).locator('svg circle').count() == 3, 'one dot per Check'
    page.reload()
    page.click('#tabResults')
    sources = page.evaluate('[...document.scripts].map(s => s.src).filter(Boolean)')
    assert sources and all(s.startswith('https://frankdavalos.github.io/sonelire-practice/') for s in sources), sources
    assert not [s for s in sources if re.search(r'chart|d3|plotly|graph', s, re.I)], sources
    assert page.evaluate('["Chart", "d3", "Plotly", "echarts", "Highcharts"].filter(n => n in window)') == []

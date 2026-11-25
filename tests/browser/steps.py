"""Steps shared by the browser scenarios, in the parent's terms."""
SITE = 'https://frankdavalos.github.io/sonelire-practice/'
MAIN = SITE + 'sonelire-practice.html'
COMPANION = SITE + 'companion.html'
UPPER = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def text(page, selector):
    return page.locator(selector).inner_text()


def pressed(page, selector):
    return page.locator(selector).get_attribute('aria-pressed') == 'true'


def accept_next_dialog(page):
    """Accept the next confirm/alert and return a list that receives its message."""
    messages = []
    page.once('dialog', lambda d: (messages.append(d.message), d.accept()))
    return messages


def seed(page, saved):
    """Replace the main page's saved data with v1-shaped data (docs/adr/0001) and reload."""
    page.evaluate('s => localStorage.setItem("sonelire-practice-v2", JSON.stringify(s))', saved)
    page.reload()


def saved_data(learner='1', results=None, draft=None):
    r = {'1': {'name': {}, 'sound': {}}, '2': {'name': {}, 'sound': {}}}
    for (who, skill, letter), status in (results or {}).items():
        r[who][skill][letter] = {'status': status, 'date': '2026-01-01T00:00:00.000Z', 'form': 'SEED'}
    return {'version': 1, 'learner': learner, 'results': r, 'draft': draft}


def prepare(page, case='upper', skill='name', order='alpha'):
    """Prepare a Check from the Assess tab; returns its form ID."""
    page.click('#tabAssess')
    page.click(f'#assessCase [data-value={case}]')
    page.click(f'#assessSkill [data-value={skill}]')
    page.click(f'#assessOrder [data-value={order}]')
    page.click('#prepare')
    return text(page, '#preparedInfo').rsplit('Form ', 1)[1]


def present(page, shown, **form):
    """Prepare and begin a Check, show `shown` letters, then end Presentation into Marking. Returns the form ID."""
    form_id = prepare(page, **form)
    page.click('#begin')
    for _ in range(shown - 1):
        page.keyboard.press('ArrowRight')
    page.click('#pause')
    accept_next_dialog(page)
    page.click('#finishEarly')
    return form_id


def save_check(page, keys, **form):
    """Present len(keys) letters, mark them with the keyboard (c/i/n/s) and save. Returns the form ID."""
    form_id = present(page, shown=len(keys), **form)
    page.focus('#scoreList [data-index="0"]')
    for key in keys:
        page.keyboard.press(key)
    page.click('#saveScores')
    return form_id


def check_list(page):
    return page.locator('#checkList li').all_inner_texts()


def results_code(form_id, marks, skill='name', case='upper', seq=UPPER):
    """A Results code for an alphabetical Form; marks is a string of C/I/N/S, padded with '-' (unmarked)."""
    return f'SON1R.{form_id}.{skill}.{case}.{seq}.{marks.ljust(len(seq), "-")}'


def swipe(page, selector, dx):
    """Drag horizontally across the middle of an element, as a finger swipe."""
    box = page.locator(selector).bounding_box()
    x, y = box['x'] + box['width'] / 2, box['y'] + box['height'] / 2
    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.move(x + dx, y, steps=4)
    page.mouse.up()


def stat(page, label):
    """The Results view's total for 'Correct', 'Needs practice' or 'Not assessed'."""
    return int(page.locator('#stats .stat', has_text=label).locator('strong').inner_text())

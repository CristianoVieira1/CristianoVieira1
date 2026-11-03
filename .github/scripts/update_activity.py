"""Generate local, theme-aware cards from GitHub APIs. Run only in Actions."""
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from html import escape
from collections import Counter
import json
import os
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets' / 'stats'
USER = 'CristianoVieira1'
TOKEN = os.environ['GITHUB_TOKEN']
THEMES = {
    'dark': ('#080D13', '#10252C', '#F8FAFC', '#94A3B8', '#234149', '#1DB3B8'),
    'light': ('#FFFFFF', '#EDF8F8', '#10252C', '#475569', '#CCE4E5', '#087D82'),
}

def api(path, payload=None):
    data = json.dumps(payload).encode() if payload else None
    req = urllib.request.Request('https://api.github.com/' + path, data=data, headers={
        'Authorization': f'Bearer {TOKEN}', 'User-Agent': 'CristianoVieira1-profile',
        'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json',
    })
    with urllib.request.urlopen(req, timeout=45) as response:
        result = json.load(response)
    if isinstance(result, dict) and result.get('errors'):
        raise RuntimeError('GitHub GraphQL returned errors; previous assets retained.')
    return result

def panel(title, theme, rows, note):
    bg, surface, fg, muted, border, accent = THEMES[theme]
    h = 295
    body = f'<title>{escape(title)}</title><rect x=".5" y=".5" width="479" height="294" rx="20" fill="{bg}" stroke="{border}"/>'
    body += f'<g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif"><text x="26" y="42" fill="{accent}" font-size="23" font-weight="600">{escape(title)}</text>'
    for index, (label, value) in enumerate(rows):
        y = 87 + index * 34
        body += f'<text x="26" y="{y}" fill="{muted}" font-size="19">{escape(str(label))}</text><text x="452" y="{y}" text-anchor="end" fill="{fg}" font-size="21" font-weight="600">{escape(str(value))}</text>'
    body += f'<text x="26" y="265" fill="{muted}" font-size="13">{escape(note)}</text></g>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="480" height="{h}" viewBox="0 0 480 {h}" role="img">{body}</svg>'

def streak_wide(theme, rows, note):
    bg, surface, fg, muted, border, accent = THEMES[theme]
    body = f'<title>GitHub Streak</title><rect x=".5" y=".5" width="975" height="209" rx="20" fill="{bg}" stroke="{border}"/>'
    body += f'<g font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif"><text x="26" y="40" fill="{accent}" font-size="23" font-weight="600">GitHub Streak</text>'
    for index, (label, value) in enumerate(rows):
        x = 26 + index * 240
        body += f'<text x="{x}" y="104" fill="{fg}" font-size="37" font-weight="600">{value}</text><text x="{x}" y="139" fill="{muted}" font-size="17">{escape(label)}</text>'
    body += f'<text x="26" y="183" fill="{muted}" font-size="14">{escape(note)}</text></g>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="976" height="210" viewBox="0 0 976 210" role="img">{body}</svg>'


def combined(left, right, mobile=False):
    width, height = (480, 606) if mobile else (976, 295)
    root = ET.Element('svg', xmlns='http://www.w3.org/2000/svg', width=str(width), height=str(height), viewBox=f'0 0 {width} {height}', role='img')
    ET.SubElement(root, 'title').text = 'Estatísticas e linguagens dos repositórios públicos'
    for i, item in enumerate((left, right)):
        node = ET.fromstring(item)
        node.set('x', '0' if mobile or i == 0 else '496')
        node.set('y', '311' if mobile and i else '0')
        root.append(node)
    return ET.tostring(root, encoding='unicode')

def main():
    # Fetch everything before replacing any cards. Never fill unavailable data with zero.
    user = api(f'users/{USER}')
    repos = []
    page = 1
    while True:
        batch = api(f'users/{USER}/repos?per_page=100&type=owner&page={page}')
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    original = [repo for repo in repos if not repo['fork']]
    languages = Counter()
    for repo in original:
        languages.update(api(f'repos/{USER}/{repo["name"]}/languages'))
    query = '''query($login:String!) { user(login:$login) { contributionsCollection { contributionCalendar { weeks { contributionDays { date contributionCount } } } } } }'''
    data = api('graphql', {'query': query, 'variables': {'login': USER}})
    weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    today = datetime.now(timezone.utc).date()
    days = sorted((d for week in weeks for d in week['contributionDays'] if date.fromisoformat(d['date']) <= today), key=lambda d: d['date'])
    if not days:
        raise RuntimeError('Empty contribution calendar; previous assets retained.')
    longest = run = 0
    for day in days:
        run = run + 1 if day['contributionCount'] > 0 else 0
        longest = max(longest, run)
    by_date = {date.fromisoformat(d['date']): d['contributionCount'] for d in days}
    cursor = today if by_date.get(today, 0) else today - timedelta(days=1)
    current = 0
    while by_date.get(cursor, 0) > 0:
        current += 1
        cursor -= timedelta(days=1)
    stamp = datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M UTC')
    first, last = days[0]['date'], days[-1]['date']
    values = [('Contribuições no período', sum(d['contributionCount'] for d in days)), ('Dias com atividade', sum(d['contributionCount'] > 0 for d in days)), ('Sequência atual (dias)', current), ('Maior sequência (dias)', longest)]
    stats = [('Repositórios públicos', user['public_repos']), ('Seguidores', user['followers']), ('Estrelas (sem forks)', sum(r['stargazers_count'] for r in original)), ('Forks recebidos (sem forks)', sum(r['forks_count'] for r in original))]
    total = sum(languages.values())
    ranked = [(name, f'{100 * count / total:.1f}%') for name, count in languages.most_common(5)] if total else [('Sem linguagens detectadas', '—')]
    files = {}
    for theme in THEMES:
        streak_note = f'{first} a {last} · calendário GitHub · UTC'
        streak = streak_wide(theme, values, streak_note)
        streak_mobile = panel('GitHub Streak', theme, values, streak_note)
        statistics = panel('GitHub Statistics', theme, stats, 'Dados públicos · ' + stamp)
        langs = panel('Top Languages', theme, ranked, 'Bytes de código · sem forks · ' + today.isoformat())
        for name, content in [('streak', streak), ('streak-mobile', streak_mobile), ('statistics', statistics), ('languages', langs), ('overview', combined(statistics, langs)), ('overview-mobile', combined(statistics, langs, True))]:
            files[OUT / f'{name}-{theme}.svg'] = content + '\n'
    for path, content in files.items():
        temp = path.with_suffix('.tmp')
        temp.write_text(content, encoding='utf-8')
        temp.replace(path)

if __name__ == '__main__':
    main()

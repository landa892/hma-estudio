from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent


class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for name in ('href', 'src', 'poster'):
            value = attrs.get(name)
            if value:
                self.refs.append((tag, name, value))


missing = []
checked = 0
for html in ROOT.rglob('*.html'):
    if any(part.startswith('.') for part in html.relative_to(ROOT).parts):
        continue
    parser = Parser()
    parser.feed(html.read_text(encoding='utf-8'))
    for tag, attr, raw in parser.refs:
        if raw.startswith(('#', 'http:', 'https:', 'mailto:', 'tel:', 'data:', 'blob:', 'javascript:')):
            continue
        path = unquote(urlsplit(raw).path)
        if not path or path.startswith('/api/') or '{' in path:
            continue
        target = ROOT / path.lstrip('/') if path.startswith('/') else html.parent / path
        if path.endswith('/') or (not Path(path).suffix and target.is_dir()):
            target = target / 'index.html'
        elif not Path(path).suffix and target.with_suffix('.html').exists():
            target = target.with_suffix('.html')
        checked += 1
        if not target.exists():
            missing.append((str(html.relative_to(ROOT)), raw))

print('referencias locales:', checked)
if missing:
    print('faltantes:', len(missing))
    for item in missing[:100]:
        print('%s -> %s' % item)
    raise SystemExit(1)
print('sin enlaces ni archivos locales rotos')

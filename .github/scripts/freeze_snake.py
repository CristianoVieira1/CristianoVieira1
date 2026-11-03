"""Add a static alternative for readers who prefer reduced motion."""
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2] / 'assets'
for theme in ('dark', 'light'):
    source = ROOT / f'snake-{theme}.svg'
    tree = ET.parse(source)
    # snk SVG animations use CSS; this final stylesheet freezes their initial state.
    style = ET.SubElement(tree.getroot(), '{http://www.w3.org/2000/svg}style')
    style.text = '* { animation: none !important; transition: none !important; }'
    tree.write(ROOT / f'snake-static-{theme}.svg', encoding='unicode')

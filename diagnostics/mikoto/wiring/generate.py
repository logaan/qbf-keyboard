"""Generate the standalone HTML/SVG wiring guide from the fixture pin map."""
from pathlib import Path

channels = [
    ('Reset', 'P0.06', 'RESET / RST', 'reset / bootloader', '#b45309', 10),
    ('Key 1', 'P0.08', 'P0.08 · D1', 'F13', '#007d6e', 17),
    ('Key 2', 'P0.17', 'P0.17 · D2', 'F14', '#2563b8', 24),
    ('Key 3', 'P0.20', 'P0.20 · D3', 'F15', '#7c3aad', 31),
    ('Key 4', 'P0.22', 'P0.22 · D4', 'F16', '#b7315c', 38),
]
svg = ['''<svg viewBox="0 0 1160 660" role="img" aria-labelledby="overview-title overview-desc" xmlns="http://www.w3.org/2000/svg">
<title id="overview-title">Five transistor switches between SuperMini and Mikoto</title>
<desc id="overview-desc">Each SuperMini output feeds a 4.7 kilohm resistor into the base of a 2N3904. Its collector goes through 1 kilohm to a Mikoto input. Its emitter and a 100 kilohm base pull-down connect to common ground. Only ground is joined between the boards.</desc>
<rect width="1160" height="660" rx="20" fill="#f7f8f6"/>
<rect x="30" y="80" width="245" height="500" rx="16" fill="#e2f0eb" stroke="#bdcec5"/>
<rect x="895" y="80" width="235" height="500" rx="16" fill="#e6edf5" stroke="#c2cfde"/>
<text x="52" y="115" class="heading">SuperMini · helper</text><text x="914" y="115" class="heading">Mikoto · target</text>
<text x="53" y="49">USB data + power to laptop</text><text x="896" y="49">USB data + power to laptop</text>
<path d="M150 57V80M1000 57V80" stroke="#69777b" stroke-width="5"/>
<text x="365" y="97" class="small">BASE CURRENT LIMIT</text><text x="653" y="97" class="small">FAULT CURRENT LIMIT</text>
<path d="M805 158V614H1000V562M152 562V614H805" fill="none" stroke="#283639" stroke-width="4"/>
<text x="83" y="561">GND</text><text x="921" y="561">GND</text><text x="350" y="587" class="small">Wire crossings connect only where a dot is shown.</text><text x="443" y="643">Shared GND only · each board gets power from its own USB cable</text>
''']
for n, (name, helper, target, event, color, row) in enumerate(channels):
    y = 160 + n*80
    svg.append(f'''<g class="channel" data-channel="{n}" style="--wire:{color}">
<text x="51" y="{y+5}" class="pin">{helper}</text><text x="170" y="{y+5}" class="small">{name}</text>
<path d="M265 {y}H350 M410 {y}H510" class="wire" stroke="{color}"/>
<rect x="350" y="{y-9}" width="60" height="18" rx="3" fill="white" stroke="{color}" stroke-width="2"/>
<text x="359" y="{y-17}" class="small">4.7 kΩ</text>
<circle cx="485" cy="{y}" r="3" fill="{color}"/>
<path d="M485 {y}V{y+11}M485 {y+32}V{y+40}H805" fill="none" stroke="#536769" stroke-width="2"/>
<rect x="480" y="{y+11}" width="10" height="21" fill="white" stroke="#536769"/>
<text x="407" y="{y+32}" class="tiny">100 kΩ</text>
<circle cx="548" cy="{y}" r="25" fill="white" stroke="#45585d" stroke-width="1.5"/>
<path d="M510 {y}H540 M540 {y-16}V{y+16} M540 {y-8}L562 {y-23}H660 M540 {y+8}L562 {y+25}H805" fill="none" stroke="#283639" stroke-width="2"/>
<path d="M554 {y+12}L563 {y+26}L550 {y+21}Z" fill="#283639"/>
<text x="299" y="{y+44}" class="tiny">Q{n} · 2N3904</text>
<text x="521" y="{y-5}" class="tiny">B</text><text x="575" y="{y-27}" class="tiny">C</text><text x="575" y="{y+23}" class="tiny">E</text>
<circle cx="805" cy="{y+25}" r="3" fill="#283639"/><circle cx="805" cy="{y+40}" r="3" fill="#283639"/>
<rect x="660" y="{y-32}" width="60" height="18" rx="3" fill="white" stroke="{color}" stroke-width="2"/>
<text x="675" y="{y-40}" class="small">1 kΩ</text>
<path d="M720 {y-23}H895" class="wire" stroke="{color}"/>
<text x="914" y="{y-18}" class="pin">{target}</text><text x="914" y="{y+4}" class="tiny">{event}</text>
</g>''')
svg.append('</svg>')
rows = ''.join(f'<tr><td><span style="color:{color}">●</span> Q{n}: {name}</td><td>{helper}</td><td>{target}</td><td>{event}</td><td>b{row}, b{row+1}, b{row+2}</td></tr>' for n,(name,helper,target,event,color,row) in enumerate(channels))
holes = ''.join(f'''<tr><td>Q{n} · {name}</td><td>b{r}</td><td>b{r+1}</td><td>b{r+2}</td><td>e{r+1} ↔ g{r+1}</td><td>e{r+2} ↔ g{r+2}</td><td>a{r} ↔ a{r+1}</td><td>j{r+1}</td><td>j{r+2}</td><td>e{r} → GND</td></tr>''' for n,(name,helper,target,event,color,r) in enumerate(channels))
# A magnified, electrically accurate breadboard subsection for Q0.
mini = ['''<svg viewBox="0 0 1100 340" role="img" aria-labelledby="holes-title" xmlns="http://www.w3.org/2000/svg"><title id="holes-title">Reset circuit on breadboard rows 10, 11 and 12</title><rect width="1100" height="340" rx="16" fill="#f7f8f6"/>
<text x="40" y="40" class="heading">Q0 · breadboard detail</text><text x="40" y="66">Each numbered strip a–e is connected. f–j is a separate connected strip.</text>
<rect x="395" y="84" width="170" height="204" fill="#fff" stroke="#ddd"/><rect x="625" y="84" width="170" height="204" fill="#fff" stroke="#ddd"/>
<text x="565" y="311" class="small">CENTER GAP</text>''']
xs = [415,447,479,511,543,645,677,709,741,773]
for col,x in zip('abcdefghij',xs):
    mini.append(f'<text x="{x-4}" y="106">{col}</text>')
for row,y in [(10,145),(11,205),(12,265)]:
    mini.append(f'<text x="366" y="{y+5}">{row}</text><path d="M415 {y}H543M645 {y}H773" stroke="#d5deda" stroke-width="7"/>')
    for x in xs:
        mini.append(f'<circle cx="{x}" cy="{y}" r="5" fill="#fff" stroke="#7e8b87"/>')
mini.append('''<path d="M543 145H875V303H1040" fill="none" stroke="#283639" stroke-width="3"/>
<text x="885" y="322" class="small">to shared GND rail</text>
<path d="M543 205H677M773 205H880" fill="none" stroke="#b45309" stroke-width="3"/>
<rect x="566" y="197" width="53" height="16" fill="#eee3cc" stroke="#b45309"/><text x="569" y="186" class="small">4.7 kΩ</text>
<text x="888" y="210" class="pin">SuperMini P0.06</text>
<path d="M543 265H677M773 265H880" fill="none" stroke="#b45309" stroke-width="3"/>
<rect x="566" y="257" width="53" height="16" fill="#eee3cc" stroke="#b45309"/><text x="576" y="247" class="small">1 kΩ</text>
<text x="888" y="270" class="pin">Mikoto RESET</text>
<path d="M415 145V205" stroke="#536769" stroke-width="2"/><rect x="409" y="160" width="12" height="29" fill="#eee3cc" stroke="#536769"/>
<text x="307" y="183" class="small">100 kΩ</text>
<path d="M260 145H447M260 205H447M260 265H447" fill="none" stroke="#45585d" stroke-width="2"/>
<rect x="70" y="122" width="190" height="163" rx="12" fill="#283639"/>
<text x="92" y="151" fill="white">Emitter: b10</text><text x="92" y="211" fill="white">Base: b11</text><text x="92" y="271" fill="white">Collector: b12</text>
<text x="40" y="322" class="small">Transistor leads are spread to distinct rows. Verify E/B/C for your exact part.</text></svg>''')
html = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mikoto automated debugging · wiring guide</title><style>
:root{color-scheme:light;--ink:#21343a;--muted:#52666b}*{box-sizing:border-box}body{margin:0;background:#f0f3f0;color:var(--ink);font:16px/1.6 system-ui,-apple-system,sans-serif}main{max-width:1240px;margin:auto;padding:36px 30px 70px}h1{font-size:clamp(30px,4vw,50px);line-height:1.1;letter-spacing:-1.5px;margin:10px 0 18px}h2{font-size:24px;line-height:1.3;margin:34px 0 12px}p{max-width:90ch}.eyebrow{font-size:13px;letter-spacing:1.5px;text-transform:uppercase;color:#007d6e;font-weight:700}.lead{font-size:20px;color:var(--muted);max-width:75ch}.callout{background:#fff4dc;border-left:4px solid #b45309;padding:16px 22px;border-radius:8px}.card{background:#fff;border:1px solid #d7e0da;border-radius:18px;padding:22px;margin-top:22px}.diagram{overflow:auto}svg{width:100%;min-width:740px;display:block;font:16px system-ui,sans-serif}svg .heading{font-size:18px;font-weight:700}svg .small{font-size:12px}svg .tiny{font-size:11px}svg .pin{font-size:16px;font-weight:650}svg .wire{fill:none;stroke-width:3}.channel{transition:opacity .15s}svg[data-focused] .channel{opacity:.14}svg[data-focused] .channel.active{opacity:1}table{width:100%;border-collapse:collapse;font-size:14px;text-align:left}th{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;background:#f0f4f1}th,td{padding:12px 10px;border-bottom:1px solid #e0e7e1;white-space:nowrap}.table-scroll{overflow:auto}button{font:inherit;font-size:14px;padding:8px 13px;margin:0 5px 8px 0;border:1px solid #c0cec5;background:white;border-radius:8px;cursor:pointer}button[aria-pressed=true]{background:#213f39;color:white}.parts{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.parts div{padding:16px;background:#f0f4f1;border-radius:10px}.parts strong{display:block;font-size:21px}code{background:#eaf0ec;padding:2px 6px;border-radius:4px;font-size:.9em}a{color:#05675e}li{margin:8px 0}.muted{color:var(--muted);font-size:14px}footer{margin-top:35px;border-top:1px solid #cedbd0;padding-top:18px;color:var(--muted)}@media(max-width:650px){main{padding:24px 15px}.card{padding:15px}.parts{grid-template-columns:repeat(2,1fr)}}@media print{body{background:white}main{padding:0}.controls{display:none}.card{break-inside:avoid}svg{min-width:0}.channel{opacity:1!important}h1{font-size:30px}}
</style></head><body><main><div class="eyebrow">QBF · controller diagnostic fixture · 13 October 2026</div><h1>A virtual pair of hands<br>for your Mikoto.</h1><p class="lead">The SuperMini briefly connects reset and four keyboard inputs to ground. Your laptop sends the commands, copies firmware to the Mikoto and checks the resulting USB keyboard events.</p>
<div class="callout"><strong>Reset means connect to ground.</strong> Do not supply voltage to RESET. Both boards use their own USB cables. Connect GND between them; leave every power pin and the batteries disconnected from this fixture.</div>
<section class="card"><h2 style="margin-top:0">Five electronic switches</h2><p>The drawing shows the selected connections, not the physical positions of the controller pads. Find the matching printed GPIO labels on each board. A high SuperMini output turns its transistor on; the Mikoto sees a low input. The fixture itself sends no keyboard events.</p><div class="controls" role="group" aria-label="Highlight a connection"><button aria-pressed="true" data-select="all">All connections</button><button aria-pressed="false" data-select="0">Reset</button><button aria-pressed="false" data-select="1">Key 1</button><button aria-pressed="false" data-select="2">Key 2</button><button aria-pressed="false" data-select="3">Key 3</button><button aria-pressed="false" data-select="4">Key 4</button></div><div class="diagram">''' + ''.join(svg) + '''</div><p class="muted">B = base (control), C = collector (Mikoto side), E = emitter (ground). The 100 kΩ resistor connects B to E. Use onsemi 2N3904 TO-92 parts and confirm the lead numbers in their datasheet; the drawing is an electrical symbol.</p></section>
<h2>Parts to gather</h2><div class="parts"><div><strong>5 × 2N3904</strong>NPN transistors</div><div><strong>5 × 4.7 kΩ</strong>Base resistors</div><div><strong>5 × 100 kΩ</strong>Base pull-down resistors</div><div><strong>5 × 1 kΩ</strong>Collector resistors</div></div><p>Also: a breadboard with at least 45 numbered rows for the five switch circuits (a standard 830-point board is suitable), jumper wires, two USB <strong>data</strong> cables, and separate breadboard space or adapters for the controllers. Use ¼ W resistors. No keyboard diodes or external pull-up resistors are needed for these four independent inputs.</p>
<section class="card"><h2 style="margin-top:0">Which pins connect?</h2><div class="table-scroll"><table><thead><tr><th>Channel</th><th>SuperMini GPIO</th><th>Mikoto input</th><th>Expected result</th><th>Transistor E, B, C holes</th></tr></thead><tbody>''' + rows + '''</tbody></table></div><p>On the SuperMini, firmware refers to <code>board.P0_06</code>, etc. On the Mikoto, D1–D4 mean the Pro Micro connector names used by ZMK; follow the <strong>P0.xx labels</strong> for the physical wiring. Do not assume a pin has the same function just because it occupies the same position on both boards.</p></section>
<section class="card"><h2 style="margin-top:0">Repeat one circuit five times</h2><div class="diagram">''' + ''.join(mini) + '''</div><p>Orient the central breadboard with letters a–j across and increasing row numbers downward. Spread each transistor's leads along <strong>three separate rows</strong>, all in column b. Never put E, B and C in the same numbered a–e strip: that shorts them together. Bend the leads gently to fit; identify them first.</p><div class="table-scroll"><table><thead><tr><th>Channel</th><th>E</th><th>B</th><th>C</th><th>4.7 kΩ</th><th>1 kΩ</th><th>100 kΩ</th><th>SuperMini wire</th><th>Mikoto wire</th><th>Emitter jumper</th></tr></thead><tbody>''' + holes + '''</tbody></table></div><p>Join each emitter jumper to the same ground rail. Join a SuperMini GND and a Mikoto GND to that rail. If the rail is split halfway along the breadboard, bridge its two ground segments with a jumper and verify continuity. Leave the positive rail empty.</p></section>
<h2>Build and test in stages</h2><ol><li>Unplug USB and disconnect batteries. Inspect the Mikoto for solder bridges. Confirm that neither board's supply pins are connected to this fixture. A board that gets hot or trips USB power needs physical inspection before continuing.</li><li>Load the supplied CircuitPython UF2 and three Python files onto the SuperMini. This one-time step needs a double reset of the <em>SuperMini</em> itself. Check its bootloader version first; use the <a href="../README.md">setup guide</a>.</li><li>Build only Q0 first. Connect shared ground, plug both boards in, then run the bootloader command. Expect a <code>MIKOTO-BOOT</code> drive with the correct <code>INFO_UF2.TXT</code> Board-ID.</li><li>Install the matching Mikoto test UF2 using the laptop command. Unplug both USB cables, add Q1–Q4, recheck the circuit, then reconnect.</li><li>Run the automated HID test. It checks F13–F16 press <em>and release</em> events from the device named <code>Mikoto Test</code>. F keys can still trigger user-configured shortcuts; close applications that bind them.</li></ol>
<div class="callout"><strong>This tests direct keys.</strong> Each key input has a firmware pull-up and is independently pulled to ground. This wiring does not close switches between scanned matrix rows and columns. A full matrix needs a different switching arrangement.</div>
<h2>What the result tells you</h2><p>If UF2 mode works, the target can run its bootloader and communicate over USB. If all four HID tests pass, those four GPIO/header paths and USB keyboard reporting work under this test. A failure can still be caused by a wire, resistor, transistor, wrong firmware revision, host permission or the Mikoto itself. Bluetooth, charging and untested pins are separate tests.</p>
<footer><p><a href="../README.md">Firmware and laptop setup</a> · <a href="../RESEARCH.md">Research and diagnostic limits</a> · <button onclick="window.print()">Print guide</button></p><p class="muted">Primary references: <a href="https://keebd.com/products/mikoto-controller">KEEBD Mikoto</a>, <a href="https://keebd.com/products/supermini-controller">KEEBD SuperMini</a>, <a href="https://github.com/adafruit/Adafruit_nRF52_Bootloader">Adafruit bootloader</a>, <a href="https://circuitpython.org/board/supermini_nrf52840/">SuperMini CircuitPython</a>, <a href="https://www.onsemi.com/pdf/datasheet/2n3904-d.pdf">2N3904 lead numbering</a>, <a href="https://github.com/zmkfirmware/zmk/tree/main/app/module/boards/zhiayang/mikoto">ZMK Mikoto definitions</a>.</p></footer></main><script>
const overview=document.querySelector('svg');document.querySelectorAll('[data-select]').forEach(button=>button.addEventListener('click',()=>{const choice=button.dataset.select;document.querySelectorAll('[data-select]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));overview.toggleAttribute('data-focused',choice!=='all');overview.querySelectorAll('.channel').forEach(g=>g.classList.toggle('active',g.dataset.channel===choice));}));
</script></body></html>'''
Path(__file__).with_name('index.html').write_text(html)

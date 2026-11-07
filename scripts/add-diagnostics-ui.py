from pathlib import Path
import json
r = Path(__file__).resolve().parents[1] / 'source/apps/iyt_app'
p = r / 'app.json'
a = json.loads(p.read_text())
a['screens'][1]['items'].append(['button', 'BTN_DIAG', 'Diagnostics'])
a['screens'].append({'name': 'DIAG', 'kind': 'menu', 'title': 'RideTube diagnostics', 'items': [
    ['text', 'DIAG_STATUS', 'Choose Refresh to read current status'],
    ['button', 'BTN_DIAG_REFRESH', 'Refresh'], ['button', 'BTN_DIAG_BACK', 'Back']]})
p.write_text(json.dumps(a, indent=2) + '\n')
p = r / 'main.js'
t = p.read_text().replace("        ctl.on('msg', (m) => {", """        ctl.on('msg', (m) => {
            if (m.ev === 'diagnostics') {
                const mb = m.memory ? Math.round(m.memory.rss / 1048576) : null;
                ui.text('DIAG_STATUS', 'RideTube ' + m.version + ' | ' + m.node +
                    ' | GPU: ' + m.gpuDevice + ' | acceleration: ' + m.hardwareAcceleration +
                    ' | memory: ' + (mb === null ? 'unavailable' : mb + ' MiB') +
                    ' | output: iDrive | cluster: simulator only' +
                    (m.lastError ? ' | ' + m.lastError.code + ': ' + m.lastError.message : ''));
                return;
            }""")
t = t.replace("        ui.onClick('BTN_SEARCH',", """        ui.onClick('BTN_DIAG', () => { ui.open('DIAG'); ctl.send({cmd: 'diagnostics'}); });
        ui.onClick('BTN_DIAG_REFRESH', () => ctl.send({cmd: 'diagnostics'}));
        ui.onClick('BTN_DIAG_BACK', () => ui.open('MAIN'));
        ui.onClick('BTN_SEARCH',""", 1)
p.write_text(t)
print('Native diagnostics menu added with real process measurements.')

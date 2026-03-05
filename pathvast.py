import re

NETWORK_CODE = '21625262017'
PREFIX = f'https://pubads.g.doubleclick.net/gampad/ads?iu=/{NETWORK_CODE},'
SUFFIX = {
    'ios':     '/mobile_ios&description_url=[placeholder]&tfcd=0&npa=0&sz=640x480&pp=ios&gdfp_req=1&output=vast&env=vp&unviewed_position_start=1&impl=s&correlator=&plcmt=PLCMT&vpmute=VPMUTE&wta=1&vpa=VPA',
    'android': '/mobile_android&description_url=[placeholder]&tfcd=0&npa=0&sz=640x480&pp=android&gdfp_req=1&output=vast&env=vp&unviewed_position_start=1&impl=s&correlator=&plcmt=PLCMT&vpmute=VPMUTE&wta=1&vpa=VPA',
    'desktop': '/desktop&description_url=[placeholder]&tfcd=0&npa=0&sz=640x480&pp=desktop&gdfp_req=1&output=vast&env=vp&unviewed_position_start=1&impl=s&correlator=&plcmt=PLCMT&vpmute=VPMUTE&wta=1&vpa=VPA',
    'mobile':  '/mobile&description_url=[placeholder]&tfcd=0&npa=0&sz=640x480&pp=mobile&gdfp_req=1&output=vast&env=vp&unviewed_position_start=1&impl=s&correlator=&plcmt=PLCMT&vpmute=VPMUTE&wta=1&vpa=VPA',
}


def get_pathvast_blocks():
    return [
        {'type': 'section', 'text': {'type': 'mrkdwn', 'text': 'Genera *Ad Unit Path* o *VAST URL*.\nPuoi inserire più righe — MCM e Ad Unit devono avere lo stesso numero di righe.'}},
        {'type': 'divider'},
        {'type': 'input', 'block_id': 'type_block', 'label': {'type': 'plain_text', 'text': 'Tipo di output'},
         'element': {'type': 'static_select', 'action_id': 'type_input', 'placeholder': {'type': 'plain_text', 'text': 'Seleziona tipo'},
                     'options': [{'text': {'type': 'plain_text', 'text': '🔗 Path'}, 'value': 'path'},
                                 {'text': {'type': 'plain_text', 'text': '📹 VAST URL'}, 'value': 'vast'}]}},
        {'type': 'input', 'block_id': 'mcm_block', 'label': {'type': 'plain_text', 'text': 'MCM (uno per riga)'},
         'element': {'type': 'plain_text_input', 'action_id': 'mcm_input', 'multiline': True, 'placeholder': {'type': 'plain_text', 'text': 'es. 21625262017'}}},
        {'type': 'input', 'block_id': 'adunit1_block', 'label': {'type': 'plain_text', 'text': 'Ad Unit 1 — Publisher'},
         'element': {'type': 'plain_text_input', 'action_id': 'adunit1_input', 'multiline': True, 'placeholder': {'type': 'plain_text', 'text': 'es. nextmediaweb365'}}},
        {'type': 'input', 'block_id': 'adunit2_block', 'optional': True, 'label': {'type': 'plain_text', 'text': 'Ad Unit 2 — Domain'},
         'element': {'type': 'plain_text_input', 'action_id': 'adunit2_input', 'multiline': True, 'placeholder': {'type': 'plain_text', 'text': 'es. corriere.it'}}},
        {'type': 'input', 'block_id': 'adunit3_block', 'optional': True, 'label': {'type': 'plain_text', 'text': 'Ad Unit 3 — Formato'},
         'element': {'type': 'plain_text_input', 'action_id': 'adunit3_input', 'multiline': True, 'placeholder': {'type': 'plain_text', 'text': 'es. preroll'}}},
        {'type': 'divider'},
        {'type': 'section', 'text': {'type': 'mrkdwn', 'text': '*Parametri VAST* — solo se hai selezionato "VAST URL"'}},
        {'type': 'input', 'block_id': 'device_block', 'optional': True, 'label': {'type': 'plain_text', 'text': 'Device Type'},
         'element': {'type': 'static_select', 'action_id': 'device_input', 'placeholder': {'type': 'plain_text', 'text': 'Seleziona device'},
                     'options': [{'text': {'type': 'plain_text', 'text': t}, 'value': v} for t, v in [('iOS','ios'),('Android','android'),('Desktop','desktop'),('Mobile generico','mobile')]]}},
        {'type': 'input', 'block_id': 'plcmt_block', 'optional': True, 'label': {'type': 'plain_text', 'text': 'plcmt'},
         'element': {'type': 'plain_text_input', 'action_id': 'plcmt_input', 'placeholder': {'type': 'plain_text', 'text': 'es. 1'}}},
        {'type': 'input', 'block_id': 'vpmute_block', 'optional': True, 'label': {'type': 'plain_text', 'text': 'vpmute'},
         'element': {'type': 'static_select', 'action_id': 'vpmute_input', 'placeholder': {'type': 'plain_text', 'text': 'Seleziona'},
                     'options': [{'text': {'type': 'plain_text', 'text': '0 — audio on'}, 'value': '0'}, {'text': {'type': 'plain_text', 'text': '1 — muted'}, 'value': '1'}]}},
        {'type': 'input', 'block_id': 'vpa_block', 'optional': True, 'label': {'type': 'plain_text', 'text': 'vpa'},
         'element': {'type': 'static_select', 'action_id': 'vpa_input', 'placeholder': {'type': 'plain_text', 'text': 'Seleziona'},
                     'options': [{'text': {'type': 'plain_text', 'text': 'auto'}, 'value': 'auto'}, {'text': {'type': 'plain_text', 'text': 'click'}, 'value': 'click'}]}},
    ]


def generate_pathvast_output(values):
    out_type = values['type_block']['type_input']['selected_option']['value']
    mcms     = split_lines(values['mcm_block']['mcm_input']['value'] or '')
    u1s      = split_lines(values['adunit1_block']['adunit1_input']['value'] or '')
    u2s      = split_lines((values.get('adunit2_block') or {}).get('adunit2_input', {}).get('value') or '')
    u3s      = split_lines((values.get('adunit3_block') or {}).get('adunit3_input', {}).get('value') or '')

    if not mcms: raise Exception('Inserisci almeno un MCM.')
    if not u1s:  raise Exception('Inserisci almeno un Ad Unit 1.')

    n = max(len(mcms), len(u1s), len(u2s) or 0, len(u3s) or 0)

    if out_type == 'path':
        return generate_paths(mcms, u1s, u2s, u3s, n)

    device = ((values.get('device_block') or {}).get('device_input') or {}).get('selected_option', {}).get('value', 'mobile')
    plcmt  = ((values.get('plcmt_block')  or {}).get('plcmt_input')  or {}).get('value', '1')
    vpmute = (((values.get('vpmute_block') or {}).get('vpmute_input') or {}).get('selected_option') or {}).get('value', '0')
    vpa    = (((values.get('vpa_block')    or {}).get('vpa_input')    or {}).get('selected_option') or {}).get('value', 'auto')

    return generate_vast(mcms, u1s, u2s, u3s, n, device, plcmt, vpmute, vpa)


def generate_paths(mcms, u1s, u2s, u3s, n):
    lines = []
    for i in range(n):
        mcm = mcms[min(i, len(mcms)-1)]
        u1  = u1s[min(i, len(u1s)-1)]
        u2  = u2s[min(i, len(u2s)-1)] if u2s else ''
        u3  = u3s[min(i, len(u3s)-1)] if u3s else ''
        parts = [f'/{mcm}'] + [x for x in [u1, u2, u3] if x]
        lines.append('/'.join(parts))
    return '\n'.join(lines)


def generate_vast(mcms, u1s, u2s, u3s, n, device, plcmt, vpmute, vpa):
    suffix = SUFFIX.get(device, SUFFIX['mobile'])
    lines  = []
    for i in range(n):
        mcm  = mcms[min(i, len(mcms)-1)]
        u1   = u1s[min(i, len(u1s)-1)]
        u2   = u2s[min(i, len(u2s)-1)] if u2s else ''
        u3   = u3s[min(i, len(u3s)-1)] if u3s else ''
        path = '/'.join([x for x in [u1, u2, u3] if x])
        url  = PREFIX + path + suffix.replace('PLCMT', plcmt).replace('VPMUTE', vpmute).replace('VPA', vpa)
        lines.append(url)
    return '\n'.join(lines)


def split_lines(text):
    return [s.strip() for s in re.split(r'[\n,\t]', text) if s.strip()]

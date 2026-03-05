import re

FORMATS = [
    'display','page-multiplier','interstitial+desktop','interstitial3',
    'interstitial2+desktop2','interstitial+interstitial2','2page','back',
    'masthead','articles','article-middles','spalla-middles','footer',
    'article-top','article-middle','article-bottom','spalla-top',
    'spalla-middle','spalla-bottom','skyscraper-left','skyscraper-right',
    'header','leaderboard','article-fluid-1','article-fluid-2',
    'interstitial0+interstitial2','interstitial_desktop+interstitial_desktop2',
    'interstitial0_desktop+interstitial_desktop2','interstitials','interstitials0',
    'preroll','preroll_pushdown','preroll_verticale','preroll_big',
    'preroll_c2p','preroll_intext','preroll_intext_audio_on','preroll_pushdown_audio_on'
]

FORMAT_MAP = {
    'display': ['footer','article-top','article-middle','article-bottom','spalla-top','spalla-middle','spalla-bottom','skyscraper-left','skyscraper-right','header','masthead','leaderboard','article-fluid-1','article-fluid-2'],
    'interstitial+desktop': ['interstitial','interstitial_desktop'],
    'interstitial3': ['interstitial3'],
    'page-multiplier': ['page-multiplier'],
    'articles': [f'article-{i}' for i in range(1,13)],
    'article-middles': [f'article-middle-{i}' for i in range(2,11)],
    'spalla-middles': [f'spalla-middle-{i}' for i in range(2,11)],
    'interstitial2+desktop2': ['interstitial2','interstitial_desktop2'],
    'interstitial+interstitial2': ['interstitial','interstitial2'],
    '2page': ['2page'], 'back': ['back'], 'masthead': ['masthead'],
    'interstitial0+interstitial2': ['interstitial0','interstitial2'],
    'interstitial_desktop+interstitial_desktop2': ['interstitial_desktop','interstitial_desktop2'],
    'interstitial0_desktop+interstitial_desktop2': ['interstitial0_desktop','interstitial_desktop2'],
    'interstitials': ['interstitial','interstitial2','interstitial_desktop','interstitial_desktop2'],
    'interstitials0': ['interstitial0','interstitial2','interstitial0_desktop','interstitial_desktop2'],
}

ENV_MAP = {
    'web': [''], 'amp': ['_amp'], 'web + amp': ['', '_amp'], 'app': ['_app']
}

AMP_OK = (
    {'interstitial','interstitial0','interstitial2','interstitial3','interstitial_desktop',
          'interstitial_desktop2','2page','back','footer','masthead','page-multiplier',
          'article-top','article-middle','article-bottom','spalla-top','spalla-middle','spalla-bottom',
     'skyscraper-left','skyscraper-right','header','article-fluid1','article-fluid2'}
    |
     {f'article-middle-{i}' for i in range(2,11)}
    | {f'spalla-middle-{i}' for i in range(2,11)}
    | {f'article-{i}' for i in range(1,13)}
)

PUBLISHER_MAP = {
    'nextmediaweb365': 'thecore', 'adgage_summonpress': 'adgage_talamoh',
    'metricsmonster': 'cognitive', 'tcec': 'tc&c',
    'adgage_globalmediagroup': 'adgage_grupomediosglobal',
    'dunkest': 'fantakinginteractive', 'hvdd': 'hovogliadidolce',
    'adgage_globalmediagroup_pt': 'adgage_globalmediagroup'
}

SIZE_MAP = {
    'footer': '300x50;300x75;300x100;320x50;320x90;320x100;728x90;970x50;970x90;980x50;980x90;1280x100;Fluid',
    'masthead': '728x90;970x90;980x90;1200x90;970x250;980x250;980x251;1200x250',
    'page-multiplier': '300x250;320x50',
    'article-fluid-1': '300x250;336x280;728x90;728x250;Fluid',
    'article-fluid-2': '300x250;336x280;728x90;728x250;Fluid',
    'article-top': '300x50;300x75;300x100;300x250;320x50;320x90;320x100;336x280;728x90;580x400;468x60;Fluid',
    'article-middle': '300x50;300x75;300x100;300x250;320x50;320x90;320x100;336x280;580x400;468x60;Fluid;300x600;728x90;980x90;970x250;980x250;1200x250;1200x90;980x251;970x90',
    'article-bottom': '300x50;300x75;300x100;300x250;320x50;320x90;320x100;336x280;728x90;580x400;468x60;Fluid',
    'interstitial': '320x480;336x280;300x600;360x540;360x600;412x600;300x250',
    'interstitial0': '320x480;336x280;300x600;360x540;360x600;412x600;300x250',
    'interstitial2': '320x480;336x280;300x600;360x540;360x600;412x600;300x250',
    'interstitial3': '320x480;336x280;300x600;360x540;360x600;412x600;300x250',
    'interstitial_desktop': 'Fluid;320x480;300x600;1800x100;640x960;800x600;1024x768;970x250',
    'interstitial0_desktop': 'Fluid;320x480;300x600;1800x100;640x960;800x600;1024x768;970x250',
    'interstitial_desktop2': 'Fluid;320x480;300x600;1800x100;640x960;800x600;1024x768;970x250',
    '2page': '300x250;320x480;336x280',
    'back': '300x250;300x600;320x480;336x280;360x540;360x600;412x600',
    'spalla-top': '300x250;300x600', 'spalla-middle': '300x250;300x600', 'spalla-bottom': '300x250;300x600',
    'skyscraper-left': '160x600;120x600', 'skyscraper-right': '160x600;120x600',
    'preroll': '640x480v', 'preroll_pushdown': '640x480v', 'preroll_verticale': '720x1280v',
    'preroll_big': '640x480v', 'preroll_c2p': '640x480v', 'preroll_intext': '640x480v',
    'preroll_intext_audio_on': '640x480v', 'preroll_pushdown_audio_on': '640x480v',
    'header': '300x50;300x75;300x100;320x50;320x90;320x100;728x90;1280x100',
    'leaderboard': '320x50;320x100;728x90;728x250;970x250'
}

DISPLAY_FMTS = {'article-top','leaderboard','article-middle','article-bottom','spalla-top',
                'spalla-middle','spalla-bottom','skyscraper-left','skyscraper-right',
                'article-fluid-1','article-fluid-2','masthead'}


def get_adunit_blocks():
    format_options = [{'text': {'type': 'plain_text', 'text': f}, 'value': f} for f in FORMATS]
    return [
        {'type': 'section', 'text': {'type': 'mrkdwn', 'text': 'Inserisci i dati per generare il *CSV di bulk creation* su GAM.\nPuoi inserire più publisher/domain (uno per riga) — devono corrispondere in numero.'}},
        {'type': 'divider'},
        {'type': 'input', 'block_id': 'publisher_block', 'label': {'type': 'plain_text', 'text': 'Publisher (uno per riga)'},
         'element': {'type': 'plain_text_input', 'action_id': 'publisher_input', 'multiline': True, 'placeholder': {'type': 'plain_text', 'text': 'es.\nnextmediaweb365\nadgage_summonpress'}}},
        {'type': 'input', 'block_id': 'domain_block', 'label': {'type': 'plain_text', 'text': 'Domain (stesso ordine del publisher)'},
         'element': {'type': 'plain_text_input', 'action_id': 'domain_input', 'multiline': True, 'placeholder': {'type': 'plain_text', 'text': 'es.\ncorriere.it\nrepubblica.it'}}},
        {'type': 'input', 'block_id': 'format_block', 'label': {'type': 'plain_text', 'text': 'Formato'},
         'element': {'type': 'static_select', 'action_id': 'format_input', 'placeholder': {'type': 'plain_text', 'text': 'Seleziona formato'}, 'options': format_options}},
        {'type': 'input', 'block_id': 'environment_block', 'label': {'type': 'plain_text', 'text': 'Environment'},
         'element': {'type': 'static_select', 'action_id': 'environment_input', 'placeholder': {'type': 'plain_text', 'text': 'Seleziona environment'},
                     'options': [{'text': {'type': 'plain_text', 'text': t}, 'value': v} for t, v in [('Web','web'),('AMP','amp'),('Web + AMP','web + amp'),('App','app')]]}},
        {'type': 'input', 'block_id': 'exists_block', 'optional': True, 'label': {'type': 'plain_text', 'text': 'Stato publisher/domain in GAM'},
         'element': {'type': 'checkboxes', 'action_id': 'exists_input', 'options': [
             {'text': {'type': 'plain_text', 'text': 'Publisher già esiste'}, 'value': 'publisher_exists'},
             {'text': {'type': 'plain_text', 'text': 'Domain già esiste'}, 'value': 'domain_exists'}]}},
        {'type': 'input', 'block_id': 'split_block', 'optional': True, 'label': {'type': 'plain_text', 'text': 'OS Split (solo preroll)'},
         'element': {'type': 'checkboxes', 'action_id': 'split_input', 'options': [
             {'text': {'type': 'plain_text', 'text': 'OS Split (mobile_ios / mobile_android / desktop)'}, 'value': 'os_split'},
             {'text': {'type': 'plain_text', 'text': 'OS App Split (ios / android)'}, 'value': 'os_app_split'}]}},
        {'type': 'divider'},
        {'type': 'input', 'block_id': 'tier_block', 'optional': True, 'label': {'type': 'plain_text', 'text': 'Tier Placement'},
         'element': {'type': 'plain_text_input', 'action_id': 'tier_input', 'placeholder': {'type': 'plain_text', 'text': 'es. editori - tier 1'}}},
        {'type': 'input', 'block_id': 'region_block', 'optional': True, 'label': {'type': 'plain_text', 'text': 'Region Placement'},
         'element': {'type': 'plain_text_input', 'action_id': 'region_input', 'placeholder': {'type': 'plain_text', 'text': 'es. Region Italy'}}},
        {'type': 'input', 'block_id': 'tam_block', 'optional': True, 'label': {'type': 'plain_text', 'text': 'TAM Placement'},
         'element': {'type': 'plain_text_input', 'action_id': 'tam_input', 'placeholder': {'type': 'plain_text', 'text': 'es. TAM Italia'}}},
        {'type': 'input', 'block_id': 'pam_block', 'optional': True, 'label': {'type': 'plain_text', 'text': 'PAM Placement'},
         'element': {'type': 'plain_text_input', 'action_id': 'pam_input', 'placeholder': {'type': 'plain_text', 'text': 'es. PAM Italia'}}},
    ]


def generate_adunit_csv(values):
    publishers = split_lines(values['publisher_block']['publisher_input']['value'] or '')
    domains    = split_lines(values['domain_block']['domain_input']['value'] or '')
    fmt        = values['format_block']['format_input']['selected_option']['value']
    env        = values['environment_block']['environment_input']['selected_option']['value']

    exists_sel = [o['value'] for o in (values.get('exists_block', {}).get('exists_input', {}).get('selected_options') or [])]
    split_sel  = [o['value'] for o in (values.get('split_block',  {}).get('split_input',  {}).get('selected_options') or [])]

    tier   = (values.get('tier_block',   {}).get('tier_input',   {}).get('value') or '').strip()
    region = (values.get('region_block', {}).get('region_input', {}).get('value') or '').strip()
    tam    = (values.get('tam_block',    {}).get('tam_input',    {}).get('value') or '').strip()
    pam    = (values.get('pam_block',    {}).get('pam_input',    {}).get('value') or '').strip()

    if not publishers: raise Exception('Inserisci almeno un publisher.')
    if not domains:    raise Exception('Inserisci almeno un domain.')
    if len(publishers) != len(domains):
        raise Exception(f'Publisher ({len(publishers)}) e domain ({len(domains)}) non corrispondono.')

    csv = '#Code,Name,Sizes:,Description,Placements,Target window,Teams,Labels,Special ad unit\n'
    for i, pub in enumerate(publishers):
        pub = pub.lower()
        dom = domains[i].lower()
        fd  = {
            'publisher': pub, 'domain': dom, 'format': fmt, 'environment': env,
            'publisherExists': 'yes' if 'publisher_exists' in exists_sel else 'no',
            'domainExists':    'yes' if 'domain_exists'    in exists_sel else 'no',
            'osSplit':         'yes' if 'os_split'         in split_sel  else 'no',
            'osAppSplit':      'yes' if 'os_app_split'     in split_sel  else 'no',
            'tierPlacement': tier, 'regionPlacement': region, 'tamPlacement': tam, 'pamPlacement': pam
        }
        if fd['publisherExists'] == 'no' and fd['domainExists'] == 'yes':
            raise Exception('Cannot create ad unit 2 if ad unit 1 does not exist')
        csv += generate_rows(fd)
    return csv


def generate_rows(fd):
    pub  = fd['publisher']
    dom  = fd['domain']
    fmts = FORMAT_MAP.get(fd['format'], [fd['format']])
    envs = ENV_MAP.get(fd['environment'], [''])
    rows = ''

    if fd['publisherExists'] == 'no':
        pub_pl = 'AdGage' if 'adgage' in pub else ''
        rows += f"{pub},{pub[0].upper()+pub[1:]},1x1,,{pub_pl},,,,no\n"
        for env in envs:
            rows += f"{pub}/{dom}{env},{dom}{env},1x1,,,,,,no\n"
    elif fd['domainExists'] == 'no':
        for env in envs:
            rows += f"{pub}/{dom}{env},{dom}{env},1x1,,,,,,no\n"

    for fmt in fmts:
        for env in envs:
            if env == '_amp' and fmt not in AMP_OK:
                continue
            pl = get_placement(fmt, pub)
            extra = [x for x in [fd['tierPlacement'], fd['regionPlacement'], fd['tamPlacement'], fd['pamPlacement']] if x]
            if extra:
                pl = (pl + ';' if pl else '') + ';'.join(extra)
            size = get_size(fmt)
            rows += f"{pub}/{dom}{env}/{fmt},{fmt},{size},,{pl},,,,no\n"

            if 'preroll' in fmt:
                for dev in get_devices(fmt, fd['osSplit'], fd['osAppSplit'], fd['environment']):
                    rows += f"{pub}/{dom}{env}/{fmt}/{dev},{dev},{size},,,,,,no\n"
            if fd['environment'] == 'app' and fd['osAppSplit'] == 'yes':
                for dev in ['ios', 'android']:
                    rows += f"{pub}/{dom}{env}/{fmt}/{dev},{dev},{size},,,,,,no\n"
    return rows


def get_placement(fmt, pub):
    base = ''
    if fmt == 'preroll_verticale':       base = 'impact'
    elif fmt in ('interstitial', 'interstitial0'):  base = 'interstitial'
    elif fmt in ('interstitial_desktop', 'interstitial0_desktop'): base = 'interstitial_desktop'
    elif fmt == 'interstitial_desktop2': base = 'interstitial_desktop2'
    elif fmt == 'interstitial2':         base = 'interstitial2'
    elif fmt == 'interstitial3':         base = 'interstitial3'
    elif fmt == '2page':                 base = '2page'
    elif fmt == 'back':                  base = 'back'
    elif fmt in DISPLAY_FMTS or re.match(r'^(article|spalla)-middle-\d+$', fmt) or re.match(r'^article-\d+$', fmt): base = 'display'
    elif fmt == 'page-multiplier':       base = 'page-multiplier'
    elif fmt in ('footer', 'header'):    base = 'display_anchored'
    elif 'preroll' in fmt:               base = 'video'

    final_pub = PUBLISHER_MAP.get(pub, pub)
    if fmt == 'preroll_verticale': return base or 'impact'
    return f'{base} - {final_pub}' if base else ''


def get_devices(fmt, os_split, os_app_split, env):
    if fmt == 'preroll_verticale': return ['mobile_ios', 'mobile_android']
    if os_split == 'yes':          return ['mobile_ios', 'mobile_android', 'desktop']
    if os_app_split == 'yes' and env == 'app': return ['ios', 'android']
    return ['mobile', 'desktop']


def get_size(fmt):
    if re.match(r'^article-middle-\d+$', fmt): return SIZE_MAP['article-middle']
    if re.match(r'^spalla-middle-\d+$',  fmt): return '300x600;300x250'
    if re.match(r'^article-\d+$',        fmt): return SIZE_MAP['article-top']
    return SIZE_MAP.get(fmt, '')


def split_lines(text):
    import re
    return [s.strip() for s in re.split(r'[\n,\t]', text) if s.strip()]

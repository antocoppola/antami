import re


def get_bulkupload_blocks():
    return [
        {'type': 'section', 'text': {'type': 'mrkdwn', 'text': 'Genera il *CSV domain/MCM* per il bulk upload dei siti su GAM.\nDomain e MCM devono avere lo stesso numero di righe.'}},
        {'type': 'divider'},
        {'type': 'input', 'block_id': 'domain_block', 'label': {'type': 'plain_text', 'text': 'Domain (uno per riga)'},
         'element': {'type': 'plain_text_input', 'action_id': 'domain_input', 'multiline': True,
                     'placeholder': {'type': 'plain_text', 'text': 'es.\ncorriere.it\nrepubblica.it'}}},
        {'type': 'input', 'block_id': 'mcm_block', 'label': {'type': 'plain_text', 'text': 'MCM (stesso ordine dei domain)'},
         'element': {'type': 'plain_text_input', 'action_id': 'mcm_input', 'multiline': True,
                     'placeholder': {'type': 'plain_text', 'text': 'es.\n21625262017\n21625262018'}}},
    ]


def generate_bulkupload_csv(values):
    domains = split_lines(values['domain_block']['domain_input']['value'] or '')
    mcms    = split_lines(values['mcm_block']['mcm_input']['value'] or '')

    if not domains: raise Exception('Inserisci almeno un domain.')
    if not mcms:    raise Exception('Inserisci almeno un MCM.')
    if len(domains) != len(mcms):
        raise Exception(f'Domain ({len(domains)}) e MCM ({len(mcms)}) non corrispondono.')

    return '\n'.join(f'{d},{m}' for d, m in zip(domains, mcms))


def split_lines(text):
    return [s.strip() for s in re.split(r'[\n,\t]', text) if s.strip()]

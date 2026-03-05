import functions_framework
import json
import requests
import os
from datetime import datetime
from adunit import get_adunit_blocks, generate_adunit_csv
from pathvast import get_pathvast_blocks, generate_pathvast_output
from bulkupload import get_bulkupload_blocks, generate_bulkupload_csv

SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')


# ============================================================
# ENTRY POINT
# ============================================================
@functions_framework.http
def main(request):
    if request.method == 'GET':
        return 'OK', 200

    if request.method != 'POST':
        return 'Method Not Allowed', 405

    content_type = request.content_type or ''

    # Slack Interactions (modal submit)
    if 'application/x-www-form-urlencoded' in content_type:
        body = request.get_data(as_text=True)
        if body.startswith('payload='):
            from urllib.parse import unquote_plus
            payload = json.loads(unquote_plus(body[len('payload='):]))
            return handle_interaction(payload)

        # Slash Command
        params = request.form
        if params.get('command'):
            return handle_slash_command(params)

    return json.dumps({'ok': True}), 200, {'Content-Type': 'application/json'}


# ============================================================
# SLASH COMMAND → apre Step 1
# ============================================================
def handle_slash_command(params):
    trigger_id  = params.get('trigger_id')
    channel_id  = params.get('channel_id')
    user_id     = params.get('user_id')
    response_url = params.get('response_url')

    open_step1_modal(trigger_id, channel_id, user_id, response_url)

    # Risposta vuota immediata (Slack vuole risposta entro 3 sec)
    return '', 200


# ============================================================
# INTERACTIONS ROUTER
# ============================================================
def handle_interaction(payload):
    if payload.get('type') == 'view_submission':
        return handle_view_submission(payload)
    return json.dumps({'ok': True}), 200, {'Content-Type': 'application/json'}


def handle_view_submission(payload):
    callback_id = payload['view']['callback_id']
    values      = payload['view']['state']['values']
    user_id     = payload['user']['id']

    try:
        meta = json.loads(payload['view'].get('private_metadata') or '{}')
    except Exception:
        meta = {}

    channel_id   = meta.get('channel_id')
    response_url = meta.get('response_url')

    try:
        if callback_id == 'step1_adunit':
            return handle_step1(values, user_id, channel_id, response_url)
        if callback_id == 'step2_pathvast':
            return handle_step2(values, user_id, channel_id, response_url)
        if callback_id == 'step3_bulkupload':
            return handle_step3(values, user_id, channel_id, response_url)
    except Exception as e:
        return json.dumps({
            'response_action': 'errors',
            'errors': {'publisher_block': '❌ ' + str(e)}
        }), 200, {'Content-Type': 'application/json'}

    return json.dumps({'response_action': 'clear'}), 200, {'Content-Type': 'application/json'}


# ============================================================
# STEP 1 — AD UNIT BUILDER
# ============================================================
def open_step1_modal(trigger_id, channel_id, user_id, response_url):
    call_slack_api('views.open', {
        'trigger_id': trigger_id,
        'view': build_step1_view(channel_id, user_id, response_url)
    })


def handle_step1(values, user_id, channel_id, response_url):
    csv_content = generate_adunit_csv(values)
    filename    = 'adunit_bulk_' + get_timestamp() + '.csv'
    target      = channel_id or get_dm_channel(user_id)

    upload_file(target, user_id, filename, csv_content,
                'Ad Unit Builder CSV',
                f'✅ *[1/3] Ad Unit Builder* — file generato da <@{user_id}>')

    next_meta = json.dumps({'channel_id': channel_id, 'user_id': user_id, 'response_url': response_url})
    return json.dumps({
        'response_action': 'update',
        'view': build_step2_view(next_meta)
    }), 200, {'Content-Type': 'application/json'}


# ============================================================
# STEP 2 — PATH/VAST BUILDER
# ============================================================
def handle_step2(values, user_id, channel_id, response_url):
    output   = generate_pathvast_output(values)
    out_type = values['type_block']['type_input']['selected_option']['value']
    filename = ('paths_' if out_type == 'path' else 'vast_urls_') + get_timestamp() + '.csv'
    target   = channel_id or get_dm_channel(user_id)
    label    = 'Path Builder' if out_type == 'path' else 'VAST Builder'

    upload_file(target, user_id, filename, output, filename,
                f'✅ *[2/3] {label}* — file generato da <@{user_id}>')

    next_meta = json.dumps({'channel_id': channel_id, 'user_id': user_id, 'response_url': response_url})
    return json.dumps({
        'response_action': 'update',
        'view': build_step3_view(next_meta)
    }), 200, {'Content-Type': 'application/json'}


# ============================================================
# STEP 3 — BULK UPLOAD SITES
# ============================================================
def handle_step3(values, user_id, channel_id, response_url):
    csv_content = generate_bulkupload_csv(values)
    filename    = 'domain_mcm_' + get_timestamp() + '.csv'
    target      = channel_id or get_dm_channel(user_id)

    upload_file(target, user_id, filename, csv_content, filename,
                f'✅ *[3/3] Bulk Upload Sites* — file generato da <@{user_id}>\n\n🎉 Tutti e tre i tool completati!')

    return json.dumps({'response_action': 'clear'}), 200, {'Content-Type': 'application/json'}


# ============================================================
# MODAL BUILDERS
# ============================================================
def build_step1_view(channel_id, user_id, response_url):
    return {
        'type': 'modal',
        'callback_id': 'step1_adunit',
        'title':  {'type': 'plain_text', 'text': '📦 Step 1/3 — Ad Unit Builder'},
        'submit': {'type': 'plain_text', 'text': 'Genera CSV e continua →'},
        'close':  {'type': 'plain_text', 'text': 'Annulla tutto'},
        'private_metadata': json.dumps({'channel_id': channel_id, 'user_id': user_id, 'response_url': response_url}),
        'blocks': get_adunit_blocks()
    }


def build_step2_view(private_metadata):
    return {
        'type': 'modal',
        'callback_id': 'step2_pathvast',
        'title':  {'type': 'plain_text', 'text': '🎬 Step 2/3 — Path/VAST Builder'},
        'submit': {'type': 'plain_text', 'text': 'Genera output e continua →'},
        'close':  {'type': 'plain_text', 'text': 'Salta questo step'},
        'private_metadata': private_metadata,
        'blocks': get_pathvast_blocks()
    }


def build_step3_view(private_metadata):
    return {
        'type': 'modal',
        'callback_id': 'step3_bulkupload',
        'title':  {'type': 'plain_text', 'text': '🌐 Step 3/3 — Bulk Upload Sites'},
        'submit': {'type': 'plain_text', 'text': 'Genera CSV e termina ✓'},
        'close':  {'type': 'plain_text', 'text': 'Salta questo step'},
        'private_metadata': private_metadata,
        'blocks': get_bulkupload_blocks()
    }


# ============================================================
# SLACK API HELPERS
# ============================================================
def call_slack_api(method, body):
    resp = requests.post(
        f'https://slack.com/api/{method}',
        headers={
            'Authorization': f'Bearer {SLACK_BOT_TOKEN}',
            'Content-Type': 'application/json'
        },
        json=body
    )
    result = resp.json()
    if not result.get('ok'):
        raise Exception(f'Slack API error ({method}): {result.get("error")}')
    return result


def upload_file(channel_id, user_id, filename, content, title, comment):
    resp = requests.post(
        'https://slack.com/api/files.upload',
        data={
            'token':           SLACK_BOT_TOKEN,
            'channels':        channel_id,
            'filename':        filename,
            'initial_comment': comment,
            'title':           title,
            'content':         content,
            'filetype':        'csv'
        }
    )
    result = resp.json()
    if not result.get('ok'):
        # Fallback: testo nel canale
        call_slack_api('chat.postMessage', {
            'channel': channel_id,
            'text': comment + '\n```' + content[:2800] + '```'
        })
    return result


def get_dm_channel(user_id):
    result = call_slack_api('conversations.open', {'users': user_id})
    return result['channel']['id']


def get_timestamp():
    return datetime.now().strftime('%Y%m%d_%H%M%S')

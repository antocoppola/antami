from flask import Flask, request, jsonify
import json, requests, os
from datetime import datetime
from adunit import get_adunit_blocks, generate_adunit_csv
from pathvast import get_pathvast_blocks, generate_pathvast_output
from bulkupload import get_bulkupload_blocks, generate_bulkupload_csv

app = Flask(__name__)
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')

@app.route('/', methods=['GET'])
def health():
    return 'OK', 200

@app.route('/', methods=['POST'])
def main():
    if request.content_type and 'application/x-www-form-urlencoded' in request.content_type:
        body = request.get_data(as_text=True)
        if body.startswith('payload='):
            from urllib.parse import unquote_plus
            payload = json.loads(unquote_plus(body[len('payload='):]))
            return handle_interaction(payload)
        params = request.form
        if params.get('command'):
            return handle_slash_command(params)
    return jsonify({'ok': True})

def handle_slash_command(params):
    trigger_id = params.get('trigger_id')
    channel_id = params.get('channel_id')
    user_id = params.get('user_id')
    response_url = params.get('response_url')
    open_step1_modal(trigger_id, channel_id, user_id, response_url)
    return '', 200

def handle_interaction(payload):
    if payload.get('type') == 'view_submission':
        return handle_view_submission(payload)
    return jsonify({'ok': True})

def handle_view_submission(payload):
    callback_id = payload['view']['callback_id']
    values = payload['view']['state']['values']
    user_id = payload['user']['id']
    try:
        meta = json.loads(payload['view'].get('private_metadata') or '{}')
    except:
        meta = {}
    channel_id = meta.get('channel_id')
    response_url = meta.get('response_url')
    try:
        if callback_id == 'step1_adunit':
            return handle_step1(values, user_id, channel_id, response_url)
        if callback_id == 'step2_pathvast':
            return handle_step2(values, user_id, channel_id, response_url)
        if callback_id == 'step3_bulkupload':
            return handle_step3(values, user_id, channel_id, response_url)
    except Exception as e:
        return jsonify({'response_action': 'errors', 'errors': {'publisher_block': '❌ ' + str(e)}})
    return jsonify({'response_action': 'clear'})

def open_step1_modal(trigger_id, channel_id, user_id, response_url):
    call_slack('views.open', {'trigger_id': trigger_id, 'view': {
        'type': 'modal', 'callback_id': 'step1_adunit',
        'title': {'type': 'plain_text', 'text': '📦 Step 1/3 — Ad Unit'},
        'submit': {'type': 'plain_text', 'text': 'Genera e continua →'},
        'close': {'type': 'plain_text', 'text': 'Annulla'},
        'private_metadata': json.dumps({'channel_id': channel_id, 'user_id': user_id, 'response_url': response_url}),
        'blocks': get_adunit_blocks()
    }})

def handle_step1(values, user_id, channel_id, response_url):
    csv = generate_adunit_csv(values)
    upload_file(channel_id or get_dm(user_id), user_id, 'adunit_' + ts() + '.csv', csv, '✅ *[1/3] Ad Unit Builder* — <@' + user_id + '>')
    return jsonify({'response_action': 'update', 'view': {
        'type': 'modal', 'callback_id': 'step2_pathvast',
        'title': {'type': 'plain_text', 'text': '🎬 Step 2/3 — Path/VAST'},
        'submit': {'type': 'plain_text', 'text': 'Genera e continua →'},
        'close': {'type': 'plain_text', 'text': 'Salta'},
        'private_metadata': json.dumps({'channel_id': channel_id, 'user_id': user_id, 'response_url': response_url}),
        'blocks': get_pathvast_blocks()
    }})

def handle_step2(values, user_id, channel_id, response_url):
    out = generate_pathvast_output(values)
    t = values['type_block']['type_input']['selected_option']['value']
    upload_file(channel_id or get_dm(user_id), user_id, ('paths_' if t=='path' else 'vast_') + ts() + '.csv', out, '✅ *[2/3] ' + ('Path' if t=='path' else 'VAST') + ' Builder* — <@' + user_id + '>')
    return jsonify({'response_action': 'update', 'view': {
        'type': 'modal', 'callback_id': 'step3_bulkupload',
        'title': {'type': 'plain_text', 'text': '🌐 Step 3/3 — Bulk Sites'},
        'submit': {'type': 'plain_text', 'text': 'Genera e termina ✓'},
        'close': {'type': 'plain_text', 'text': 'Salta'},
        'private_metadata': json.dumps({'channel_id': channel_id, 'user_id': user_id, 'response_url': response_url}),
        'blocks': get_bulkupload_blocks()
    }})

def handle_step3(values, user_id, channel_id, response_url):
    csv = generate_bulkupload_csv(values)
    upload_file(channel_id or get_dm(user_id), user_id, 'domain_mcm_' + ts() + '.csv', csv, '✅ *[3/3] Bulk Upload Sites* — <@' + user_id + '>\n\n🎉 Completato!')
    return jsonify({'response_action': 'clear'})

def call_slack(method, body):
    r = requests.post('https://slack.com/api/' + method,
        headers={'Authorization': 'Bearer ' + SLACK_BOT_TOKEN, 'Content-Type': 'application/json'},
        json=body)
    return r.json()

def upload_file(channel_id, user_id, filename, content, comment):
    requests.post('https://slack.com/api/files.upload', data={
        'token': SLACK_BOT_TOKEN, 'channels': channel_id,
        'filename': filename, 'title': filename,
        'initial_comment': comment, 'content': content, 'filetype': 'csv'
    })

def get_dm(user_id):
    r = call_slack('conversations.open', {'users': user_id})
    return r['channel']['id']

def ts():
    return datetime.now().strftime('%Y%m%d_%H%M%S')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

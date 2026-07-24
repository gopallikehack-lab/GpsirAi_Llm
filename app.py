import os
import json
import requests
import time
import base64
import hashlib
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from urllib.parse import quote

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'gpsirai_super_secret_key_2026')
CORS(app)

HF_TOKEN = os.environ.get('HF_TOKEN', '')
HF_DATASET = os.environ.get('HF_DATASET', 'gopallikehack/MULTIMEDIA')

MODELS = {
    'gpt-5': {
        'name': 'GPT-5',
        'logo': 'gpt5.png',
        'color': '#10A37F',
        'accent': '#74AA9C',
        'api_url': 'https://r-bots-free-apis.co08.art/api/v1/api/gpt-5',
        'param': 'q',
        'description': 'Latest OpenAI GPT-5 model'
    },
    'deep-ai': {
        'name': 'Deep AI Reasoning',
        'logo': 'deepai.png',
        'color': '#6366F1',
        'accent': '#818CF8',
        'api_url': 'https://r-bots-free-apis.co08.art/api/v1/api/deep-ai',
        'param': 'query',
        'description': 'Advanced reasoning AI'
    },
    'llama': {
        'name': 'Llama AI',
        'logo': 'llama.png',
        'color': '#F59E0B',
        'accent': '#FCD34D',
        'api_url': 'https://r-bots-free-apis.co08.art/api/v1/api/llama-meta',
        'param': 'q',
        'description': "Meta's Llama 3.1 AI"
    },
    'copilot': {
        'name': 'Copilot AI',
        'logo': 'copilot.png',
        'color': '#00A4EF',
        'accent': '#4FC3F7',
        'api_url': 'https://r-bots-free-apis.co08.art/api/v1/api/copilot',
        'param': 'text',
        'description': 'Microsoft Copilot AI'
    }
}

UTILITIES = {
    'randomimage': {
        'name': 'Random Image',
        'icon': '🖼️',
        'api_url': 'https://r-bots-free-apis.co08.art/api/v1/api/randomimage',
        'type': 'image',
        'response_key': 'responce'
    },
    'randomquotes': {
        'name': 'Random Quotes',
        'icon': '💬',
        'api_url': 'https://r-bots-free-apis.co08.art/api/v1/api/randomquotes',
        'type': 'text',
        'response_key': 'quotes'
    },
    'facts': {
        'name': 'Random Facts',
        'icon': '🧠',
        'api_url': 'https://r-bots-free-apis.co08.art/api/v1/api/facts',
        'type': 'text',
        'response_key': 'fact'
    },
    'waifu': {
        'name': 'Waifu Generator',
        'icon': '🌸',
        'api_url': 'https://r-bots-free-apis.co08.art/api/v1/api/waifu',
        'type': 'image',
        'response_key': None
    },
    'cosplay': {
        'name': 'Cosplay Generator',
        'icon': '🎭',
        'api_url': 'https://r-bots-free-apis.co08.art/api/v1/api/cosplay',
        'type': 'image',
        'response_key': None
    }
}

def get_user_id():
    if 'user_id' not in session:
        session['user_id'] = hashlib.md5(str(time.time()).encode()).hexdigest()[:16]
    return session['user_id']

def save_chat_history(model_id, messages):
    try:
        session['chat_history'] = session.get('chat_history', {})
        session['chat_history'][model_id] = messages
        session.modified = True
        return True
    except:
        return False

def load_chat_history(model_id):
    try:
        session_history = session.get('chat_history', {})
        return session_history.get(model_id, [])
    except:
        return []

def delete_chat_history(model_id):
    try:
        session_history = session.get('chat_history', {})
        if model_id in session_history:
            del session_history[model_id]
            session['chat_history'] = session_history
            session.modified = True
        return True
    except:
        return False

def call_ai_api(model_id, query):
    model = MODELS.get(model_id)
    if not model:
        return {'success': False, 'error': 'Model not found'}
    try:
        url = model['api_url']
        param = model['param']
        full_url = f"{url}?{param}={quote(query)}"
        response = requests.get(full_url, timeout=60)
        if response.status_code == 200:
            data = response.json()
            if model_id == 'gpt-5':
                text = data.get('results', 'No response')
            elif model_id == 'deep-ai':
                text = data.get('results', 'No response')
            elif model_id == 'llama':
                text = data.get('response', 'No response')
            elif model_id == 'copilot':
                text = data.get('results', {}).get('text', 'No response')
            else:
                text = str(data)
            return {
                'success': True,
                'response': text,
                'model': model['name'],
                'model_id': model_id
            }
        else:
            return {'success': False, 'error': f'API Error: {response.status_code}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def fetch_image(util):
    try:
        response = requests.get(util['api_url'], timeout=30)
        if response.status_code == 200:
            try:
                data = response.json()
                if util.get('response_key') and util['response_key'] in data:
                    image_url = data[util['response_key']]
                    if image_url.startswith('http'):
                        return {
                            'success': True,
                            'image_url': image_url,
                            'type': 'url'
                        }
            except:
                pass
            content_type = response.headers.get('Content-Type', 'image/png')
            image_data = response.content
            b64 = base64.b64encode(image_data).decode('utf-8')
            return {
                'success': True,
                'image': f"data:{content_type};base64,{b64}",
                'type': 'base64'
            }
        return {'success': False, 'error': f'HTTP {response.status_code}'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/')
def index():
    return render_template('index.html', models=MODELS, utilities=UTILITIES)

@app.route('/chat/<model_id>')
def chat_page(model_id):
    if model_id not in MODELS:
        return render_template('index.html', models=MODELS, utilities=UTILITIES)
    messages = load_chat_history(model_id)
    return render_template('chat.html', model=MODELS[model_id], model_id=model_id, messages=messages)

@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.get_json()
    model_id = data.get('model', 'gpt-5')
    query = data.get('query', '').strip()
    if not query:
        return jsonify({'success': False, 'error': 'Query cannot be empty'}), 400
    if model_id not in MODELS:
        return jsonify({'success': False, 'error': 'Invalid model'}), 400
    messages = load_chat_history(model_id)
    messages.append({'role': 'user', 'content': query})
    result = call_ai_api(model_id, query)
    if result.get('success'):
        messages.append({'role': 'assistant', 'content': result['response']})
        save_chat_history(model_id, messages)
        result['history'] = messages
    else:
        error_msg = f"⚠️ Error: {result.get('error', 'Unknown error')}. Please try again."
        messages.append({'role': 'assistant', 'content': error_msg})
        save_chat_history(model_id, messages)
        result['history'] = messages
    return jsonify(result)

@app.route('/api/chat/history/<model_id>', methods=['GET'])
def get_chat_history(model_id):
    if model_id not in MODELS:
        return jsonify({'error': 'Invalid model'}), 400
    messages = load_chat_history(model_id)
    return jsonify({'success': True, 'messages': messages})

@app.route('/api/chat/history/<model_id>', methods=['DELETE'])
def delete_chat_history_route(model_id):
    if model_id not in MODELS:
        return jsonify({'error': 'Invalid model'}), 400
    if delete_chat_history(model_id):
        return jsonify({'success': True, 'message': 'History deleted'})
    else:
        return jsonify({'success': False, 'error': 'Failed to delete'}), 500

@app.route('/api/utility/<utility_id>')
def utility_api(utility_id):
    if utility_id not in UTILITIES:
        return jsonify({'error': 'Utility not found'}), 404
    util = UTILITIES[utility_id]
    if util['type'] == 'image':
        result = fetch_image(util)
        if result['success']:
            return jsonify({
                'success': True,
                'image': result.get('image'),
                'image_url': result.get('image_url'),
                'type': result['type']
            })
        else:
            return jsonify({'success': False, 'error': result['error']}), 500
    else:
        try:
            response = requests.get(util['api_url'], timeout=30)
            if response.status_code == 200:
                data = response.json()
                key = util.get('response_key', 'text')
                text = data.get(key, str(data))
                return jsonify({
                    'success': True,
                    'text': text,
                    'type': 'text'
                })
            else:
                return jsonify({'error': f'API Error: {response.status_code}'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

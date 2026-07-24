import os
import json
import requests
import random
import time
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from urllib.parse import quote

app = Flask(__name__)
CORS(app)

# ============================================================
# AI MODEL CONFIGURATION
# ============================================================

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
        'type': 'image'
    },
    'randomquotes': {
        'name': 'Random Quotes',
        'icon': '💬',
        'api_url': 'https://r-bots-free-apis.co08.art/api/v1/api/randomquotes',
        'type': 'text'
    },
    'facts': {
        'name': 'Random Facts',
        'icon': '🧠',
        'api_url': 'https://r-bots-free-apis.co08.art/api/v1/api/facts',
        'type': 'text'
    },
    'waifu': {
        'name': 'Waifu Generator',
        'icon': '🌸',
        'api_url': 'https://r-bots-free-apis.co08.art/api/v1/api/waifu',
        'type': 'image'
    },
    'cosplay': {
        'name': 'Cosplay Generator',
        'icon': '🎭',
        'api_url': 'https://r-bots-free-apis.co08.art/api/v1/api/cosplay',
        'type': 'image'
    }
}

# ============================================================
# AI CHAT FUNCTION
# ============================================================

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

# ============================================================
# ROUTES
# ============================================================

@app.route('/')
def index():
    return render_template('index.html', models=MODELS, utilities=UTILITIES)

@app.route('/chat')
def chat():
    return render_template('chat.html', models=MODELS)

@app.route('/utilities')
def utilities_page():
    return render_template('utilities.html', utilities=UTILITIES)

@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.get_json()
    model_id = data.get('model', 'gpt-5')
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'success': False, 'error': 'Query cannot be empty'}), 400
    
    if model_id not in MODELS:
        return jsonify({'success': False, 'error': 'Invalid model'}), 400
    
    result = call_ai_api(model_id, query)
    return jsonify(result)

@app.route('/api/utility/<utility_id>')
def utility_api(utility_id):
    if utility_id not in UTILITIES:
        return jsonify({'error': 'Utility not found'}), 404
    
    util = UTILITIES[utility_id]
    
    try:
        response = requests.get(util['api_url'], timeout=30)
        
        if response.status_code == 200:
            if util['type'] == 'image':
                return jsonify({
                    'success': True,
                    'image_url': response.text.strip(),
                    'type': 'image'
                })
            else:
                data = response.json()
                if utility_id == 'randomquotes':
                    text = data.get('quotes', 'No quote available')
                elif utility_id == 'facts':
                    text = data.get('fact', 'No fact available')
                else:
                    text = str(data)
                
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

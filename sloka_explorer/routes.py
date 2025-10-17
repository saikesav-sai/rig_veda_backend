import json
import os

from flask import Blueprint, Flask, abort, jsonify, send_file

veda_bp = Blueprint("veda_bp", __name__)
BASE_PATH = f"data/dataset"
_HERE = os.path.dirname(__file__)
_AUDIO_ABS = os.path.abspath(os.path.join(_HERE, "..", "data", "audio"))
AUDIO_FOLDER = _AUDIO_ABS

def load_index():
    index_path = os.path.join(BASE_PATH, 'rig_veda_index.json')
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_mandala(mandala_num):
    mandala_path = os.path.join(BASE_PATH, f'mandala_{mandala_num}.json')
    try:
        with open(mandala_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


@veda_bp.route('/api/index/<int:mandala_num>')
def get_index_for_mandala(mandala_num):
    index = load_index()
    mandalas = index.get('mandalas', [])
    mandala_info = next((m for m in mandalas if m['mandala_number'] == mandala_num), None)
    if not mandala_info:
        abort(404, description="Mandala not found in index")
    
    hymns_summary = []
    for hymn in mandala_info.get('hymns', []):
        hymns_summary.append({
            'hymn_number': hymn.get('hymn_number'),
            'total_stanzas': hymn.get('total_slokas') 
        })
    return jsonify({
        'mandala': mandala_num,
        'total_hymns': len(mandala_info.get('hymns', [])),
        'hymns': hymns_summary
    })
 
@veda_bp.route('/api/sloka/<int:mandala_num>/<int:hymn_num>/<int:stanza_num>')
def get_sloka(mandala_num, hymn_num, stanza_num):
    mandala_data = load_mandala(mandala_num)
    if not mandala_data:
        abort(404, description="Mandala data not found")
    
    hymn = next((h for h in mandala_data.get('hymns', []) if h['hymn_number'] == hymn_num), None)
    if not hymn:
        abort(404, description="Hymn not found")

    stanza = next((s for s in hymn.get('stanzas', []) if s['stanza_number'] == stanza_num), None)
    if not stanza:
        abort(404, description="Stanza not found")

    return jsonify(stanza)

@veda_bp.route('/api/audio/<int:mandala_num>/<int:hymn_num>/<int:stanza_num>')
def get_audio(mandala_num, hymn_num, stanza_num):
    audio_path = os.path.join(AUDIO_FOLDER, str(mandala_num), f"Hymn_{str(hymn_num)}", f"Stanza_{stanza_num}.mp3")
    if not os.path.exists(audio_path):
        return jsonify({'error': 'Audio file not found', 'path': audio_path}), 404
    return send_file(audio_path, mimetype='audio/mpeg')


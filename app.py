from flask import Flask, render_template, request, jsonify
from datetime import datetime
app = Flask(__name__)

eventi = []

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/evento', methods=['POST'])
def ricevi_evento():
    dati = request.json
    dati['timestamp_inizio'] = dati.get('timestamp_inizio', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    dati['timestamp_fine'] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    dati['tempo_elaborazione'] = dati.get('tempo_elaborazione', 0)
    eventi.append(dati)
    return jsonify({'status': 'ok'})

@app.route('/api/eventi')
def get_eventi():
    return jsonify(eventi)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
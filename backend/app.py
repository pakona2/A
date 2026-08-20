import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, abort, current_app, g, jsonify, request
from flask_cors import CORS
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse


DEFAULT_CONTACTS = [
    ('Maya Chen', '@maya.chen', 'MC', 'coral', 'On a call'),
    ('Jordan Bell', '@jordan.b', 'JB', 'mint', 'Available'),
    ('Samira Okafor', '@samira.o', 'SO', 'violet', 'Available'),
    ('Leo Park', '@leo.park', 'LP', 'gold', 'Away'),
]
E164_PATTERN = re.compile(r'^\+[1-9]\d{7,14}$')


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=os.environ.get('CALLME_DATABASE', str(Path(__file__).with_name('callme.sqlite3'))),
        FRONTEND_ORIGIN=os.environ.get('FRONTEND_ORIGIN', 'http://localhost:5173,capacitor://localhost,http://localhost'),
        TWILIO_ACCOUNT_SID=os.environ.get('TWILIO_ACCOUNT_SID', ''),
        TWILIO_AUTH_TOKEN=os.environ.get('TWILIO_AUTH_TOKEN', ''),
        TWILIO_FROM_NUMBER=os.environ.get('TWILIO_FROM_NUMBER', ''),
        CALL_GREETING=os.environ.get('CALL_GREETING', 'You are receiving a CallMe call.'),
    )
    if test_config:
        app.config.update(test_config)

    allowed_origins = [origin.strip() for origin in app.config['FRONTEND_ORIGIN'].split(',') if origin.strip()]
    CORS(app, resources={r'/api/*': {'origins': allowed_origins}})

    with app.app_context():
        init_db(app)

    @app.teardown_appcontext
    def close_db(_error=None):
        database = g.pop('database', None)
        if database is not None:
            database.close()

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify(error=str(error.description)), 400

    @app.get('/api/health')
    def health():
        return jsonify({'status': 'ok', 'service': 'CallMe API', 'timestamp': utc_now()})

    @app.get('/api/contacts')
    def list_contacts():
        rows = get_db().execute('SELECT * FROM contacts ORDER BY name').fetchall()
        return jsonify({'contacts': [dict(row) for row in rows]})

    @app.post('/api/contacts')
    def create_contact():
        payload = json_body(('name', 'handle', 'initials', 'color'))
        database = get_db()
        try:
            cursor = database.execute(
                'INSERT INTO contacts (name, handle, initials, color, status) VALUES (?, ?, ?, ?, ?)',
                (payload['name'], payload['handle'], payload['initials'], payload['color'], payload.get('status', 'Available')),
            )
            database.commit()
        except sqlite3.IntegrityError:
            return jsonify(error='A contact with that handle already exists'), 409
        contact = database.execute('SELECT * FROM contacts WHERE id = ?', (cursor.lastrowid,)).fetchone()
        return jsonify(contact=dict(contact)), 201

    @app.get('/api/calls')
    def list_calls():
        rows = get_db().execute('SELECT * FROM calls ORDER BY created_at DESC LIMIT 50').fetchall()
        return jsonify({'calls': [dict(row) for row in rows]})

    @app.post('/api/calls')
    def create_call():
        payload = json_body(('phone_number',))
        call_type = payload.get('type', 'outgoing')
        if call_type not in {'outgoing', 'incoming', 'missed'}:
            return jsonify(error='type must be outgoing, incoming, or missed'), 400
        database = get_db()
        cursor = database.execute(
            'INSERT INTO calls (name, phone_number, type, duration, created_at) VALUES (?, ?, ?, ?, ?)',
            (payload.get('name', payload['phone_number']), payload['phone_number'], call_type, payload.get('duration', 'Connecting'), utc_now()),
        )
        database.commit()
        call = database.execute('SELECT * FROM calls WHERE id = ?', (cursor.lastrowid,)).fetchone()
        return jsonify(call=dict(call)), 201

    @app.post('/api/calls/trigger')
    def trigger_call():
        payload = json_body(('phone_number',))
        phone_number = payload['phone_number']
        if not E164_PATTERN.fullmatch(phone_number):
            return jsonify(error='phone_number must use international E.164 format, for example +14155552671'), 400
        missing_config = [key for key in ('TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_FROM_NUMBER') if not app.config[key]]
        if missing_config:
            return jsonify(error='Calling provider is not configured', missing_config=missing_config), 503
        try:
            twilio_call = Client(app.config['TWILIO_ACCOUNT_SID'], app.config['TWILIO_AUTH_TOKEN']).calls.create(
                to=phone_number,
                from_=app.config['TWILIO_FROM_NUMBER'],
                twiml=voice_twiml(app.config['CALL_GREETING']),
            )
        except Exception:
            app.logger.exception('Twilio call failed')
            return jsonify(error='The call provider could not start the call'), 502
        database = get_db()
        cursor = database.execute(
            'INSERT INTO calls (name, phone_number, type, duration, created_at) VALUES (?, ?, ?, ?, ?)',
            (payload.get('name', phone_number), phone_number, 'outgoing', 'Started', utc_now()),
        )
        database.commit()
        return jsonify(call_id=cursor.lastrowid, provider_call_id=twilio_call.sid, status=twilio_call.status), 201

    @app.post('/api/twilio/status')
    def twilio_status():
        payload = request.form
        current_app.logger.info('Twilio call %s status: %s', payload.get('CallSid'), payload.get('CallStatus'))
        return ('', 204)

    @app.post('/api/twilio/voice')
    def twilio_voice():
        return voice_twiml(app.config['CALL_GREETING']), 200, {'Content-Type': 'text/xml'}

    return app


def get_db():
    if 'database' not in g:
        database = sqlite3.connect(current_app.config['DATABASE'])
        database.row_factory = sqlite3.Row
        g.database = database
    return g.database


def init_db(app):
    database = sqlite3.connect(app.config['DATABASE'])
    database.executescript('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            handle TEXT NOT NULL UNIQUE,
            initials TEXT NOT NULL,
            color TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Available'
        );
        CREATE TABLE IF NOT EXISTS calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            type TEXT NOT NULL,
            duration TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    ''')
    if database.execute('SELECT COUNT(*) FROM contacts').fetchone()[0] == 0:
        database.executemany('INSERT INTO contacts (name, handle, initials, color, status) VALUES (?, ?, ?, ?, ?)', DEFAULT_CONTACTS)
    database.commit()
    database.close()


def json_body(required):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        abort(400, description='Request body must be a JSON object')
    missing = [key for key in required if not str(payload.get(key, '')).strip()]
    if missing:
        abort(400, description=f'Missing required field(s): {", ".join(missing)}')
    return {key: str(value).strip() if value is not None else value for key, value in payload.items()}


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def voice_twiml(greeting):
    response = VoiceResponse()
    response.say(greeting)
    return str(response)


app = create_app()

if __name__ == '__main__':
    app.run(host=os.environ.get('HOST', '0.0.0.0'), port=int(os.environ.get('PORT', '5000')))

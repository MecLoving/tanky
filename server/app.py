import sys
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import threading

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Now import your GameServer after path is set
from server.game_server import GameServer

app = Flask(__name__, 
            template_folder='../client/templates',  # Update this path
            static_folder='../client/static')       # Update static files too
socketio = SocketIO(app)
game_server = GameServer()

# Run WebSocket server in background
threading.Thread(
    target=game_server.run,
    daemon=True
).start()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/lobby')
def lobby():
    return render_template('lobby.html')

@app.route('/game')
def game():
    return render_template('game.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('join_queue')
def handle_join_queue(data):
    join_time = datetime.now().strftime('%H:%M:%S')
    print(f"Player joined {data['queue_type']} queue at {join_time}")
    
    emit('queue_update', {
        'message': f'Searching {data["queue_type"]} match...',
        'queue_type': data['queue_type']
    })
    
    # Simulate match found after 3 seconds
    threading.Timer(3.0, lambda: emit('match_found')).start()

if __name__ == '__main__':
    socketio.run(app, debug=True)
import sys
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, request  # Added request
from flask_socketio import SocketIO, emit  # Added emit to imports
import threading

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Now import your GameServer after path is set
from server.game_server import GameServer

app = Flask(__name__, 
            template_folder='../client/templates',
            static_folder='../client/static')
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
    
    # Use either:
    # Option 1: The emit that's automatically available in SocketIO handlers
    emit('queue_update', {
        'message': f'Searching {data["queue_type"]} match...',
        'queue_type': data['queue_type']
    })
    
    # Option 2: Or use socketio.emit explicitly
    # socketio.emit('queue_update', {
    #     'message': f'Searching {data["queue_type"]} match...',
    #     'queue_type': data['queue_type']
    # })
    
    # Simulate match found after 3 seconds
    threading.Timer(3.0, lambda: socketio.emit('match_found', room=request.sid)).start()

if __name__ == '__main__':
    socketio.run(app, debug=True)
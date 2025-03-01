# flask_server.py
from flask import Flask
from flask_socketio import SocketIO
import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('send_data')
def handle_data(data):
    print("📥 Received data from client:")
    print(data)
    
    # 데이터 키 이름 통일: led_brightness -> light, monitor_tilt -> monitor_angle
    if "led_brightness" in data:
        data["light"] = data.pop("led_brightness")
    if "monitor_tilt" in data:
        data["monitor_angle"] = data.pop("monitor_tilt")
    
    # 모든 클라이언트(예: desk_gui, user_gui)로 변경된 데이터 전달
    socketio.emit('desk_update', data, broadcast=True)

    response_data = {
        "status": "received",
        "timestamp": datetime.datetime.now().isoformat(),
        "message": "Data received and broadcasted successfully"
    }
    socketio.emit('response_data', response_data)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=2000, allow_unsafe_werkzeug=True)

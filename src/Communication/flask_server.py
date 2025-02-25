from flask import Flask
from flask_socketio import SocketIO
import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 클라이언트에서 메시지를 받을 때 실행되는 함수
@socketio.on('send_data')
def handle_data(data):
    print("📥 Received data from client:")
    print(data)

    # 서버에서 받은 데이터를 클라이언트에게 응답으로 전송
    response_data = {
        "status": "received",
        "timestamp": datetime.datetime.now().isoformat(),
        "message": "Data received successfully"
    }
    socketio.emit('response_data', response_data)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True) #포트번호 5000번 이상설정할것

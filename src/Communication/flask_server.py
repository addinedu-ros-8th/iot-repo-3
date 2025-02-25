from flask import Flask, render_template
from flask_socketio import SocketIO, send
import threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 메시지를 클라이언트들에게 브로드캐스트
@socketio.on('message')
def handle_message(msg):
    print(f"클라이언트: {msg}")
    send(msg, broadcast=True)

# 서버에서 터미널 입력을 받아 클라이언트에게 전송
def send_from_terminal():
    while True:
        message = input("서버에서 보낼 메시지: ")
        socketio.send(message)

if __name__ == '__main__':
    threading.Thread(target=send_from_terminal, daemon=True).start()
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)

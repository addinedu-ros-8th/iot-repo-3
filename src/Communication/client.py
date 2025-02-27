import socketio
import datetime
import random

sio = socketio.Client()

@sio.on('response_data')
def on_response(data):
    print("📤 Received response from server:")
    print(data)

if __name__ == "__main__":
    server_url = "http://192.168.245.485:5000"  # 서버 주소
    sio.connect(server_url)

    # 더미 데이터 생성
    data = {
        "user_id": "04AABBCCDD",  # HEX 형식
        "function_code": random.randint(1, 10),
        "mode": random.randint(0, 1),
        "request_id": random.randint(1000, 9999),
        "timestamp": datetime.datetime.now().isoformat(),
        "light": random.randint(0, 100),
        "desk_status": random.randint(0, 1),
        "monitor_height": random.randint(50, 150),
        "monitor_angle": random.randint(0, 180),
        "desk_height": random.randint(60, 120)
    }

    print("📤 Sending data to server:")
    print(data)

    sio.emit('send_data', data)
    sio.wait()

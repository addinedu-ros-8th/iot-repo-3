import socket
import json

# 서버의 IP 주소와 포트를 지정하세요.
HOST = '192.168.2.41'  # 예: '192.168.1.100'
PORT = 12345

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((HOST, PORT))
    print("서버에 연결되었습니다.")

    while True:
        user_input = input("보낼 메시지를 입력하세요 (종료하려면 'exit' 입력): ")
        if user_input.lower() == 'exit':
            print("연결을 종료합니다.")
            break

        # JSON 형식의 메시지 생성 (예시 구조)
        data = {
            "servo1": 110,
            "servo2": 70
        }
        client_socket.sendall(json.dumps(data).encode())
        print("메시지를 전송했습니다:", data)

        data = client_socket.recv(1024)
        if not data:
            print("서버가 연결을 종료했습니다.")
            break

        response_str = data.decode()
        try:
            response_json = json.loads(response_str)
        except json.JSONDecodeError:
            response_json = None

        print("서버 응답 (문자열):", response_str)
        print("서버 응답 (JSON):", response_json)

print("클라이언트 종료")

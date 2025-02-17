import socket
import json

HOST = '192.168.2.41'
PORT = 1237

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((HOST, PORT))
    print("서버에 연결되었습니다.")

    while True:
        command = input("메시지를 전송하려면 'send', 종료하려면 'exit'를 입력하세요: ")
        if command.lower() == 'exit':
            print("연결을 종료합니다.")
            break

        if command.lower() == 'send':
            try:
                servo1_angle = int(input("servo1 각도 (0~180): "))
                servo2_angle = int(input("servo2 각도 (0~180): "))
            except ValueError:
                print("유효한 정수 값을 입력하세요.")
                continue

            data = {
                "servo1": servo1_angle,
                "servo2": servo2_angle
            }
            client_socket.sendall(json.dumps(data).encode())
            print("메시지를 전송했습니다:", data)

            data_recv = client_socket.recv(1024)
            if not data_recv:
                print("서버가 연결을 종료했습니다.")
                break

            response_str = data_recv.decode()
            try:
                response_json = json.loads(response_str)
            except json.JSONDecodeError:
                response_json = None

            print("서버 응답 (문자열):", response_str)
            print("서버 응답 (JSON):", response_json)

print("클라이언트 종료")

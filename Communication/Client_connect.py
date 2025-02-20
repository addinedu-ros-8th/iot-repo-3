import socket
import json
import threading

HOST = '192.168.0.45' #IP 확인 후 변경
PORT = 1234 # 포트번호 확인 후 변경

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("서버가 연결을 종료했습니다.")
                break
            message = data.decode('utf-8')
            try:
                json_message = json.loads(message)
                print("서버로부터 수신된 JSON 메시지:", json_message)
            except json.JSONDecodeError:
                print("서버로부터 수신된 메시지 (문자열):", message)
        except Exception as e:
            print("수신 오류:", e)
            break

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((HOST, PORT))
    print("서버에 연결되었습니다.")

    recv_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
    recv_thread.start()

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
            client_socket.sendall(json.dumps(data, separators=(',', ':')).encode())
            print("서버에 메시지를 전송했습니다:", data)
    print("클라이언트 종료")

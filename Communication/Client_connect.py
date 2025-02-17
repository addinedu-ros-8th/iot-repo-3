import socket

HOST = '192.168.2.16'  # Raspberry Pi의 IP 주소로 변경
PORT = 12345                # 서버와 동일한 포트 번호

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    message = "아아 마이크 테스트"
    s.sendall(message.encode())
    data = s.recv(1024)
    print("서버로부터 수신:", data.decode())
import socket
import sys
import select
import termios
import tty

def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return None

HOST = '0.0.0.0'
PORT = 12345

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    server_socket.setblocking(False)
    print(f"서버가 {PORT} 포트에서 대기 중입니다. (ESC 키 누르면 종료)")

    connections = []

    try:
        while True:
            try:
                conn, addr = server_socket.accept()
                print(f"연결됨: {addr}")
                conn.setblocking(False)
                connections.append(conn)
            except BlockingIOError:
                pass

            for conn in connections[:]:
                try:
                    data = conn.recv(1024)
                    if data:
                        print("수신 데이터:", data.decode())
                        conn.sendall(data)
                    else:
                        print("클라이언트 연결 종료")
                        connections.remove(conn)
                        conn.close()
                except BlockingIOError:
                    continue

                except ConnectionResetError:
                    print("클라이언트 강제 종료")
                    connections.remove(conn)
                    conn.close()
            key = get_key()
            if key == '\x1b':
                print("ESC 키 입력 감지, 서버를 종료합니다.")
                break

    finally:
        for conn in connections:
            conn.close()
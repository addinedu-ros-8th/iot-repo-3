import socket
import json
import threading
import sys
import select
import termios
import tty
import serial
import time

# 아두이노와 연결된 포트와 보드레이트 설정 (포트 이름은 환경에 맞게 수정)
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)  # 아두이노 리셋 대기

HOST = '0.0.0.0'   # 모든 인터페이스에서 접속 허용
PORT = 12345       # 사용할 포트 번호

# 전역 종료 플래그
exit_flag = False

def keyboard_listener():
    """
    별도의 스레드에서 키보드 입력을 감지하여 ESC 키가 눌리면 exit_flag를 True로 설정합니다.
    """
    global exit_flag
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)  # 문자 단위로 입력 받도록 설정
        while not exit_flag:
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
            if rlist:
                ch = sys.stdin.read(1)
                if ch == '\x1b':  # ESC 키 (ASCII 27)
                    print("\n[키보드] ESC 키 입력 감지. 서버를 종료합니다.")
                    exit_flag = True
                    break
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def run_server():
    global exit_flag
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        print(f"서버가 {PORT} 포트에서 대기 중입니다. (종료: ESC 키)")
        
        # 클라이언트 연결 수락
        conn, addr = server_socket.accept()
        with conn:
            print("클라이언트 연결됨:", addr)
            # 소켓에 타임아웃 설정 (0.5초마다 타임아웃 발생)
            conn.settimeout(0.5)
            while not exit_flag:
                try:
                    data = conn.recv(1024)
                    if not data:
                        # 클라이언트가 연결 종료 시
                        print("클라이언트가 연결을 종료했습니다.")
                        break

                    # 수신한 데이터를 문자열로 디코딩 및 JSON 파싱
                    received_message = data.decode()
                    print("수신된 원시 메시지:", received_message)
                    try:
                        json_data = json.loads(received_message)
                        print("파싱된 JSON 데이터:", json_data)
                    except json.JSONDecodeError as e:
                        print("JSON 파싱 에러:", e)
                        json_data = None

                    # 클라이언트에서 받은 JSON 데이터를 아두이노로 전송 (데이터 끝을 구분하기 위해 '\n' 추가)
                    if json_data is not None:
                        json_to_send = json.dumps(json_data) + '\n'
                        ser.write(json_to_send.encode('utf-8'))
                        print("아두이노로 전송된 데이터:", json_to_send)

                    # 응답 메시지 생성 (클라이언트로 회신)
                    response = {
                        "status": "ok",
                        "received": json_data,
                        "message": "메시지를 성공적으로 수신 및 아두이노로 전송했습니다."
                    }
                    conn.sendall(json.dumps(response).encode())
                except socket.timeout:
                    # 타임아웃 발생 시 exit_flag 확인 후 계속 반복
                    continue
                except Exception as e:
                    print("오류 발생:", e)
                    break

            print("서버 종료를 시작합니다.")

if __name__ == '__main__':
    # 키보드 감지 스레드 시작
    key_thread = threading.Thread(target=keyboard_listener, daemon=True)
    key_thread.start()

    # 서버 실행
    run_server()

    # 키보드 스레드 종료 대기
    key_thread.join()
    print("프로그램이 종료되었습니다.")

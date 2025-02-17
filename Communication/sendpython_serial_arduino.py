import json
import serial
import time

# 예시 TCP/IP 수신 후 JSON 데이터를 dictionary로 변환했다고 가정
data_dict = {
    'sensor1': 23.5,
    'sensor2': 48,
    'status': 'OK'
}

# dictionary를 JSON 문자열로 직렬화 (구분자로 '\n' 추가)
json_str = json.dumps(data_dict) + '\n'

# Arduino와 연결된 포트와 보드레이트 설정 (포트 이름은 환경에 맞게 수정)
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)  # Arduino 리셋 대기

# 데이터 전송
ser.write(json_str.encode('utf-8'))

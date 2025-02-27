![header](https://capsule-render.vercel.app/api?type=venom&color=timeGradient&height=300&section=header&text=SmartDesk&fontColor=333333&fontSize=90)                       
Smart DeskTerior
===========
Team 3. DeskMate(IOT Project)
***
## :computer: Skill Set
|Categories|SKills|
|------|------|
|IDE|![Static Badge](https://img.shields.io/badge/linux-%23FCC624?style=plastic&logo=linux&logoColor=ffffff) ![Static Badge](https://img.shields.io/badge/ubuntu-22.04-grey?style=plastic&logo=ubuntu&logoColor=ffffff&labelColor=%23E95420) ![Static Badge](https://img.shields.io/badge/vsCode-%232185D0?style=plastic&logo=vscode&logoColor=ffffff) ![Static Badge](https://img.shields.io/badge/jupyter-%23F37626?style=plastic&logo=jupyter&logoColor=ffffff) ![Static Badge](https://img.shields.io/badge/arduino-sketchIDE-grey?style=plastic&logo=arduino&labelColor=%2300878F)|
|Design|![Static Badge](https://img.shields.io/badge/figma-%23F24E1E?style=plastic&logo=figma&logoColor=white) ![Static Badge](https://img.shields.io/badge/pyQT-Designer-grey?style=plastic&logo=qt&logoColor=white&labelColor=%2341CD52)|
|Data|![Static Badge](https://img.shields.io/badge/mysql-%234479A1?style=plastic&logo=mysql&logoColor=ffffff) ![Static Badge](https://img.shields.io/badge/amazonrds-%23527FFF?style=plastic&logo=amazonrds&logoColor=ffffff)|
|Programming Languages|![Static Badge](https://img.shields.io/badge/Python-%233776AB?style=plastic&logo=python&logoColor=ffffff) ![Static Badge](https://img.shields.io/badge/C%2B%2B-%2300599C?style=plastic&logo=cplusplus&logoColor=white)|
|Communication|![Static Badge](https://img.shields.io/badge/serial-grey?style=plastic) ![Static Badge](https://img.shields.io/badge/flask-%23000000?style=plastic&logo=flask&logoColor=%23FFFFFF)|
|Cooperation Tools|![Static Badge](https://img.shields.io/badge/jira-%230052CC?style=plastic&logo=jira&logoColor=ffffff) ![Static Badge](https://img.shields.io/badge/confluence-%23172B4D?style=plastic&logo=confluence&logoColor=ffffff) ![Static Badge](https://img.shields.io/badge/slack-%234A154B?style=plastic&logo=slack)

***
## :sparkles: 구성원 및 역할
|구성원|역할|
|-----|-----|
|이정림(팀장)|프로젝트 관리<br>Jira 관리<br>desk GUI 설계<br>RFID : 사용자 인증, 커스텀 모드<br>user GUI 구현<br>tcp/ip 통신<br>Serial 통신|
|심채훈|기구 설계<br>DB 설계<br>책상 높이 제어<br>Serial 통신<br>TCP/IP 통신<br>Desk GUI 구현|
|이우재|기구 설계<br>DB 설계<br>DB 관리<br>모니터 제어<br>server 구현<br>발표|
|권 빛|user GUI 설계<br>user GUI 구현<br>LED 제어<br>PPT 제작<br>GitHub 정리|

***
## :hourglass_flowing_sand: 프로젝트 설계 및 개발 계획


***

# IOT 스마트데스크 프로젝트
![001](https://github.com/user-attachments/assets/04697113-9218-4869-9034-3c32d54ac885)

[프로젝트 목차]
![iot-스마트-데스크-002 (4)](https://github.com/user-attachments/assets/d9d94928-24ab-492e-971f-fd9b2e702c35)

## 1. 프로젝트 소개
IOT 스마트데스크 프로젝트는 사용자의 업무 및 학습 환경을 쾌적하게 만들기 위해 센서와 IoT 기술을 활용해 데스크 주변 환경을 자동으로 제어하는 시스템입니다.  
주요 기능은 조명 제어, 데스크 높낮이 및 모니터 각도 제어, 사용자 인식 기능 등을 포함하며, 사용자의 편의와 생산성 향상을 목표로 합니다.

## 2. 프로젝트 설계

### 2-1. Scenario
- **사용 시나리오 예시**  
  - 사용자가 책상 앞에 앉으면, 센서가 사용자를 인식하여 자동으로 조명을 켬  
  - 데스크와 모니터 높이를 사용자 신체에 맞게 조절  
  - 일정 시간이 지나면 자세 교정 알림 및 데스크 높낮이 자동 전환  

### 2-2. System Requirements
- **하드웨어**  
  - 센서(조도 센서, 거리 센서, 무게 센서 등)  
  - 데스크 높낮이 모터 및 제어 모듈  
  - 모니터 각도/높낮이 제어 모듈  
  - 조명 장치(스탠드, LED 조명 등)
- **소프트웨어**  
  - 마이크로컨트롤러(Arduino, ESP32 등) 펌웨어  
  - 서버/클라우드(데이터 수집 및 분석)  
  - 사용자 인터페이스(웹/모바일 앱)  

### 2-3. System Architecture
- **센서 데이터 흐름**: 센서 → 마이크로컨트롤러 → 서버(또는 클라우드)  
- **제어 명령 흐름**: 사용자 앱(또는 웹) → 서버 → 마이크로컨트롤러 → 모터/조명  

### 2-4. Desk 기구설계
- **데스크 프레임 구조**  
  - 모터 장착 위치 및 기어 구조  
  - 센서 부착 위치(앞, 뒤, 양 측면 등)  
- **안전성 고려**  
  - 기계식 안전 장치, 과부하 감지  

### 2-5. GUI 화면 설계
- **주요 화면**  
  - 센서 상태 모니터링 대시보드(온도, 습도, 조도, 사용자 유무 등)  
  - 데스크/모니터 제어 화면(높낮이, 각도 등 제어 슬라이더)  
  - 사용자 프로필 및 맞춤 세팅(신체 정보 기반 자동 세팅)  

## 3. 프로젝트 기능 설명

### 3-1. 조명 제어
- 조도 센서를 통해 주변 밝기를 측정하고, 자동으로 조명을 켜거나 밝기를 조절  
- 사용자가 앱 또는 웹을 통해 수동으로 밝기 및 색온도를 조절 가능  

### 3-2. 데스크 높낮이 제어
- 모터와 리니어 액추에이터를 활용하여 데스크의 높낮이를 자동 조절  
- 사용자 맞춤 프로필(신장, 자세)에 따라 최적 높이로 자동 세팅  

### 3-3. 모니터 높낮이·각도 제어
- 서보 모터를 통해 모니터의 각도와 높이를 조절  
- 집중 모드, 회의 모드 등 시나리오에 따라 미리 설정된 각도로 자동 전환  

### 3-4. 사용자 인식
- 거리 센서, 무게 센서, 혹은 카메라 모듈(선택 사항)을 통해 사용자가 책상 앞에 있는지 감지  
- 사용자 부재 시 에너지 절약 모드(조명·모니터 전원 자동 오프)  

## 4. 프로젝트 결과
- **시연 영상 및 사진**  
  - 실제 동작 시연 영상 또는 사진을 첨부  
  - 성능 평가(정확도, 반응 속도 등)  
- **추가 개선점**  
  - 소음 감소, 안전성 강화, UI/UX 개선 등  

---



### 문의
- 프로젝트 담당자: [example@example.com](mailto:example@example.com)


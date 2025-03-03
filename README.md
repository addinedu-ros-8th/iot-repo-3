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

![004](https://github.com/user-attachments/assets/81693ffc-63af-4ad8-8af7-6059edefb550)
![005](https://github.com/user-attachments/assets/c9bbb441-56bc-4773-8675-b5718d973a4a)

주요 기능은 조명 제어, 데스크 높낮이 및 모니터 각도 제어, 사용자 인식 기능 등을 포함하며, 사용자의 편의와 생산성 향상을 목표로 합니다.
## 2. 프로젝트 설계

### 2-1. Scenario
**RFID SUCCESS**
	![Image](https://github.com/user-attachments/assets/19a7bb6e-49a2-461e-82b3-b331f8d1313a)                             

**RFID ERROR**
	![Image](https://github.com/user-attachments/assets/768b0ca8-4562-4f66-b15c-38c2368a37e5)                            

**Manual Control Success**
	![Image](https://github.com/user-attachments/assets/60edacdf-2391-4af6-bd41-50f43be6db3b)                           

**Hardware ERROR**
	![Image](https://github.com/user-attachments/assets/7b8617cd-9413-4d3d-bbfc-0b6e83224b6b)                         

### 2-2. System Requirements

### 2-3. System Architecture
**하드웨어**  
  ![Image](https://github.com/user-attachments/assets/1266ac6a-ce54-477e-8a54-9d3f5cb76b88)
**소프트웨어**  
   ![Image](https://github.com/user-attachments/assets/ad806e1d-4484-4053-9f55-4f44a2ff73a2)

### 2-4. Desk 기구설계
![Image](https://github.com/user-attachments/assets/58cbd91a-8c2e-4470-9615-f38e8b717d34) 

### 2-5. GUI 화면 설계
**Desk GUI**  
	![Image](https://github.com/user-attachments/assets/a4cfb278-3b02-491c-bfa8-2bf264f3b5bb)
	![Image](https://github.com/user-attachments/assets/3dc70b8c-56c4-4881-a520-494bb41ab218)
	![Image](https://github.com/user-attachments/assets/bb876e61-491b-49b0-bef2-4f989fec1e86)
	![Image](https://github.com/user-attachments/assets/77213b30-df7d-41c1-99f2-b588ba3f5f26)
	![Image](https://github.com/user-attachments/assets/28a7e275-4b12-4d80-8b63-f6083eb957ab)             

**User GUI**
	![Image](https://github.com/user-attachments/assets/9b633cb9-929b-46c4-a888-866ce1624e2d)
	![Image](https://github.com/user-attachments/assets/803766fb-a3a0-4b93-ace6-d8df14d3fdd8)

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

>>>>>>> fa4b0e6272d5bc351035969099a33365c67dffdc

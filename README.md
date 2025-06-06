![header](https://capsule-render.vercel.app/api?type=venom&color=timeGradient&height=300&section=header&text=SmartDeskterior&fontColor=333333&fontSize=90)                  
### Team 3. DeskMate(IOT Project)

<details>
  <summary><strong>📑 목차 (Table of Contents) 📑</strong></summary>

- [Project Overview](#project-overview)
- [System Requirements](#system-requirements)
- [Installation & Running](#installation--running)
- [기능 및 기술](#기능-및-기술)
  - [조명 제어(PWM)](#조명-제어)
  - [데스크 높이 제어(Linear Actuator, Ultrasonic Sensor)](#데스크-높이-제어)
  - [모니터 높이 제어(모니터 암 구조)](#모니터-높이-제어)
  - [사용자 커스텀 모드(RFID)](#사용자-커스텀-모드)
  - [UI(Serial Communication, TCP)](#ui)
- [문제 상황 및 해결 방안](#문제-상황-및-해결-방안)
  - [TCP 포트](#tcp-포트)
  - [하드웨어 이슈](#하드웨어-이슈)
- [프로젝트 운영](#프로젝트-운영)
  - [Skill Set](#skill-set)
  - [Members](#members)
  - [Process](#process)
- [프로젝트 설계](#프로젝트-설계)
  - [System Architecture](#system-architecture)
  - [Data Structure](#data-structure)
  - [Scenario_Sequnce Diagram](#scenario_sequnce-diagram)
  - [기구 설계](#기구-설계)

</details>

---

<h2>&#128194; Project Overview &#128194;</h2>

> **Smart DeskTerior**는 IoT 기술을 통해 데스크 주변 환경(높낮이, 모니터 각도, 조명 등)을 자동·수동 제어하여 사용자의 편의와 생산성을 높이는 프로젝트입니다. **Deskterior**란 사무실 책상을 꾸민다는 의미에서 나온 용어로, Desk와 Interior의 합성어입니다. 현재는 가시적인 예쁨, 즉 눈에 예쁜 디자인적인 측면이 강조되고 있는데 **자동화**라는 부분을 추가하여 편의성을 더 해 책상을 세팅할 수 있으면 어떨까 생각을 해 프로젝트를 진행하게 되었습니다.

> 현존하는 스마트 데스크들의 경우 사람들의 키에 맞춰 높이 조절의 기능만 존재하지만 이 프로젝트는 컴퓨터를 많이 사용하는 현대인들을 고려하여 모니터의 높이, 조명 밝기까지 함께 연동하여 설정하고 그 값을 저장하여 불러올 수 있도록 합니다. 더 편안한 컴퓨터 작업과 컴퓨터 외에도 더 다양한 작업을 할 수 있도록 만들었습니다.

<h4>System Requirements</h4>

> - 하드웨어: 센서(거리), 모터(리니어 액추에이터, 서보 등), RFID 리더기, 마이크로컨트롤러(Arduino, ESP32 등)  
> - 소프트웨어: Python(Flask, PyQt), C++(임베디드), MySQL/ Amazon RDS, Jira/Confluence/Slack(협업 툴)

|ID|Function|Description|
|-----|-----|-----|
|SR_01|조명 밝기 제어|사용자의 기분, 시간대, 작업 모드(업무, 게임, 독서 등)에 따라 조명 밝기를 변경|
|SR_02|데스크 높낮이 제어|앉아 있을 때, 서 있을 때, 사람의 키에 따라 데스크 높이 조절<br>기본 설정 값 : 100<br><br>Min : 100<br>Max : 150|
|SR_03|모니터 높낮이 제어|사용하는 모드, 자세, 키에 따라 모니터의 높이를 제어|
|SR_04|모니터 각도 제어|사용하는 모드, 자세, 키, 모니터 높이에 따라 모니터의 각도를 제어|
|SR_05|데스크 제어를 위한 사용자 인터페이스|데스크에 부착되어 있는 버튼으로 사용자가 직접 수동으로 제어<br>데스크에 내장되어 있는 터치 스크린으로 사용자가 데스크에서 제어<br>사용자의 컴퓨터에서 원격으로 데스크 제어|
|SR_06|데스크 현재 정보 열람|현재 조명,모니터 높낮이, 모니터 각도,책상 높낮이의 정보를 컴퓨터 인터페이스에서 확인|
|SR_07|카드에 등록된 정보로 모드 제어|사용자의 정보, 모드가 저장되어 있는 카드를 꽂아 사용자가 저장한 모드를 불러와 그에 맞게 제어|
|SR_08|데스크 사용 기록 조회|데스크의 각종 기능을 제어했던 모든 사용기록을 조회|

<hr>

<h2>&#128187; Installation & Running &#128187;</h2>

1. **프로젝트 클론**
    ```bash
    git clone https://github.com/yourusername/smart-desk-project.git
    cd smart-desk-project
    ```
2. **하드웨어 연결**
    - 센서, 모터, RFID 리더기, 마이크로컨트롤러 등을 설계도에 맞게 연결
    - 전원, I/O 입출력 핀, 시리얼 통신 포트 확인

3. **소프트웨어 환경 세팅**
    - Python 라이브러리 설치  
      ```bash
      pip install -r requirements.txt
      ```
    - (선택) Arduino/ESP32 IDE 설정 후 펌웨어 업로드

4. **실행**
    - **Flask 서버** 및 **PyQt GUI** 실행  
      ```bash
      python app.py
      ```
    - 브라우저(또는 GUI 프로그램)에서 기능 테스트  

5. **기타**
    - DB(MySQL/Amazon RDS) 설정 파일(.env 등)에 접속 정보 기입
    - RFID 리더기, 모터 제어 라이브러리 등 외부 라이브러리 설치 여부 확인
  
      
<hr>

<h2>&#128297; 기능 및 기술 &#128297;</h2>
<h3>조명 제어</h3>
<table>
    <tr>
        <td width="25%" align="center">
            <h5>Desk GUI</h5>
        </td>
        <td width="25%" align="center">
            <h5>User GUI</h5>
        </td>
        <td width="25%" align="center">
            <h5>Hardware Interface</h5>
        </td>
        <td width="25%" align="center">
            <h4>Descriptions</h4>
        </td>
    </tr>
    <tr>
        <td>
            <img src="https://github.com/user-attachments/assets/1238bce0-ebc1-4886-9e4c-13424a6294ff" width="100%" />
        </td>
        <td>
            <img src="https://github.com/user-attachments/assets/7bdf66f1-a100-4dd6-a46d-4293261775a2" width="100%" />
        </td>
        <td>
            <img src="https://github.com/user-attachments/assets/8bc60f13-f97e-4401-8fcb-45f98584c128" width="100%" />
        </td>
        <td>
            <ul>
                <li>0 ~ 8 단계의 밝기로 조명 제어</li>
                <li>LED 밝기 제어는 max 밝기와 OFF 범위를 8단계로 나누어 값을 지정</li>
            </ul>
        </td>
    </tr>
</table>
<h5>PWM 제어</h5>

<h3>데스크 높이 제어</h3>
<table>
    <tr>
        <td width="25%" align="center">
            <h5>Desk GUI</h5>
        </td>
        <td width="25%" align="center">
            <h5>User GUI</h5>
        </td>
        <td width="25%" align="center">
            <h5>Hardware Interface</h5>
        </td>
        <td width="25%" align="center">
            <h4>Descriptions</h4>
        </td>
    </tr>
    <tr>
        <td>
            <img src="" width="100%" />
        </td>
        <td>
            <img src="" width="100%" />
        </td>
        <td>
            <img src="" width="100%" />
        </td>
        <td>
            <ul>
                <li>자신이 원하는 높이로 책상 높이를 맞춰 사용 할 수 있는 기능</li>
                <li>데스크 다리 제어 : 리니어 액추에이터</li>
                <li>책상 높이 측정 : 초음파센서</li>
            </ul>
        </td>
    </tr>
</table>
<h5>Linear Actuator</h5>
<h5>Ultrasonic Sensor</h5>

<h3>모니터 높이 제어</h3>
<table>
    <tr>
        <td width="25%" align="center">
            <h5>Desk GUI</h5>
        </td>
        <td width="25%" align="center">
            <h5>User GUI</h5>
        </td>
        <td width="25%" align="center">
            <h5>Hardware Interface</h5>
        </td>
        <td width="25%" align="center">
            <h4>Descriptions</h4>
        </td>
    </tr>
    <tr>
        <td>
            <img src="" width="100%" />
        </td>
        <td>
            <img src="" width="100%" />
        </td>
        <td>
            <img src="" width="100%" />
        </td>
        <td>
            <ul>
                <li>모니터 암이 책상에 연동되어 있어 따로 조절하지 않고 앉은 자리에서 원하는 높이, 각도로 제어 할 수 있는 기능</li>
                <li>2개의 서보 모터로 각각 높이, 각도를 제어</li>
            </ul>
        </td>
    </tr>
</table>
<h5>모니터 암 구성</h5>

<h3>사용자 커스텀 모드</h3>
<table>
    <tr>
        <td width="25%" align="center">
            <h5>Desk GUI</h5>
        </td>
        <td width="25%" align="center">
            <h5>User GUI</h5>
        </td>
        <td width="25%" align="center">
            <h5>Hardware Interface</h5>
        </td>
        <td width="25%" align="center">
            <h4>Descriptions</h4>
        </td>
    </tr>
    <tr>
        <td>
            <img src="" width="100%" />
        </td>
        <td>
            <img src="" width="100%" />
        </td>
        <td>
            <img src="" width="100%" />
        </td>
        <td>
            <ul>
                <li>사용자가 보유하고 있는 사용자 카드를 인식시키면 사용자 커스텀 모드 사용 가능</li>
                <li>User GUI에서는 값을 수정, 새로운 모드 저장 등 사용자 카드 내부 데이터 수정도 가능</li>
                <li>Desk GUI에서는 저장되어 있는 설정 적용만 가능</li>
                <li>사용자 카드는 RFID 카드, 인식은 RFID 안테나로 구성</li>
            </ul>
        </td>
    </tr>
</table>
<h5>RFID</h5>

<h3>UI</h3>
내용 정리 아직 안 됨

<hr>

<h2>&#128204; 문제 상황 및 해결 방안 &#128204;</h2>
<h3>TCP 포트</h3>
<h3></h3>
<h3>하드웨어 이슈</h3>


<hr>

<h2>&#128197; 프로젝트 운영 &#128197;</h2>
<h3>Skill Set</h3>

|Categories|SKills|
|------|------|
|개발환경|![Static Badge](https://img.shields.io/badge/linux-%23FCC624?style=plastic&logo=linux&logoColor=ffffff) ![Static Badge](https://img.shields.io/badge/ubuntu-22.04-grey?style=plastic&logo=ubuntu&logoColor=ffffff&labelColor=%23E95420) ![Static Badge](https://img.shields.io/badge/vsCode-%232185D0?style=plastic&logo=vscode&logoColor=ffffff) ![Static Badge](https://img.shields.io/badge/jupyter-%23F37626?style=plastic&logo=jupyter&logoColor=ffffff) ![Static Badge](https://img.shields.io/badge/arduino-sketchIDE-grey?style=plastic&logo=arduino&labelColor=%2300878F)|
|Design|![Static Badge](https://img.shields.io/badge/figma-%23F24E1E?style=plastic&logo=figma&logoColor=white) ![Static Badge](https://img.shields.io/badge/pyQT-Designer-grey?style=plastic&logo=qt&logoColor=white&labelColor=%2341CD52)|
|Data|![Static Badge](https://img.shields.io/badge/mysql-%234479A1?style=plastic&logo=mysql&logoColor=ffffff) ![Static Badge](https://img.shields.io/badge/amazonrds-%23527FFF?style=plastic&logo=amazonrds&logoColor=ffffff)|
|Programming Languages|![Static Badge](https://img.shields.io/badge/Python-%233776AB?style=plastic&logo=python&logoColor=ffffff) ![Static Badge](https://img.shields.io/badge/C%2B%2B-%2300599C?style=plastic&logo=cplusplus&logoColor=white)|
|Communication|![Static Badge](https://img.shields.io/badge/serial-grey?style=plastic) ![Static Badge](https://img.shields.io/badge/flask-%23000000?style=plastic&logo=flask&logoColor=%23FFFFFF)|
|Cooperation Tools|![Static Badge](https://img.shields.io/badge/jira-%230052CC?style=plastic&logo=jira&logoColor=ffffff) ![Static Badge](https://img.shields.io/badge/confluence-%23172B4D?style=plastic&logo=confluence&logoColor=ffffff) ![Static Badge](https://img.shields.io/badge/slack-%234A154B?style=plastic&logo=slack)|

<h3>Members</h3>

|구성원|역할|Contacts|
|-----|-----|-----|
|**이정림 (팀장)**|프로젝트 관리<br>Jira 관리<br>Desk GUI 설계<br>RFID : 사용자 인증, 커스텀 모드<br>User GUI 구현<br>TCP/IP 통신<br>Serial 통신|[JlimL(LeeJ)](https://github.com/JlimL) <br>[jeongliml2002@gmail.com](mailto:jeongliml2002@gmail.com)|
|**심채훈**|기구 설계<br>DB 설계<br>책상 높이 제어<br>Serial 통신<br>TCP/IP 통신<br>Desk GUI 구현|[Huni0128(심채훈)](https://github.com/Huni0128) <br>[tlacogns@gmail.com](mailto:tlacogns@gmail.com)|
|**이우재**|기구 설계<br>DB 설계<br>DB 관리<br>모니터 제어<br>Server 구현<br>발표|[woojaelee-k(이우재)](https://github.com/woojaelee-k) <br>[tedlee911@gmail.com](mailto:tedlee911@gmail.com)|
|**권 빛**|User GUI 설계<br>User GUI 구현<br>LED 제어<br>PPT 제작<br>GitHub 정리|[V2TAMIN(V2TAMIN)](https://github.com/V2TAMIN) <br>[k23909275@gmail.com](mailto:k23909275@gmail.com)|

<h3>Process</h3>
<img src="https://github.com/user-attachments/assets/1332319e-8ee2-49f0-9397-74eceacdb5a5" width="1000" align="center" />

<hr>

<h2>&#128221; 프로젝트 설계 &#128221;</h2>
<h3>System Architecture</h3>
<h3>Data Structure</h3>
<h3>Scenario_Sequnce Diagram</h3>
<h3>기구 설계</h3>






<br><br><br><br>
<hr>

하기 내용은 구성 확정 되면 삭제할 내용
---

## :computer: Skill Set
|Categories|SKills|
|------|------|
|개발환경|![Static Badge](https://img.shields.io/badge/linux-%23FCC624?style=plastic&logo=linux&logoColor=ffffff) ![Static Badge](https://img.shields.io/badge/ubuntu-22.04-grey?style=plastic&logo=ubuntu&logoColor=ffffff&labelColor=%23E95420) ![Static Badge](https://img.shields.io/badge/vsCode-%232185D0?style=plastic&logo=vscode&logoColor=ffffff) ![Static Badge](https://img.shields.io/badge/jupyter-%23F37626?style=plastic&logo=jupyter&logoColor=ffffff) ![Static Badge](https://img.shields.io/badge/arduino-sketchIDE-grey?style=plastic&logo=arduino&labelColor=%2300878F)|
|Design|![Static Badge](https://img.shields.io/badge/figma-%23F24E1E?style=plastic&logo=figma&logoColor=white) ![Static Badge](https://img.shields.io/badge/pyQT-Designer-grey?style=plastic&logo=qt&logoColor=white&labelColor=%2341CD52)|
|Data|![Static Badge](https://img.shields.io/badge/mysql-%234479A1?style=plastic&logo=mysql&logoColor=ffffff) ![Static Badge](https://img.shields.io/badge/amazonrds-%23527FFF?style=plastic&logo=amazonrds&logoColor=ffffff)|
|Programming Languages|![Static Badge](https://img.shields.io/badge/Python-%233776AB?style=plastic&logo=python&logoColor=ffffff) ![Static Badge](https://img.shields.io/badge/C%2B%2B-%2300599C?style=plastic&logo=cplusplus&logoColor=white)|
|Communication|![Static Badge](https://img.shields.io/badge/serial-grey?style=plastic) ![Static Badge](https://img.shields.io/badge/flask-%23000000?style=plastic&logo=flask&logoColor=%23FFFFFF)|
|Cooperation Tools|![Static Badge](https://img.shields.io/badge/jira-%230052CC?style=plastic&logo=jira&logoColor=ffffff) ![Static Badge](https://img.shields.io/badge/confluence-%23172B4D?style=plastic&logo=confluence&logoColor=ffffff) ![Static Badge](https://img.shields.io/badge/slack-%234A154B?style=plastic&logo=slack)|

---

## :sparkles: 구성원 및 역할
|구성원|역할|Contacts|
|-----|-----|-----|
|**이정림 (팀장)**|프로젝트 관리<br>Jira 관리<br>Desk GUI 설계<br>RFID : 사용자 인증, 커스텀 모드<br>User GUI 구현<br>TCP/IP 통신<br>Serial 통신||
|**심채훈**|기구 설계<br>DB 설계<br>책상 높이 제어<br>Serial 통신<br>TCP/IP 통신<br>Desk GUI 구현||
|**이우재**|기구 설계<br>DB 설계<br>DB 관리<br>모니터 제어<br>Server 구현<br>발표||
|**권 빛**|User GUI 설계<br>User GUI 구현<br>LED 제어<br>PPT 제작<br>GitHub 정리||

---

# IOT 스마트데스크 프로젝트

![001](https://github.com/user-attachments/assets/04697113-9218-4869-9034-3c32d54ac885)

### [프로젝트 목차]
![iot-스마트-데스크-002 (4)](https://github.com/user-attachments/assets/d9d94928-24ab-492e-971f-fd9b2e702c35)

## 1. 프로젝트 소개
IOT 스마트데스크 프로젝트는 사용자의 업무 및 학습 환경을 쾌적하게 만들기 위해 센서와 IoT 기술을 활용해 데스크 주변 환경을 자동으로 제어하는 시스템입니다.

![004](https://github.com/user-attachments/assets/81693ffc-63af-4ad8-8af7-6059edefb550)
![005](https://github.com/user-attachments/assets/c9bbb441-56bc-4773-8675-b5718d973a4a)

주요 기능은 **조명 제어**, **데스크 높낮이 및 모니터 각도 제어**, **사용자 인식 기능** 등을 포함하며, 사용자의 편의와 생산성 향상을 목표로 합니다.

## 2. 프로젝트 설계

### 2-1. Scenario
- **RFID SUCCESS**  
  ![Image](https://github.com/user-attachments/assets/19a7bb6e-49a2-461e-82b3-b331f8d1313a)                             

- **RFID ERROR**  
  ![Image](https://github.com/user-attachments/assets/768b0ca8-4562-4f66-b15c-38c2368a37e5)                            

- **Manual Control Success**  
  ![Image](https://github.com/user-attachments/assets/60edacdf-2391-4af6-bd41-50f43be6db3b)                           

- **Hardware ERROR**  
  ![Image](https://github.com/user-attachments/assets/7b8617cd-9413-4d3d-bbfc-0b6e83224b6b)                         

### 2-2. System Requirements
> - 하드웨어: 센서(조도, 거리, 무게), 모터(리니어 액추에이터, 서보 등), RFID 리더기, 마이크로컨트롤러(Arduino, ESP32 등)  
> - 소프트웨어: Python(Flask, PyQt), C++(임베디드), MySQL/ Amazon RDS, Jira/Confluence/Slack(협업 툴)


|ID|Function|Description|
|-----|-----|-----|
|SR_01|조명 밝기 제어|사용자의 기분, 시간대, 작업 모드(업무, 게임, 독서 등)에 따라 조명 밝기를 변경|
|SR_02|데스크 높낮이 제어|앉아 있을 때, 서 있을 때, 사람의 키에 따라 데스크 높이 조절<br>기본 설정 값 : 100<br><br>Min : 100<br>Max : 150|
|SR_03|모니터 높낮이 제어|사용하는 모드, 자세, 키에 따라 모니터의 높이를 제어|
|SR_04|모니터 각도 제어|사용하는 모드, 자세, 키, 모니터 높이에 따라 모니터의 각도를 제어|
|SR_05|데스크 제어를 위한 사용자 인터페이스|데스크에 부착되어 있는 버튼으로 사용자가 직접 수동으로 제어<br>데스크에 내장되어 있는 터치 스크린으로 사용자가 데스크에서 제어<br>사용자의 컴퓨터에서 원격으로 데스크 제어|
|SR_06|데스크 현재 정보 열람|현재 조명,모니터 높낮이, 모니터 각도,책상 높낮이의 정보를 컴퓨터 인터페이스에서 확인|
|SR_07|카드에 등록된 정보로 모드 제어|사용자의 정보, 모드가 저장되어 있는 카드를 꽂아 사용자가 저장한 모드를 불러와 그에 맞게 제어|
|SR_08|데스크 사용 기록 조회|데스크의 각종 기능을 제어했던 모든 사용기록을 조회|

### 2-3. System Architecture
- **하드웨어 구조**  
  ![Image](https://github.com/user-attachments/assets/1266ac6a-ce54-477e-8a54-9d3f5cb76b88)

- **소프트웨어 구조**  
   ![Image](https://github.com/user-attachments/assets/ad806e1d-4484-4053-9f55-4f44a2ff73a2)

### 2-4. Desk 기구설계
![Image](https://github.com/user-attachments/assets/58cbd91a-8c2e-4470-9615-f38e8b717d34)

### 2-5. GUI 화면 설계
- **Desk GUI**  
  ![Image](https://github.com/user-attachments/assets/a4cfb278-3b02-491c-bfa8-2bf264f3b5bb)  
  ![Image](https://github.com/user-attachments/assets/3dc70b8c-56c4-4881-a520-494bb41ab218)  
  ![Image](https://github.com/user-attachments/assets/bb876e61-491b-49b0-bef2-4f989fec1e86)  
  ![Image](https://github.com/user-attachments/assets/77213b30-df7d-41c1-99f2-b588ba3f5f26)  
  ![Image](https://github.com/user-attachments/assets/28a7e275-4b12-4d80-8b63-f6083eb957ab)

- **User GUI**  
  ![Image](https://github.com/user-attachments/assets/9b633cb9-929b-46c4-a888-866ce1624e2d)  
  ![Image](https://github.com/user-attachments/assets/803766fb-a3a0-4b93-ace6-d8df14d3fdd8)

## 3. 프로젝트 기능 설명

### 3-1. 조명 제어

1. **기존 책상 조명의 문제점**  
   - 사용자가 직접 움직여서 조명을 제어해야 하는 번거로움이 존재

https://github.com/user-attachments/assets/33a42b2f-9539-4258-b7b3-ef4e926df855

2. **터치스크린을 통한 조명 제어**  
   - 책상에 내장된 **터치스크린**을 이용해 0~7단계까지 조명의 밝기를 간편하게 조절

https://github.com/user-attachments/assets/51f67d94-2979-4021-9bb7-58c132e7f8e4


3. **사용자 PC를 통한 조명 제어**  
   - 사용자의 **컴퓨터 화면**에서 소프트웨어 UI를 통해 0~7단계까지 조명의 밝기를 제어


https://github.com/user-attachments/assets/92a1c9a8-aff3-4fbc-accb-ef3e1bebb798


4. **HW 버튼을 통한 조명 제어**  
   - 책상 측면에 위치한 **하드웨어 버튼**으로 0~7단계까지 조명의 밝기를 조절 가능


https://github.com/user-attachments/assets/8bebd767-6dcf-4125-a794-76780d90f5cc



### 3-2. 데스크 높낮이 제어
- 모터와 리니어 액추에이터를 활용하여 데스크의 높낮이를 자동 조절  
- 사용자 맞춤 프로필(신장, 자세)에 따라 최적 높이로 자동 세팅  

### 3-3. 모니터 높낮이·각도 제어
- 서보 모터를 통해 모니터의 각도와 높이를 조절  
- 집중 모드, 회의 모드 등 시나리오에 따라 미리 설정된 각도로 자동 전환  

### 3-4. 사용자 인식
- 거리 센서, 무게 센서, 혹은 카메라 모듈(선택 사항)을 통해 사용자가 책상 앞에 있는지 감지  
- 사용자 부재 시 에너지 절약 모드(조명·모니터 전원 자동 오프)  

## 4. 추가 개선점 
  - 현재 무선 통신 부분은 flask를 사용하고 있는데 이를 tcp/ip socket 통신으로 변경하여 사용하도록 수정을 하는게 좋을 것 같다
  - 계획했던 기능들 중에 구현하지 못 한 기능들이 있는데 이를 추가적으로 더 개발하여 완성도가 있었으면 좋을 것 같다
  - 통신 프로토콜을 정확하게 정하고 통신을 먼저 세팅을 다 한 다음에 다른 개발을 진행했으면 이후 프로젝트 진행이 더 수월했을 것 같다

---

## 설치 및 실행 방법
1. **프로젝트 클론**
    ```bash
    git clone https://github.com/yourusername/smart-desk-project.git
    cd smart-desk-project
    ```
2. **하드웨어 연결**
    - 센서, 모터, RFID 리더기, 마이크로컨트롤러 등을 설계도에 맞게 연결
    - 전원, I/O 입출력 핀, 시리얼 통신 포트 확인

3. **소프트웨어 환경 세팅**
    - Python 라이브러리 설치  
      ```bash
      pip install -r requirements.txt
      ```
    - (선택) Arduino/ESP32 IDE 설정 후 펌웨어 업로드

4. **실행**
    - **Flask 서버** 또는 **PyQt GUI** 실행  
      ```bash
      python app.py
      ```
    - 브라우저(또는 GUI 프로그램)에서 기능 테스트  

5. **기타**
    - DB(MySQL/Amazon RDS) 설정 파일(.env 등)에 접속 정보 기입
    - RFID 리더기, 모터 제어 라이브러리 등 외부 라이브러리 설치 여부 확인

---


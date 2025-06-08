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

<h2>&#128297; 기능 및 기술 &#128297;</h2>
<h3>조명 제어</h3>
<table>
    <tr>
        <td width="25%" align="center">
            <h4>Desk GUI</h4>
        </td>
        <td width="25%" align="center">
            <h4>User GUI</h4>
        </td>
        <td width="25%" align="center">
            <h4>Hardware Interface</h4>
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
<h4>PWM 제어</h4>

<h3>데스크 높이 제어</h3>
<table>
    <tr>
        <td width="25%" align="center">
            <h4>Desk GUI</h4>
        </td>
        <td width="25%" align="center">
            <h4>User GUI</h4>
        </td>
        <td width="25%" align="center">
            <h4>Hardware Interface</h4>
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
<h4>Linear Actuator</h4>
<h4>Ultrasonic Sensor</h4>

<h3>모니터 높이 제어</h3>
<table>
    <tr>
        <td width="25%" align="center">
            <h4>Desk GUI</h4>
        </td>
        <td width="25%" align="center">
            <h4>User GUI</h4>
        </td>
        <td width="25%" align="center">
            <h4>Hardware Interface</h4>
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
<h4>모니터 암 구성</h4>

<h3>사용자 커스텀 모드</h3>
<table>
    <tr>
        <td width="50%" align="center">
            <h4>User GUI</h4>
        </td>
        <td width="50%" align="center">
            <h4>Descriptions</h4>
        </td>
    </tr>
    <tr>
        <td>
            <img src="https://github.com/user-attachments/assets/0e66e1ca-7183-4226-ab3f-345eb089fa78" width="100%" />
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
<h4>RFID</h4>

<h3>Desk GUI</h3>
<table>
  <tr>
    <td width="40%" rowspan="6">
      <img src="https://github.com/user-attachments/assets/3f5862aa-0df3-4459-a861-0e9df2792f64" width="100%" />
    </td>
    <td width="10%">
      <h4>No.</h4>
    </td>
    <td width="50%">
      <h4>Descriptions</h4>
    </td>
  </tr>
  <tr>
    <td>01</td>
    <td>RFID tag 후 읽어 온 UID 출력</td>
  </tr>
  <tr>
    <td>02</td>
    <td>Mode1 클릭 시 RFID tag에 저장되어 있는 Mode1 Setting 값 읽어 와 그 값에 따라 세팅</td>
  </tr>
  <tr>
    <td>03</td>
    <td>Mode2 클릭 시 RFID tag에 저장되어 있는 Mode2 Setting 값 읽어 와 그 값에 따라 세팅</td>
  </tr>
  <tr>
    <td>04</td>
    <td>Mode3 클릭 시 RFID tag에 저장되어 있는 Mode3 Setting 값 읽어 와 그 값에 따라 세팅</td>
  </tr>
  <tr>
    <td>05</td>
    <td>Control Mode 클릭 시 제어 할 기기 선택하는 화면으로 전환</td>
  </tr>
</table>

<table>
  <tr>
    <td width="20%" rowspan="5">
      <img src="https://github.com/user-attachments/assets/0430f6ed-a318-4afb-830b-836dbc6aa0ef" width="100%" />
    </td>
    <td width="10%">
      <h4>No.</h4>
    </td>
    <td width="20%">
      <h4>Descriptions</h4>
    </td>
    <td width="20%" rowspan="5">
      <img src="https://github.com/user-attachments/assets/a39af12d-e647-4bf2-ba0e-cf3bc9f5cd72" width="100%" />
    </td>
    <td width="10%">
      <h4>No.</h4>
    </td>
    <td width="20%">
      <h4>Descriptions</h4>
    </td>
  </tr>
  <tr>
    <td>01</td>
    <td>클릭 시 LED 수동 조작 화면으로 전환</td>
    <td>01</td>
    <td>클릭 시 Brightness 값 증가</td>
  </tr>
  <tr>
    <td>02</td>
    <td>Desk 클릭 시 Desk 수동 조작 화면으로 전환</td>
    <td>02</td>
    <td>현재 LED Brightness 값 표시</td>
  </tr>
  <tr>
    <td>03</td>
    <td>Monitor 클릭 시 Monitor 수동 조작 화면으로 전환</td>
    <td>03</td>
    <td>클릭 시 Brightness 값 감소</td>
  </tr>
  <tr>
    <td>04</td>
    <td>Back 클릭 시 Main Screen으로 화면 전환</td>
    <td>04</td>
    <td>Back 클릭 시 Control Mode 화면으로 전환</td>
  </tr>
  <tr>
    <td width="20%" rowspan="6">
      <img src="https://github.com/user-attachments/assets/f2065699-4fda-4c8d-bb11-c6dd5e19bdec" width="100%" />
    </td>
    <td width="10%">
      <h4>No.</h4>
    </td>
    <td width="20%">
      <h4>Descriptions</h4>
    </td>
    <td width="20%" rowspan="6">
      <img src="https://github.com/user-attachments/assets/e436507e-b334-41d3-9fb7-661a61532d03" width="100%" />
    </td>
    <td width="10%">
      <h4>No.</h4>
    </td>
    <td width="20%">
      <h4>Descriptions</h4>
    </td>
  </tr>
  <tr>
    <td rowspan="2">01</td>
    <td rowspan="2">클릭 시 Desk 높이 증가</td>
    <td>01</td>
    <td>클릭 시 Monitor Arm 전진</td>
  </tr>
  <tr>
    <td>02</td>
    <td>클릭 시 Monitor Arm 후퇴</td>
  </tr>
  <tr>
    <td rowspan="2">02</td>
    <td rowspan="2">클릭 시 Desk 높이 감소</td>
    <td>03</td>
    <td>클릭 시 Monitor Arm 높이 증가</td>
  </tr>
  <tr>
    <td>04</td>
    <td>클릭 시 Monitor Arm 높이 감소</td>
  </tr>
  <tr>
    <td>03</td>
    <td>Back 클릭 시 Control Mode 화면으로 전환</td>
    <td>05</td>
    <td>Back 클릭 시 Control Mode 화면으로 전환</td>
  </tr>
</table>

<h3>User GUI</h3>
<table>
  <tr>
    <td width="50%" rowspan="14">
      <img src="https://github.com/user-attachments/assets/db2515b8-7987-42df-9f03-f93c7b914587" width="100%" />
    </td>
    <td width="10%">
      <h4>No.</h4>
    </td>
    <td width="40%">
      <h4>Descriptions</h4>
    </td>
  </tr>
  <tr>
    <td>01</td>
    <td>User GUI Main 화면으로 이동</td>
  </tr>
  <tr>
    <td>02</td>
    <td>LED Brightness 값을 표시</td>
  </tr>
  <tr>
    <td>03</td>
    <td>LED의 Brightness 값 수정</td>
  </tr>
  <tr>
    <td>04</td>
    <td>Desk Height 값 표시</td>
  </tr>
  <tr>
    <td>05</td>
    <td>Desk Height 값 수정</td>
  </tr>
  <tr>
    <td>06</td>
    <td>Monitor Tilt 값 표시</td>
  </tr>
  <tr>
    <td>07</td>
    <td>Monitor Tilt 값 수정</td>
  </tr>
  <tr>
    <td>08</td>
    <td>Monitor Height 값 표시</td>
  </tr>
  <tr>
    <td>09</td>
    <td>Monitor Height 값 수정</td>
  </tr>
  <tr>
    <td>10</td>
    <td>사용자의 RFID UID 값 표시(로그인 시, 로그인 안 할 시 None 출력)</td>
  </tr>
  <tr>
    <td>11</td>
    <td>클릭 시 사용자가 저장한 모드로 전환</td>
  </tr>
  <tr>
    <td>12</td>
    <td>SAVE 클릭 시 사용자가 변경한 설정 값으로 해당 모드 설정 값 수정</td>
  </tr>
  <tr>
    <td>13</td>
    <td>LOG 클릭 시 로그 데이터 확인 화면으로 이동</td>
  </tr>
  <tr>
    <td rowspan="6">
      <img src="https://github.com/user-attachments/assets/a5b6869e-82cb-4d91-92be-9afcc53c848f" width="100%" />
    </td>
    <td>
      <h4>No.</h4>
    </td>
    <td>
      <h4>Descriptions</h4>
    </td>
  </tr>
  <tr>
    <td>01</td>
    <td>User GUI Main 화면으로 이동</td>
  </tr>
  <tr>
    <td>02</td>
    <td>RFID tag에서 읽어 온 UDI 출력</td>
  </tr>
  <tr>
    <td>03</td>
    <td>현재 화면이 Log Data 확인을 위한 화면임을 출력</td>
  </tr>
  <tr>
    <td>04</td>
    <td>사용자의 LogData 표시</td>
  </tr>
  <tr>
    <td>05</td>
    <td>Back 클릭 시 User GUI Main 화면으로 이동</td>
  </tr>
</table>

<hr>

<h2>&#128204; 문제 상황 및 해결 방안 &#128204;</h2>
<h3>통신 구현 방법 변경</h3>
<table>
  <tr>
    <td width="50%">
      <h4>문제</h4>
    </td>
    <td width="50%">
      <h4>해결 방안</h4>
    </td>
  </tr>
  <tr>
    <td></td>
    <td>
      <ul>
        <li></li>
      </ul>
    </td>
  </tr>
</table>
<h3>TCP 포트</h3>
<table>
  <tr>
    <td width="50%">
      <h4>문제</h4>
    </td>
    <td width="50%">
      <h4>해결 방안</h4>
    </td>
  </tr>
  <tr>
    <td></td>
    <td>
      <ul>
        <li></li>
      </ul>
    </td>
  </tr>
</table>
<h3>하드웨어 이슈</h3>
<table>
  <tr>
    <td width="50%">
      <h4>문제</h4>
    </td>
    <td width="50%">
      <h4>해결 방안</h4>
    </td>
  </tr>
  <tr>
    <td></td>
    <td>
      <ul>
        <li></li>
      </ul>
    </td>
  </tr>
</table>

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
<table>
  <tr>
    <td width="60%">
      <img src="https://github.com/user-attachments/assets/ae15ac57-8930-46a8-8983-72196175a49d" width="100%" />
    </td>
    <td width="40%">
      <ul>
        <li>2개의 아두이노 보드, 1개의 라즈베리파이 보드, 1대의 컴퓨터, 1대의 데스크 본체로 시스템 이루어짐</li>
        <li>아두이노 보드와 라즈베리파이 보드는 데스크 내부에 부착되어 있음</li>
        <li>데스크 내부에서는 시리얼 통신으로, 데스크 외부로의 통신은 TCP 통신으로 설계</li>
      </ul>
    </td>
  </tr>
</table>

<h3>Data Structure</h3>
<table>
  <tr>
    <td width="60%">
      <img src="https://github.com/user-attachments/assets/719aea29-7bdc-4645-8d62-51c75d060e66" width="100%" />
    </td>
    <td width="40%">
      <ul>
        <li>
          desk_info : 데스크 자체의 정보 관리
          <ul>
            <li>데스크 ID : 데스크의 제품 번호</li>
            <li>데스크의 기본 상태 값들 저장</li>
          </ul>
        </li>
        <li>
          log : 데스크 사용 정보 관리
          <ul>
            <li>데스크 유저 ID : RFID UID 값으로 저장, 없을 시 None으로 저장</li>
            <li>사용한 상태 값 저장</li>
            <li>해당 상태로 변경한 시간 저장</li>
          </ul>
        </li>
      </ul>
    </td>
  </tr>
</table>

<h3>Scenario_Sequnce Diagram</h3>
<table>
  <tr>
    <td width="30%">
      <img src="https://github.com/user-attachments/assets/8744f662-0af8-473c-b4d1-b297bcfb29c9" width="100%" />
    </td>
    <td width="20%">
      <ul>
        <li></li>
      </ul>
    </td>
    <td width="30%">
      <img src="https://github.com/user-attachments/assets/b0fc3c40-131f-4e0f-ad19-5d2f4485f51b" width="100%" />
    </td>
    <td width="20%">
      <ul>
        <li></li>
      </ul>
    </td>
  </tr>
  <tr>
    <td width="30%">
      <img src="https://github.com/user-attachments/assets/4a610bb0-7941-43dc-a53d-c7d439236e71" width="100%" />
    </td>
    <td width="20%">
      <ul>
        <li></li>
      </ul>
    </td>
    <td width="30%">
      <img src="https://github.com/user-attachments/assets/10e5d2d1-b996-4657-ba7b-eb58e94a8be0" width="100%" />
    </td>
    <td width="20%">
      <ul>
        <li></li>
      </ul>
    </td>
  </tr>
</table>

<h3>기구 설계</h3>
<table>
  <tr>
    <td wisth=20%">
      <h4>leg_mount1</h4>
    </td>
    <td width="20%">
      <h4>leg_mount2</h4>
    </td>
    <td width="20%">
      <h4>servo_mount</h4>
    </td>
    <td width="40%">
      <h4>assembly</h4>
    </td>
  </tr>
  <tr>
    <td>
      <img src="https://github.com/user-attachments/assets/2de5a670-41c2-4302-8178-40975545be6c" width="100%" />
    </td>
    <td>
      <img src="https://github.com/user-attachments/assets/48b52ef1-e40d-48f1-bae5-3e58ee4ca324" width="100%" />
    </td>
    <td>
      <img src="https://github.com/user-attachments/assets/3615c3ed-7c07-43c4-9ecc-56e372215a1f" width="100%" />
    </td>
    <td rowspan="3">
      <img src="https://github.com/user-attachments/assets/36d5a7d9-1f09-4abb-bac9-d65590ee90f6" width="100%" />
    </td>
  </tr>
  <tr>
    <td>
      <h4>servo1_fix</h4>
    </td>
    <td>
      <h4>servo1_fly</h4>
    </td>
    <td>
      <h4>servo2_fix</h4>
    </td>
  </tr>
  <tr>
    <td>
      <img src="https://github.com/user-attachments/assets/c48867fd-b5c2-42ce-8014-47aa64276784" width="100%" />
    </td>
    <td>
      <img src="https://github.com/user-attachments/assets/455b4dbf-581e-4ee4-80c5-ab72f948f26b" width="100%" />
    </td>
    <td>
      <img src="https://github.com/user-attachments/assets/8ef58288-e3e4-447e-89b0-3c1179a14eae" width="100%" />
    </td>
  </tr>
</table>



![header](https://capsule-render.vercel.app/api?type=blur&color=timeGradient&height=300&section=header&text=ThankYou&fontColor=333333&fontSize=90) 

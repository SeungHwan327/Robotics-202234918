   # 261122 — ROS 2 Launch, Service 및 사용자 정의 인터페이스 실습

> **강의:** 로봇 자율주행: 고수준 판단 및 저수준 제어  
> **실습일:** 2026년 11월 22일  
> **작성자:** 가천대학교 인공지능학과 이승환  
> **주요 내용:** Publisher–Processor–Subscriber, Launch, Service, Custom Message, 로봇 위치 계산

## 1. 실습 개요와 학습 목표

이번 실습은 ROS 2의 기본 발행·구독 구조를 확장하여 여러 노드를 연결하고, Launch 파일로 함께 실행하는 방법을 다룬다. 또한 사용자 정의 메시지와 서비스를 만들고 Python 클라이언트·서버에서 사용하면서, 데이터의 형식과 통신 구조가 어떻게 연결되는지 학습한다.

기본 Topic 실습은 `talker.py`와 `listener.py` 사이에서 문자열을 전달한다. 확장 Topic 실습은 `publisher.py`가 두 정수를 전달하고, `processor.py`가 합을 계산하여 다시 발행하며, `subscriber.py`가 결과를 출력하는 구조이다. Service 실습에서는 요청과 응답을 명확하게 나누어 두 정수의 합과 로봇의 이동 후 위치를 계산한다.

학습 목표는 다음과 같다.

- 하나의 패키지에 여러 Python 노드를 구성하는 방법을 이해한다.
- Topic 기반 데이터 처리와 Service 기반 요청·응답의 차이를 설명한다.
- Python Launch 파일의 역할과 실행 명령 형식을 이해한다.
- `.msg`와 `.srv`를 이용해 사용자 정의 인터페이스를 정의한다.
- 중첩 메시지의 필드에 접근하는 방법을 이해한다.
- 비동기 서비스 호출과 Future의 처리 과정을 설명한다.
- 위치·방향·이동 거리로 새로운 2차원 위치를 계산한다.
- Python 실행 패키지와 인터페이스 생성 패키지의 빌드 역할을 구분한다.




## 2. 실습 자료와 파일별 역할

### 2.1 Topic 및 Launch 실습

| 파일 | 역할 | 확인 근거 |
| --- | --- | --- |
| `talker.py` | 문자열 메시지를 주기적으로 발행 | 제공된 기존 코드 |
| `listener.py` | 문자열 메시지를 구독하여 출력 | 제공된 기존 코드 |
| `publisher.py` | 입력한 두 정수를 메시지로 전달 | 추가 수업 설명 |
| `processor.py` | 두 정수를 수신하고 덧셈 결과를 발행 | 추가 수업 설명 |
| `subscriber.py` | 계산 결과를 수신하여 출력 | 추가 수업 설명 |
| 이름 미확인의 `.launch.py` | 숫자 처리 노드 3개를 함께 실행 | 추가 수업 설명 및 강의 노트 |

위 Python 파일 5개는 `1_pubsub`에 속하는 하나의 Python 모듈 폴더 안에 함께 두는 구성으로 이해한다. Launch 파일은 보통 패키지 루트의 `launch/`에서 별도로 관리한다. 

### 2.2 Service 구현 파일

| 파일 | 기능 | 사용하는 인터페이스 |
| --- | --- | --- |
| `add_ints_server.py` | 두 정수의 합을 계산해 응답 | `AddTwoInts` |
| `add_ints_client.py` | 명령행의 두 정수를 요청으로 전달 | `AddTwoInts` |
| `move_robot_server.py` | 현재 방향으로 이동한 위치를 계산 | `MoveRobot` |
| `move_robot_client.py` | 위치·방향·거리를 전달하고 결과 출력 | `MoveRobot` |

### 2.3 메시지·서비스 정의 파일

| 파일 | 정의하는 데이터 |
| --- | --- |
| `Num.msg` | `int64 my_num` |
| `RobotPose.msg` | `float64 x`, `float64 y`, `float64 theta` |
| `AddTwoInts.srv` | 두 `Num`을 요청하고 합을 `Num`으로 응답 |
| `MoveRobot.srv` | 현재 자세와 거리를 요청하고 결과 자세·성공 여부 응답 |

### 2.4 패키지 설정과 테스트

| 전달된 파일명 | 파일 내용의 소속·역할 |
| --- | --- |
| `setup.py` | `2_srvmsg`의 Python 설치 및 실행 진입점 |
| `setup.cfg` | `2_srvmsg` 실행 파일 설치 위치 |
| `package(1).xml` | `2_srvmsg` 의존성과 `ament_python` 선언 |
| `package(2).xml` | `custom_interfaces` 의존성과 `ament_cmake` 선언 |
| `CMakeLists.txt` | 메시지 2개·서비스 2개의 인터페이스 코드 생성 |
| `test_copyright(1).py` | 저작권 헤더 검사, 현재 skip 처리 |
| `test_flake8(1).py` | Python 스타일 검사 |
| `test_pep257(1).py` | Python docstring 검사 |

전달된 이름의 `(1)`, `(2)`는 같은 이름의 첨부 파일을 구분하는 표기이다. ROS 패키지 안에서는 각 패키지에 맞는 `setup.py`, `setup.cfg`, `package.xml`과 같은 표준 파일명을 사용한다. 서로 다른 두 `package.xml`을 한 패키지의 동일한 위치에 겹쳐 두는 구조가 아니다.

## 3. 이론 — Node, Topic과 데이터 처리

### 3.1 Node와 역할 분리

Node는 로봇 시스템에서 특정 기능을 수행하는 소프트웨어 구성 요소이다. 입력, 계산, 출력을 별도 노드로 나누면 각 기능을 독립적으로 확인할 수 있다.

이번 숫자 처리 구조에서는 입력 방식이 바뀌더라도 계산 노드를 재사용할 수 있고, 출력 노드를 다른 표시 장치나 기록 노드로 확장할 수 있다. 각 노드는 다른 노드의 내부 변수에 직접 접근하는 대신 메시지를 통해 정보를 전달한다.

노드 하나가 반드시 프로세스 하나나 터미널 하나를 의미하는 것은 아니다. Launch도 여러 노드의 실행을 관리하는 도구이지, 노드들을 하나의 함수로 합치는 기능은 아니다.

### 3.2 Topic과 Message

Topic은 메시지를 발행·구독하는 이름 있는 통신 채널이다. Message는 전달할 데이터의 형식을 정의한다. 통신하려는 노드 사이에서는 토픽 이름과 메시지 타입, QoS 등의 조건이 맞아야 한다.

| 역할 | 동작 |
| --- | --- |
| Publisher | 메시지를 생성하여 토픽에 발행 |
| Subscriber | 토픽을 구독하고 수신 콜백에서 처리 |
| Processor | 입력 토픽을 구독하고 결과 토픽을 발행 |

`processor.py`는 파일명으로 역할을 나타낸다. ROS 2에 Processor라는 별도 통신 API가 있는 것이 아니라, 하나의 노드 안에서 Subscriber와 Publisher를 함께 사용하는 구성이다.

### 3.3 두 정수를 배열로 전달하는 의미

두 정수를 하나의 메시지에 묶으면 같은 계산에 사용할 입력 쌍을 함께 전달할 수 있다. 개념적으로 수신 데이터가 `[a, b]`라면 계산은 `a + b`이다.

예를 들어 `std_msgs/msg/Int32MultiArray`나 `Int64MultiArray`는 정수 배열을 담을 수 있는 표준 메시지이다. 그러나 이번 배열 실습에서 실제로 사용한 타입은 원본이 없어 확정할 수 없다. 아래에서 사용하는 `[a, b]`는 데이터 구조의 개념 표현이다.

Python의 `int`와 ROS 메시지의 정수 타입도 구분해야 한다. ROS 필드는 `int32`, `int64` 등으로 표현 범위가 정해질 수 있다. 제공된 `Num.msg`의 실제 필드는 `int64`이지만, 이것이 앞선 배열 실습의 타입까지 증명하는 것은 아니다.

## 4. 이론 — Launch 파일과 여러 노드 실행

### 4.1 Launch의 역할

노드가 늘어나면 각각 실행하고 설정을 반복하는 작업이 복잡해진다. Launch 파일은 실행할 노드, 실행 파일, 이름, 파라미터, 토픽 이름 변경 등의 구성을 한곳에 모아 관리한다.

수업에서는 `.launch.py` 형식의 Python 파일을 사용한 것으로 기록되어 있다. Python Launch 파일은 일반적으로 `generate_launch_description()`에서 실행 구성을 반환한다.

| 구성 요소 | 의미 |
| --- | --- |
| `LaunchDescription` | 전체 실행 구성 |
| `launch_ros.actions.Node` | 실행할 ROS 노드의 설정 |
| `package` | 실행 파일이 설치된 패키지 |
| `executable` | 패키지에 등록된 실행 이름 |
| `name` | 실행 중 사용할 노드 이름 |
| `parameters` | 노드에 전달할 파라미터 |
| `remappings` | 토픽·서비스 등의 이름 변경 |
| `output` | 프로세스 출력 처리 방식 |

### 4.2 실행 명령

패키지에 설치된 Launch 파일의 일반적인 실행 형식은 다음과 같다.

```text
ros2 launch <패키지 이름> <Launch 파일 이름>
```

수업에서 기억한 `ros2 launch 1_pubsub`는 이 명령의 패키지 부분이다. 정확한 명령을 재현하려면 뒤에 실제 Launch 파일 이름이 필요하다. 이 문서에서는 기억나지 않는 이름을 임의로 정해 실제 파일인 것처럼 사용하지 않는다.

### 4.3 실행과 통신 준비는 별개

세 노드를 한 명령으로 시작해도 발행과 구독 연결이 준비되는 시점이 완전히 같다는 뜻은 아니다. 프로세스 시작 순서만으로 첫 메시지의 전달까지 보장할 수 없다.

또한 일반적인 Launch는 노드별 터미널 창을 자동으로 하나씩 만드는 방식과 다르다. 한 터미널에 여러 노드 로그가 표시될 수 있으며, 별도 창이 필요한 경우에는 추가 구성이 필요하다.

### 4.4 키보드 입력 노드의 주의점

`publisher.py`가 `input()`으로 대화형 입력을 받았다면 개별 실행과 Launch 실행에서 표준입력 전달 방식이 달라질 수 있다. `output='screen'`이나 터미널 출력 설정만으로 대화형 입력이 보장되지는 않는다.

수업에서 세 노드가 함께 실행되었다는 설명은 기록하되, 원본 Launch 파일이 없으므로 입력 전달 방식과 구체적인 실행 옵션은 확정하지 않는다.

## 5. 이론 — Service의 요청과 응답

### 5.1 Service란?

Service는 클라이언트가 요청을 보내면 서버가 처리한 뒤 응답하는 통신 방식이다. 강의 노트의 메뉴판 비유처럼, 어떤 정보를 입력해야 하고 어떤 결과를 받을 수 있는지가 인터페이스에 명시되어 있다.

| 구성 요소 | 역할 |
| --- | --- |
| Client | 요청 데이터를 만들고 서버에 전송 |
| Server | 요청을 수신하고 계산·처리 |
| Request | 작업 수행에 필요한 입력 |
| Response | 처리 결과 |

한 번의 계산이나 설정 조회처럼 짧게 끝나는 작업에 적합하다. Service는 요청·응답 구조를 제공하지만 Action과 같은 진행 피드백·목표 취소 프로토콜을 기본으로 제공하지 않는다.

### 5.2 `.srv` 파일

서비스 파일은 요청과 응답을 `---`로 구분한다.

```text
요청 필드
---
응답 필드
```

요청과 응답에 들어가는 필드는 기본 타입뿐 아니라 다른 사용자 정의 메시지일 수도 있다. 이번 실습의 `AddTwoInts`는 `Num`, `MoveRobot`은 `RobotPose`를 사용한다.

### 5.3 비동기 호출과 Future

클라이언트는 `call_async()`를 호출하여 요청을 보내고 Future를 받는다. Future는 나중에 응답이 준비될 때 결과를 담는 객체이다.

제공 코드는 그 직후 `rclpy.spin_until_future_complete()`로 응답을 기다린다. 따라서 API 호출은 비동기이지만, 해당 함수 흐름은 결과가 준비될 때까지 대기하는 구조이다. `future.result()`는 완료된 응답을 가져온다.

### 5.4 서버 탐색

두 클라이언트는 `wait_for_service(timeout_sec=1.0)`을 반복한다. 서버가 없으면 `Waiting for service...`를 출력하며 기다린다.

1초는 전체 요청의 제한 시간이 아니다. 서비스 탐색을 한 번 기다리는 시간이고, 현재 코드는 이를 계속 반복하므로 서버가 영구적으로 없으면 대기도 계속될 수 있다.

## 6. 이론 — Action과 Topic·Service 비교

Action은 오래 걸리는 작업을 위한 통신 구조로 Goal, Feedback, Result를 사용한다. 강의 노트에서는 개념을 학습했지만 직접 Action 코드를 작성한 것은 아니라고 기록되어 있다.

| 요소 | 의미 | 이동 작업 예시 |
| --- | --- | --- |
| Goal | 수행할 목표 | 목표 위치로 이동 |
| Feedback | 진행 중 상태 | 남은 거리·현재 진행률 |
| Result | 작업 종료 결과 | 도착·실패 등의 결과 |

Action은 취소 요청도 지원한다. 다만 취소 요청을 보냈다고 서버가 항상 즉시 정지하거나 반드시 수락하는 것은 아니다. 서버 구현과 작업 상태에 따라 처리된다.

| 구분 | Topic | Service | Action |
| --- | --- | --- | --- |
| 기본 형태 | 발행·구독 | 요청·응답 | 목표·피드백·결과 |
| 일반적인 용도 | 지속적인 데이터 흐름 | 짧은 작업·조회 | 오래 걸리는 작업 |
| 중간 진행 피드백 | 별도 토픽으로 설계 가능 | 기본 구조에 없음 | 지원 |
| 목표 취소 | 별도 설계 필요 | Action식 취소 없음 | 취소 요청 지원 |
| 이번 실습 | 문자열·정수 처리 | 덧셈·위치 계산 | 이론 학습 |

## 7. 이론 — Custom Interface와 코드 생성

### 7.1 사용자 정의 인터페이스가 필요한 이유

표준 메시지로 표현하기 어렵거나 필드의 의미를 명확하게 묶고 싶을 때 사용자 정의 메시지를 사용할 수 있다. 현재 위치와 방향을 `RobotPose` 하나로 표현하면 서로 관련된 값의 구조가 분명해진다.

`.msg`와 `.srv`는 Python 클래스 소스 자체가 아니라 인터페이스 정의이다. 빌드 과정에서 이를 바탕으로 언어별 사용 코드가 생성되어야 Python의 `import`로 접근할 수 있다.

### 7.2 두 패키지의 역할

| 패키지 | 빌드 형식 | 역할 |
| --- | --- | --- |
| `custom_interfaces` | `ament_cmake` | 메시지·서비스 정의 및 코드 생성 |
| `2_srvmsg` | `ament_python` | 생성된 인터페이스로 노드 실행 |

`2_srvmsg`의 `package.xml`에는 `custom_interfaces` 의존성이 선언되어 있다. 인터페이스가 먼저 준비되어야 서비스 노드가 해당 타입을 가져올 수 있다.

### 7.3 메시지 필드 접근

`request.a`는 정수 그 자체가 아니라 `Num` 메시지 객체이다. 실제 정수는 `request.a.my_num`에 있다. 응답도 동일하게 `response.sum.my_num`으로 접근한다.

중첩 구조를 이해하지 못하고 `request.a + request.b`를 계산하려 하면 메시지 객체와 숫자의 역할을 혼동하게 된다.

## 8. 실습 구성과 패키지 구조 이해

### 8.1 `1_pubsub` 내부의 다섯 Python 파일

| 논리적 위치 | 내용 |
| --- | --- |
| 패키지 루트 | `package.xml`, `setup.py`, `setup.cfg`, `resource/` |
| 내부 Python 모듈 폴더 `1_pubsub/` | `__init__.py`, `talker.py`, `listener.py`, `publisher.py`, `processor.py`, `subscriber.py` |
| 패키지의 `launch/` | 실제 이름의 `.launch.py` 파일 |

같은 `1_pubsub`이라는 이름이 패키지 폴더와 내부 Python 모듈 폴더에서 반복될 수 있다. 패키지 메타데이터와 Python 소스의 위치를 구분해야 한다.

이 표는 요청한 파일 배치와 ROS 패키지 구성을 설명하는 것이다. 현재 문서가 있는 폴더에 이 파일들을 생성하거나 옮겼다는 뜻은 아니다.

### 8.2 서비스와 인터페이스의 분리

서비스 구현 Python 파일 4개는 `2_srvmsg`의 실행 코드이고, `.msg` 2개와 `.srv` 2개는 `custom_interfaces`의 정의 파일이다. 인터페이스 패키지의 `CMakeLists.txt`는 `msg/`와 `srv/`의 상대 경로를 참조한다.

실습 파일을 모으는 날짜 폴더와 ROS의 빌드 작업공간은 같은 개념이 아니다. 제출 저장소에 날짜별 소스를 보관하더라도 빌드할 때는 실제 패키지를 워크스페이스의 `src/` 아래에서 탐색할 수 있어야 한다.

## 9. 실습 — Talker와 Listener 기본 통신

### 9.1 Talker

제공된 Talker는 노드 이름 `talker`를 사용하며, `/demo_topic`에 `std_msgs/msg/String`을 발행한다. 타이머는 1초 간격으로 설정되어 있다.

타이머 콜백은 시작 시각과 현재 시각의 차이를 정수로 바꾸어 `Hello ROS2: <경과 초>`를 만든다. 이 숫자는 별도로 증가시키는 발행 횟수가 아니라 경과 시간이다.

### 9.2 Listener

Listener는 같은 `/demo_topic`과 String 타입으로 subscription을 만든다. 메시지가 도착하면 콜백이 호출되고 `msg.data`를 로그에 출력한다.

두 코드에서 QoS 인수 `10`은 메시지를 10번 보내라는 뜻이 아니라 이력 깊이 설정이다. `rclpy.spin()`은 타이머와 수신 콜백 등을 실행기가 처리하도록 한다.

### 9.3 기본 실습과 확장 실습의 관계

기본 실습은 한 방향 문자열 전달이다. 확장 실습은 입력 노드와 출력 노드 사이에 계산 노드를 배치한다. 두 경우 모두 노드를 토픽으로 연결하지만, 확장 구조에서는 processor가 구독과 발행을 동시에 담당한다.

## 10. 실습 — 두 정수의 발행·계산·출력

### 10.1 수업에서 설명한 동작

| 순서 | 파일 | 동작 |
| --- | --- | --- |
| 1 | `publisher.py` | 두 정수를 입력받아 하나의 입력 데이터로 전달 |
| 2 | `processor.py` | 입력 데이터를 수신하고 두 정수의 합 계산 |
| 3 | `processor.py` | 계산 결과를 출력용 토픽에 발행 |
| 4 | `subscriber.py` | 결과를 구독하고 화면에 출력 |

입력과 계산 결과를 서로 다른 메시지 흐름으로 구분하면 subscriber는 원본 숫자를 다시 계산하지 않고 결과를 받는 역할에 집중할 수 있다.

### 10.2 배열을 사용했을 때의 해석

두 값이 배열로 전달되었다면 processor는 원소 두 개를 꺼내 더하는 구조로 이해할 수 있다.

```text
입력 데이터의 개념 예시: [12, 8]
계산: 12 + 8
결과 데이터: 20
```

이는 동작 설명용 예시이며 실제 입력 기록이 아니다. 결과가 단일 정수 메시지였는지, 길이 1인 배열이었는지는 원본을 확인해야 한다.

배열 방식에서는 길이가 2인지, 두 값이 정수인지, 합이 메시지 타입의 범위에 들어가는지 검사하는 것이 중요하다. 이런 검사가 수업 원본에 구현되어 있었다고 단정하지 않는다.

### 10.3 Topic 덧셈과 Service 덧셈의 차이

Topic 덧셈은 입력 데이터가 processor를 거쳐 subscriber로 흘러가는 구조이다. Service 덧셈은 요청한 client에게 server가 응답을 돌려주는 구조이다.

계산 자체는 같아도 결과를 누구에게 어떻게 전달하는지가 다르다. Topic으로 다수의 소비자에게 결과를 공유할 수 있고, Service에서는 개별 요청에 대한 응답 관계가 분명하다.

## 11. 실습 — Launch로 세 노드 함께 실행

### 11.1 수행 내용

추가 수업 설명에 따르면 `.launch.py` 파일을 작성하여 publisher, processor, subscriber 세 노드를 한 명령으로 시작하는 단계까지 수행했다. 기본 talker·listener를 포함한 다섯 파일이 같은 모듈에 있다는 사실과, Launch가 숫자 처리 노드 세 개를 시작한다는 사실은 구분한다.

### 11.2 실행 구성이 성립하는 조건

| 항목 | 확인할 내용 |
| --- | --- |
| 실행 진입점 | publisher·processor·subscriber가 각각 실행 이름으로 등록되었는지 |
| Launch 설치 | Launch 파일이 패키지 설치 결과의 공유 디렉터리에 포함되는지 |
| Launch 참조 | `package`, `executable`이 실제 설치 이름과 일치하는지 |
| 데이터 연결 | 입력·결과 토픽 이름과 메시지 타입이 호환되는지 |
| 환경 | 같은 ROS 환경과 도메인을 사용하는지 |

Python 패키지에서는 `setup.py`의 `data_files`에 Launch 파일을 설치하는 구성이 필요하다.

### 11.3 Launch 파일 이름을 모를 때

실제 패키지에서 `.launch.py` 파일과 설치 결과를 확인해야 한다. 예를 들어 현재 소스 폴더에서 다음 명령은 Launch 파일을 찾는 용도이다.

```bash
find . -type f -name '*.launch.py'
```

설치된 패키지의 공유 위치는 다음 형식으로 확인할 수 있다.

```text
ros2 pkg prefix --share <실제 패키지 이름>
```

찾은 실제 파일명을 `ros2 launch`의 두 번째 인수에 사용한다. 

## 12. 실습 — 사용자 정의 메시지와 서비스

### 12.1 `Num.msg`

```text
int64 my_num
```

64비트 부호 있는 정수 한 개를 담는 메시지이다. Python에서는 `msg.my_num`으로 접근한다. `int64`의 표현 범위는 -2^63부터 2^63-1까지이다.

### 12.2 `RobotPose.msg`

```text
float64 x
float64 y
float64 theta
```

2차원 위치와 방향을 나타내는 사용자 정의 메시지이다. `x`, `y`는 위치이고 `theta`는 평면에서의 방향각으로 사용한다.

메시지 정의 자체는 단위나 좌표계를 강제하지 않는다. 제공 서버가 `math.cos()`와 `math.sin()`을 사용하므로 `theta`는 라디안으로 해석해야 한다. `distance`와 `x`, `y`도 일관된 길이 단위를 사용해야 한다.

### 12.3 `AddTwoInts.srv`

```text
custom_interfaces/Num a
custom_interfaces/Num b
---
custom_interfaces/Num sum
```

요청은 Num 두 개, 응답은 Num 한 개이다. 사용자 정의 메시지를 서비스 필드로 다시 사용하므로 메시지 간 조합을 학습할 수 있다.

| Python 필드 | 데이터 |
| --- | --- |
| `request.a.my_num` | 첫 번째 정수 |
| `request.b.my_num` | 두 번째 정수 |
| `response.sum.my_num` | 계산된 합 |

### 12.4 `MoveRobot.srv`

```text
RobotPose current_pose
float64 distance
---
RobotPose result_pose
bool success
```

같은 인터페이스 패키지의 `RobotPose`를 요청과 응답에서 사용한다. 현재 자세와 이동 거리를 입력하고 이동 후 자세와 성공 여부를 받는다.

여기서 `success`는 응답 필드이다. 

## 13. 실습 — 두 정수 덧셈 Service

### 13.1 서버의 처리 과정

`add_ints_server.py`는 `AddTwoIntsServer` 클래스를 만들고 노드 이름을 `srv_server`로 지정한다. 서비스 타입은 `AddTwoInts`, 이름은 `/add_two_ints`이다.

요청 콜백의 핵심 계산은 다음과 같다.

```python
response.sum.my_num = request.a.my_num + request.b.my_num
```

콜백은 입력과 결과를 로그로 출력한 뒤 response를 반환한다. 서비스 이름과 메시지 필드가 클라이언트와 동일해야 통신이 성립한다.

### 13.2 클라이언트의 처리 과정

`add_ints_client.py`는 `/add_two_ints` 서비스를 찾고 `AddTwoInts.Request()`를 생성한다. 명령행의 두 인수를 `int()`로 변환하여 각 Num의 `my_num` 필드에 저장한다.

1. `sys.argv[1]`, `sys.argv[2]`로 입력을 읽는다.
2. 두 값을 정수로 변환한다.
3. `call_async()`로 요청을 보낸다.
4. Future가 완료될 때까지 spin한다.
5. 응답의 `sum.my_num`을 `Sum:` 형식으로 출력한다.
6. 노드를 정리하고 ROS를 종료한다.


## 14. 실습 — 로봇 이동 후 위치 계산 Service

### 14.1 서버와 요청

`move_robot_server.py`는 `MoveRobot` 타입의 `/move_robots` 서비스를 만든다. 클라이언트는 현재 `x`, `y`, `theta`와 이동 거리 `distance`를 전달한다.

서버는 다음과 같이 현재 방향으로의 변위를 계산한다.

```text
new_x = x + distance × cos(theta)
new_y = y + distance × sin(theta)
new_theta = theta
```

### 14.2 계산 원리

이동 거리 벡터를 X축과 Y축으로 분해한 식이다. 방향각이 0이면 +X 방향, π/2이면 +Y 방향으로 이동한다. 방향각을 변경하는 회전 명령은 포함되어 있지 않다.

| 입력 예시 | 계산 결과 |
| --- | --- |
| `(x, y, theta) = (1, 2, 0)`, 거리 3 | `(4, 2, 0)` |
| `(0, 0, π/2)`, 거리 2 | 대략 `(0, 2, π/2)` |
| `(1, 2, 0)`, 거리 -1 | `(0, 2, 0)` |

삼각함수와 부동소수점 연산 때문에 이론적으로 0인 값이 매우 작은 수로 표현될 수 있다. 결과를 비교할 때는 적절한 허용 오차를 사용한다.

### 14.3 응답 객체를 변경하는 방식

서버의 `result = response.result_pose`는 응답 안의 메시지 객체를 참조한다. 이후 `result.x`, `result.y`, `result.theta`를 수정하면 응답의 해당 필드에도 반영된다.

서버는 현재 모든 요청에서 `response.success = True`를 설정한다. 충돌 검사나 센서 피드백을 거쳐 주행 성공을 판정하는 코드는 아니다.

### 14.4 실제 로봇 주행과의 구분

파일명에 MoveRobot이 있지만 제공된 서버는 좌표를 계산할 뿐이다. 모터 명령 발행, 엔코더 읽기, 실제 위치 추정, 장애물 검사는 수행하지 않는다. 따라서 응답이 True라는 사실을 실제 로봇이 목표 위치에 도착했다는 증거로 해석하면 안 된다.

### 14.5 클라이언트 출력

클라이언트는 명령행 인수 네 개를 `float()`로 변환하고 요청한다. 응답 후 로그에는 `pose.x`, `pose.y`, `response.success`를 출력한다. `result_pose.theta`도 응답에 들어 있지만 현재 로그에는 출력하지 않는다.

음수 거리나 비정상적인 입력 값의 허용 여부를 별도 검증하지 않는다는 점도 확인할 수 있다.

## 15. 빌드 설정과 실행 방법

### 15.1 필수 환경과 의존성

수업 환경인 Ubuntu 24.04 및 ROS 2 Jazzy를 기준으로 설명한다. 아래는 ROS가 설치된 bash 환경에서 사용하는 예시이다.

| 영역 | 의존성 |
| --- | --- |
| Python 노드 | Python 3, `rclpy` |
| 기본 문자열 통신 | `std_msgs` |
| 서비스 노드 | 빌드된 `custom_interfaces` |
| Python 패키지 | `setuptools`, `ament_python`, `colcon` |
| 인터페이스 생성 | `ament_cmake`, `rosidl_default_generators` |
| 인터페이스 실행 지원 | `rosidl_default_runtime` |
| Launch | `launch`, `launch_ros`, `ros2launch` |
| 테스트 | `pytest`, ament의 스타일·문서 검사 도구 |

서비스 패키지의 XML에는 `geometry_msgs`, `sensor_msgs`, `nav_msgs`도 선언되어 있다. 다만 제공된 서비스 코드가 직접 가져오는 인터페이스는 `custom_interfaces`이다.

### 15.2 `CMakeLists.txt`에서 확인한 내용

인터페이스 패키지는 `project(custom_interfaces)`를 선언하고 다음 네 파일을 생성 대상으로 등록한다.

```cmake
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Num.msg"
  "srv/AddTwoInts.srv"
  "msg/RobotPose.msg"
  "srv/MoveRobot.srv"
)
```

이 네 파일이 실제 상대 경로에 있어야 한다. 빌드 결과가 준비되고 환경을 적용한 뒤 다음을 통해 정의를 확인할 수 있다.

```bash
ros2 interface show custom_interfaces/msg/Num
ros2 interface show custom_interfaces/msg/RobotPose
ros2 interface show custom_interfaces/srv/AddTwoInts
ros2 interface show custom_interfaces/srv/MoveRobot
```

### 15.3 `setup.py`의 실행 진입점

제공된 서비스 패키지는 다음 실행 이름을 등록한다.

| 실행 이름 | 연결되는 함수 |
| --- | --- |
| `add_ints_client` | `2_srvmsg.add_ints_client:main` |
| `add_ints_server` | `2_srvmsg.add_ints_server:main` |
| `move_robot_client` | `2_srvmsg.move_robot_client:main` |
| `move_robot_server` | `2_srvmsg.move_robot_server:main` |

`setup.cfg`는 `$base/lib/2_srvmsg`를 설치 위치로 지정한다. 이 경로와 패키지 이름·실행 등록이 일치해야 한다.


### 15.5 인터페이스 빌드

기존 워크스페이스에 `custom_interfaces`의 표준 패키지 구조가 준비되어 있다고 가정한다. `~/ros2_ws`는 작업공간 경로 예시이다.

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_ws
colcon build --packages-select custom_interfaces
source install/setup.bash
```

빌드한 환경을 사용해야 Python에서 다음 import가 가능하다.

```bash
python3 -c 'from custom_interfaces.srv import AddTwoInts, MoveRobot; print("interface import OK")'
```

인터페이스 파일을 Python 소스 옆에 복사하는 것만으로 import가 가능해지는 것은 아니다.

### 15.6 덧셈 서비스 스크립트 실행

각 터미널에서 기본 ROS 환경과 인터페이스 작업공간을 적용한다. 아래 명령은 각 Python 파일이 있는 폴더에서 실행한다.

**터미널 A — 서버**

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
export ROS_DOMAIN_ID=2
python3 add_ints_server.py
```

**터미널 B — 클라이언트**

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
export ROS_DOMAIN_ID=2
python3 add_ints_client.py 7 5
```


### 15.7 위치 계산 서비스 스크립트 실행

덧셈 시험을 종료한 후 각 파일이 있는 폴더에서 다음을 실행한다. 새 터미널에는 앞 절과 동일한 ROS 환경과 Domain ID를 적용한다.

```bash
python3 move_robot_server.py
```

다른 터미널에서 요청한다.

```bash
python3 move_robot_client.py 1 2 0 3
```

입력 순서는 `x`, `y`, `theta`, `distance`이며, 코드상 예상 출력의 값은 `4.0 2.0 True`이다. 실행 중인 서버는 `Ctrl+C`로 종료한다.

패키지 빌드와 실행 등록이 검증된 환경에서는 `ros2 run <실제 패키지 이름> <실행 이름> ...` 형식도 사용할 수 있다. 스크립트 직접 실행 성공과 Python 패키지 설치 성공은 별도로 확인해야 한다.

### 15.8 서비스 상태와 노드 이름

```bash
ros2 service list
ros2 service type /add_two_ints
ros2 service type /move_robots
ros2 node list
```

덧셈 서버와 위치 계산 서버는 모두 `srv_server`, 두 클라이언트는 모두 `srv_client`라는 노드 이름을 사용한다. 동시에 실행하면 서비스 이름은 달라도 노드 이름이 중복될 수 있다.

두 서비스를 함께 시험하려면 실행 시 서로 다른 노드 이름을 부여하는 방법을 사용할 수 있다. 예를 들어 서버 스크립트에 `--ros-args -r __node:=add_ints_server_node`와 같이 ROS 인수를 전달할 수 있다. 해당 서비스 클라이언트는 위치 인수를 사용하므로 추가 인수의 배치도 확인해야 한다.

## 16. 코드 품질 검사와 확인 범위

### 16.1 제공된 테스트 파일

| 검사 | 호출 도구 | 현재 코드의 의미 |
| --- | --- | --- |
| 저작권 | `ament_copyright` | `pytest.mark.skip`으로 생략 |
| Python 스타일 | `ament_flake8` | 반환 코드와 오류 목록 검사 |
| Docstring | `ament_pep257` | 모듈·클래스·함수 문서화 규칙 검사 |

테스트 파일이 있다는 사실만으로 통과를 의미하지 않는다. 제공된 서비스 코드에는 docstring이 없는 부분과 불필요한 공백 등이 있어 실제 결과를 확인해야 한다.

### 16.2 실행 형식

빌드 가능한 실제 패키지 이름을 사용하여 워크스페이스에서 실행한다.

```text
colcon test --packages-select <실제 패키지 이름>
colcon test-result --verbose
```

이 검사는 서비스 계산의 정답이나 여러 노드의 실제 통신까지 모두 보장하는 기능 테스트가 아니다. 송수신과 계산 결과는 별도 시험이 필요하다.

## 17. 결과 해석과 문제 해결

### 17.1 자료에서 확인한 결과와 확인 한계

| 항목 | 확인 가능한 내용 | 추가 확인이 필요한 내용 |
| --- | --- | --- |
| 기본 Topic | String 발행·구독 코드와 토픽 | 실제 송수신 로그 |
| 정수 처리 Topic | 설명한 3단계 데이터 처리 흐름 | 원본 메시지 타입·토픽·입력 처리 코드 |
| Launch | 세 노드를 함께 실행했다는 수업 설명 | 실제 파일명·Launch 설치·입력 연결 |
| 덧셈 Service | 중첩 Num 필드를 더하는 코드 | 실제 요청·응답 기록과 예외 입력 결과 |
| 위치 계산 Service | 삼각함수를 통한 위치 계산 | 실제 실행 기록; 하드웨어 주행은 구현 범위 밖 |
| 코드 품질 | 테스트 종류와 skip 여부 | 실제 검사 통과 여부 |


## 18. 학습 정리

이번 실습의 핵심은 계산식 자체보다 **노드 사이에서 입력과 결과를 어떻게 표현하고 전달하는가**이다.

Topic 실습에서는 입력·계산·출력을 서로 다른 노드로 나누었다. Launch는 이 노드들의 실행 구성을 모아서 관리한다. Service 실습에서는 요청과 응답의 형식을 명시하고 클라이언트·서버 사이의 한 번의 계산 흐름을 구현한다. Custom Interface는 이 통신에 필요한 데이터의 구조를 정의하며 빌드 과정을 통해 실제 프로그래밍 언어에서 사용하는 타입으로 연결된다.

핵심 개념을 다음과 같이 정리할 수 있다.

- `processor.py`는 입력 구독과 결과 발행을 함께 수행하는 노드이다.
- Launch 실행 명령에는 패키지 이름과 실제 Launch 파일 이름이 필요하다.
- `.srv`에서 `---` 위는 Request, 아래는 Response이다.
- `Num` 내부의 실제 정수는 `my_num` 필드에 저장된다.
- `call_async()`의 Future를 기다리는 단계와 요청 전송 단계는 구분된다.
- MoveRobot의 theta는 삼각함수 계산에서 라디안으로 해석된다.
- 위치 계산 성공과 실제 로봇 주행 성공은 같은 의미가 아니다.
- Action은 이번 제공 코드의 구현 대상이 아니라 이론 학습 범위이다.

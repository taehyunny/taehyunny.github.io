---
title: "객체화와 캡슐화를 책임 단위로 나누는 고민"
date: 2026-03-03 00:00:00 +0900
categories: [project-log, architecture]
tags: [cpp, oop, encapsulation, responsibility, mvc]
---

## 상황

키오스크 프로젝트를 설계하면서 “객체화를 한다”는 말이 생각보다 막연하다는 것을 느꼈다.

단순히 클래스를 많이 만드는 것이 객체지향은 아니다. 중요한 것은 어떤 데이터를 숨기고, 어떤 행위만 외부에 열어둘지 결정하는 일이다. 그래서 이번에는 캡슐화, 독립성, 객체 분화를 어떻게 바라볼지 정리해봤다.

## 캡슐화에서 먼저 의심해야 할 것

캡슐화는 단순히 멤버 변수를 `private`으로 숨기는 문법이 아니다.

내가 생각한 핵심 질문은 다음과 같았다.

- UI가 결제 상태를 직접 수정할 수 있는가?
- 버튼 하나가 `OrderManager` 내부 변수를 직접 건드리고 있지는 않은가?
- 사용자가 떠난 뒤 초기화 로직이 외부에 노출되어 오작동할 여지는 없는가?

즉 캡슐화는 “숨긴다”보다 “잘못된 접근을 막는다”에 가깝다.

## private과 public의 역할

예를 들어 결제 처리, 주문 완료, 초기화 같은 흐름은 외부에서 마음대로 호출되면 위험할 수 있다.

```cpp
private slots:
    void processPayment();
    void finishOrder(bool printReceipt);
    void resetToInitialState();
```

반면 외부에서 사용할 수 있어야 하는 기능은 public 인터페이스로 열어둘 수 있다.

```cpp
private:
    QSoundEffect* voicePlayer;

public slots:
    void playVoice(VoiceType type);
```

비유하자면 내부에서 어떤 파일을 어떤 경로로 불러오는지는 숨기고, 외부에는 “이 상황에 맞는 안내 음성을 재생해줘”라는 버튼만 제공하는 구조다.

## 객체화는 데이터와 행위를 묶는 일

객체는 데이터와 행위를 하나로 묶은 주머니라고 생각했다.

- 상태: 이름, 금액, 색상, 선택 옵션
- 행위: 계산하기, 출력하기, 검증하기, 초기화하기

절차지향이 “이 데이터를 저 함수에 넣어”라고 명령하는 방식이라면, 객체지향은 “객체야, 네가 가진 데이터를 써서 이 일을 해줘”라고 요청하는 방식에 가깝다.

## 객체를 나눌 때의 기준

키오스크 프로젝트에서는 다음과 같은 객체 단위를 생각했다.

| 객체 | 역할 |
| --- | --- |
| `Product` | 상품 이름, 가격, 옵션 정보를 담는 순수 데이터 객체 |
| `Cart` | 장바구니 상품 목록과 총액 관리 |
| `OrderDraft` | 팝업이 닫히기 전 사용자의 미완성 선택 상태 저장 |
| `PaymentSystem` | 결제 수단과 승인 로직 처리 |
| `ButtonAction` | 버튼 클릭 시 수행할 행위를 주입받아 실행 |

이렇게 나누면 UI가 DB나 결제 로직을 직접 알 필요가 줄어든다.

## 데이터와 로직의 분리

장바구니를 관리하는 객체는 화면을 직접 바꾸기보다, 데이터가 변경되었을 때 외부에서 주입한 함수를 호출하도록 만들 수 있다.

```cpp
class DSOrderManager {
public:
    DSOrderManager() = default;

    void setOnUpdate(std::function<void(int total)> action);
    void addItem(const Product& product);
    void clear();

private:
    std::vector<Product> items;
    std::function<void(int total)> onUpdate;
};
```

이 구조에서는 `DSOrderManager`가 장바구니 데이터와 계산 책임을 갖고, 화면 갱신 방식은 외부에서 결정한다.

## 배운 점

객체화는 클래스를 많이 만드는 일이 아니라 책임을 분리하는 일이다.

어떤 객체가 너무 많은 일을 하고 있다면, 그것은 객체의 탈을 쓴 절차지향 코드일 수 있다. 그래서 객체를 나눌 때는 “이 객체가 무엇을 알고 있어야 하는가”와 “무엇을 몰라도 되는가”를 계속 물어봐야 한다.

## 다음 과제

- UI, 데이터, 결제, 음성 안내의 책임 경계를 더 명확히 나누기
- 객체 간 의존성을 생성자 주입으로 관리할 수 있을지 확인하기
- DTO와 도메인 객체의 차이를 더 구체적으로 정리하기
- 실제 코드에서 한 객체가 너무 많은 책임을 갖는 지점 찾기


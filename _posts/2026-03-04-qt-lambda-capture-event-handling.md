---
title: "Qt 이벤트 처리에서 람다와 캡처를 사용할 때의 기준"
date: 2026-03-04 00:00:00 +0900
categories: [project-log, architecture]
tags: [cpp, qt, lambda, capture, event-handling]
---

## 상황

Qt에서 버튼 클릭 이벤트를 처리하다 보면 모든 동작을 별도 슬롯 함수로 빼야 하는지 고민하게 된다.

짧고 한 번만 쓰이는 로직이라면 람다를 쓰는 편이 더 직관적일 수 있다. 하지만 람다는 이름이 없는 함수이기 때문에, 너무 쉽게 쓰면 예외 처리와 책임 경계가 흐려질 수 있다.

## 람다가 잘 맞는 경우

버튼과 매니저 사이에서 단순한 연결만 수행하는 경우에는 람다가 읽기 쉽다.

```cpp
connect(btnAme, &QPushButton::clicked, [this]() {
    manager->selectProduct(Product("아메리카노", 3000));
});

connect(btnLatte, &QPushButton::clicked, [this]() {
    manager->selectProduct(Product("카페라떼", 3500));
});
```

이 경우 람다는 버튼 클릭 이벤트를 상품 선택 명령으로 바꿔주는 통역사 역할만 한다.

## 일회성 UI 조작

도움말 팝업을 닫는 것처럼 특정 화면 안에서만 일어나는 짧은 동작도 람다와 잘 맞는다.

```cpp
connect(btnHelpClose, &QPushButton::clicked, [this]() {
    helpWidget->hide();
});
```

로직이 짧고 재사용 가능성이 거의 없다면, 별도 함수 이름을 만드는 것보다 이벤트 연결부에서 바로 읽히는 편이 낫다.

## 지연 실행

주문 완료 후 5초 뒤 초기 화면으로 돌아가는 흐름도 람다로 표현할 수 있다.

```cpp
void KioskWidget::finishOrder() {
    stack->setCurrentWidget(gratitudePage);

    QTimer::singleShot(5000, [this]() {
        this->resetToInitialState();
    });
}
```

이렇게 쓰면 “5초 뒤 무엇을 할지”가 코드상에서 바로 보인다.

## 람다 사용 기준

내가 세운 기준은 다음과 같다.

- 다른 곳에서 재사용될 가능성이 거의 없는가?
- 코드가 3줄 이내로 짧은가?
- 이 이벤트의 목적을 더 직관적으로 설명하는가?
- 예외가 발생했을 때 그 자리에서 처리할 수 있는가?

이 기준을 벗어나면 람다보다 이름 있는 함수로 분리하는 편이 낫다.

## 캡처 범위 통제

람다에서 가장 조심해야 할 부분은 캡처다.

특히 `[&]`처럼 주변 변수를 모두 참조로 캡처하는 방식은 편하지만 위험하다. 람다가 실행되는 시점에는 캡처한 객체가 이미 사라졌을 수도 있고, 어떤 값을 사용하고 있는지 코드만 봐서는 흐려질 수 있다.

그래서 가능한 한 필요한 값만 명시적으로 캡처하는 편이 좋다.

```cpp
connect(button, &QPushButton::clicked, [this, productId]() {
    manager->selectProductById(productId);
});
```

## 배운 점

람다는 코드를 짧고 직관적으로 만들 수 있지만, 이름이 없다는 점 때문에 책임이 흐려지기 쉽다.

짧고 지역적인 UI 이벤트는 람다로 처리하고, 여러 곳에서 재사용되거나 예외 처리가 중요한 로직은 이름 있는 함수로 분리하는 기준이 필요하다.

## 다음 과제

- `[this]` 캡처 시 객체 생명주기 문제 확인하기
- 람다 내부 예외 처리 패턴 정리하기
- 재사용 가능한 슬롯 함수와 람다의 기준을 프로젝트 코드에 적용해보기


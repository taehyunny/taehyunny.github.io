---
title: "버튼 클릭 행위를 객체로 분리하는 설계 고민"
date: 2026-03-05 00:00:00 +0900
categories: [project-log, architecture]
tags: [cpp, qt, oop, strategy-pattern, debounce]
---

## 상황

옵션 선택 화면에서 버튼이 눌렸을 때 처리해야 할 일이 점점 늘어났다.

예를 들어 옵션 추가 버튼은 선택한 옵션과 금액을 주문 임시 데이터에 기록해야 하고, 초기화 버튼은 선택된 옵션과 추가 금액을 다시 비워야 한다. 처음에는 버튼마다 직접 로직을 넣을 수도 있지만, 버튼이 많아질수록 화면 코드가 점점 복잡해질 것 같았다.

그래서 버튼이 눌리는 행위를 별도의 객체로 분리해보는 방식을 고민했다.

## 역할 분리

### 추가 객체: `OptionAddAction`

추가 객체의 역할은 단순하다.

> 나는 옵션만 담는다.

버튼이 눌리면 자신이 가진 옵션 정보, 예를 들어 `"샷 추가"`와 `500원` 같은 데이터를 공통 장부 역할을 하는 `DSOrderDraft`에 기록한다.

이 객체는 화면이 어떻게 생겼는지, 라벨을 어떻게 바꾸는지 알 필요가 없다. 오직 데이터 갱신이라는 본질에만 집중한다.

### 삭제/초기화 객체: `OptionResetAction`

초기화 객체는 선택된 옵션을 전부 지우고 다시 시작하게 만든다.

설계도의 초기화 버튼에 해당하며, `DSOrderDraft`의 옵션 문자열을 비우고 추가 금액을 `0원`으로 되돌린다.

이 객체 역시 화면을 다시 그리는 책임은 갖지 않는다. 화면 갱신은 창 객체가 맡는다.

### 흐름/관리 객체: `DSOptionSelectPage`

화면 객체는 일꾼들을 배치하고 최종 결과를 메인 시스템에 전달하는 역할을 맡는다.

주요 역할은 다음과 같다.

- `Adder`, `Reseter` 객체를 화면의 알맞은 위치에 배치한다.
- 버튼 동작이 끝날 때마다 선택한 옵션과 총 결제 금액을 갱신한다.
- 주문 담기, 이전, 다음 같은 이동 버튼이 눌리면 완성된 `DSOrderDraft`를 메인 시스템 또는 DB로 넘긴다.

## 설계 방향

버튼 자체는 클릭 이벤트를 받고, 실제 행위는 `IButtonAction` 인터페이스를 구현한 객체가 수행하게 만들고 싶었다.

이렇게 하면 버튼은 “클릭되었다”는 이벤트 처리와 중복 클릭 방지 같은 공통 역할에 집중하고, 옵션 추가나 초기화 같은 업무 로직은 별도 객체로 분리할 수 있다.

```cpp
#ifndef DSBUTTON_H
#define DSBUTTON_H

#include <QPushButton>
#include <QTimer>
#include "dsorderdraft.h"

class IButtonAction {
public:
    virtual ~IButtonAction() = default;
    virtual void execute(DSOrderDraft& draft) = 0;
};

class DSButton : public QPushButton {
    Q_OBJECT

public:
    explicit DSButton(QWidget *parent = nullptr);
    ~DSButton();

    void setAction(IButtonAction* action, DSOrderDraft* draft);

private slots:
    void handleClicked();

private:
    IButtonAction* m_action;
    DSOrderDraft* m_draft;
    bool m_isProcessing;
};

#endif
```

여기서 `m_isProcessing`은 중복 클릭을 막기 위한 디바운스 플래그로 생각했다. 사용자가 버튼을 빠르게 여러 번 누르더라도 주문 데이터가 중복으로 들어가지 않게 막기 위한 장치다.

## 공통 기능 분리 고민

버튼 행위뿐 아니라 자주 쓰는 포맷팅 기능도 공통으로 분리할 수 있을지 고민했다.

예를 들어 금액을 `3300`에서 `"3,300원"`으로 바꾸거나, 휴대폰 번호를 일정한 형식으로 정리하는 기능은 여러 화면에서 반복될 가능성이 높다.

```cpp
namespace KioskCommon {
    inline QString formatCurrency(int amount) {
        return QLocale(QLocale::Korean).toString(amount) + "원";
    }

    inline QString formatPhone(QString raw) {
        raw.remove(QRegularExpression("[^0-9]"));

        if (raw.length() == 11) {
            return raw.mid(0, 3) + "-" + raw.mid(3, 4) + "-" + raw.mid(7);
        }

        return raw;
    }

    inline bool isPhoneValid(const QString& phone) {
        return phone.length() == 11;
    }
}
```

이런 공통 기능은 화면 로직 안에 흩어져 있는 것보다 별도 네임스페이스로 묶어두는 편이 재사용성과 가독성 면에서 좋다고 생각했다.

## 배운 점

이번 설계에서 가장 크게 고민한 부분은 “무엇을 객체로 나눌 것인가”였다.

처음에는 버튼마다 기능을 직접 넣는 방식이 단순해 보였지만, 버튼이 많아지고 역할이 늘어나면 화면 코드가 지나치게 많은 책임을 갖게 된다. 그래서 버튼 클릭이라는 공통 흐름과 실제 업무 행위를 분리하는 방향을 생각해봤다.

아직 이 설계가 완전히 정답이라고 생각하지는 않는다. 다만 버튼, 화면, 데이터 객체가 각각 어떤 책임을 가져야 하는지 고민해보는 과정 자체가 객체지향 설계를 이해하는 데 도움이 되었다.

## 다음 과제

- `IButtonAction` 객체의 소유권을 누가 관리할지 정리하기
- raw pointer 대신 스마트 포인터를 사용할 수 있을지 검토하기
- `DSOrderDraft` 변경 후 화면 갱신을 어떤 방식으로 통지할지 정리하기
- 공통 유틸 함수가 많아질 때 namespace와 class 중 어떤 방식이 나을지 비교하기


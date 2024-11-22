import QtQuick 2.0
import QtQuick.Controls 2.3

RangeSlider {
    id: rangeSlider
    from: 0
    to: 100
    first.value: 25
    second.value: 75

    onFirstValueChanged: {
        firstValueChanged(first.value)
    }

    onSecondValueChanged: {
        secondValueChanged(second.value)
    }

    signal firstValueChanged(real value)
    signal secondValueChanged(real value)
}
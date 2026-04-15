package com.dance4life.core.utils


object HrCalculator {

    fun calculate(acc: Double, gyro: Double): Int {
        var novoHR = 60 + ((acc + gyro) * 2).toInt()
        if (novoHR < 60) novoHR = 60
        if (novoHR > 140) novoHR = 140
        return novoHR
    }
}
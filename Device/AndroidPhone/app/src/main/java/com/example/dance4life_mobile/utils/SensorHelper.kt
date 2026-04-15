package com.example.dance4life_mobile.utils

import android.content.Context
import android.hardware.*
import com.example.dance4life_mobile.data.model.SensorData
import kotlin.math.sqrt

class SensorHelper(
    context: Context,
    private val onData: (SensorData) -> Unit
) : SensorEventListener {

    private val sensorManager =
        context.getSystemService(Context.SENSOR_SERVICE) as SensorManager

    private var lastAcc = 0.0
    private var lastGyro = 0.0

    private var sliderHR = 70

    private val accData = mutableListOf<Float>()
    private val gyroData = mutableListOf<Float>()
    private val hrData = mutableListOf<Int>()

    private var accX = 0f
    private var accY = 0f
    private var accZ = 0f

    private var gyroX = 0f
    private var gyroY = 0f
    private var gyroZ = 0f

    private var accUpdated = false
    private var gyroUpdated = false

    private val accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
    private val gyroscope = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE)

    private val heartRateSensor = sensorManager.getDefaultSensor(Sensor.TYPE_HEART_RATE)

    fun start() {
        accelerometer?.also {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL)
        }
        gyroscope?.also {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL)
        }
        heartRateSensor?.also {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL)
        }
    }

    fun stop() {
        sensorManager.unregisterListener(this)
    }

    fun updateSliderHR(value: Int) {
        sliderHR = value
    }

    override fun onSensorChanged(event: SensorEvent) {

        if (event.sensor.type == Sensor.TYPE_ACCELEROMETER) {

            accX = event.values[0]
            accY = event.values[1]
            accZ = event.values[2]

            lastAcc = sqrt((accX * accX + accY * accY + accZ * accZ).toDouble())
            accUpdated = true
        }

        if (event.sensor.type == Sensor.TYPE_GYROSCOPE) {

            gyroX = event.values[0]
            gyroY = event.values[1]
            gyroZ = event.values[2]

            lastGyro = sqrt((gyroX * gyroX + gyroY * gyroY + gyroZ * gyroZ).toDouble())
            gyroUpdated = true
        }

        //só quando ambos estiverem atualizados
        if (accUpdated && gyroUpdated) {

            val autoHR = atualizarHRComMovimento(lastAcc, lastGyro)
            val currentHR = combinarHR(autoHR, sliderHR)

            hrData.add(currentHR)

            val data = SensorData(
                accX, accY, accZ,
                gyroX, gyroY, gyroZ,
                currentHR,
                lastAcc,
                lastGyro
            )

            onData(data)

            accUpdated = false
            gyroUpdated = false

            if (event.sensor.type == Sensor.TYPE_HEART_RATE) {
                val realHR = event.values[0].toInt()

                val data = SensorData(
                    accX, accY, accZ,
                    gyroX, gyroY, gyroZ,
                    realHR,
                    lastAcc,
                    lastGyro
                )

                onData(data)
            }
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}

    private fun atualizarHRComMovimento(acc: Double, gyro: Double): Int {
        var novoHR = 60 + ((acc + gyro) * 2).toInt()
        if (novoHR < 60) novoHR = 60
        if (novoHR > 140) novoHR = 140
        return novoHR
    }

    private fun combinarHR(autoHR: Int, sliderHR: Int): Int {
        return (0.7 * autoHR + 0.3 * sliderHR).toInt()
    }
}
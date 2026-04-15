package com.dance4life.wear.domain.sensor

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.util.Log
import com.dance4life.core.data.model.SensorData
import com.dance4life.core.domain.controller.DanceController
import com.dance4life.core.utils.HrCalculator
import kotlin.math.sqrt

class SensorHelper(
    context: Context,
    private val onData: (SensorData) -> Unit
) : SensorEventListener {

    private val sensorManager =
        context.getSystemService(Context.SENSOR_SERVICE) as SensorManager

    private var accX = 0f
    private var accY = 0f
    private var accZ = 0f

    private var gyroX = 0f
    private var gyroY = 0f
    private var gyroZ = 0f

    private var lastAcc = 0.0
    private var lastGyro = 0.0

    private var accUpdated = false
    private var gyroUpdated = false
    private var hrUpdated = false

    private var currentHR = 0

    private var lastUpdateTime = 0L
    private val updateInterval = 500L

    private val accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
    private val gyroscope = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE)
    private val heartRateSensor = sensorManager.getDefaultSensor(Sensor.TYPE_HEART_RATE)

    fun start() {

        Log.d("WEAR", "ACC: $accelerometer")
        Log.d("WEAR", "GYRO: $gyroscope")
        Log.d("WEAR", "HR: $heartRateSensor")

        accelerometer?.also {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_GAME)
        }

        gyroscope?.also {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_GAME)
        }

        heartRateSensor?.also {
            sensorManager.registerListener(
                this,
                it,
                SensorManager.SENSOR_DELAY_NORMAL
            )
        }

        // 🔥 IMPORTANTE: enviar dados iniciais para UI não ficar vazia
        onData(buildData())
    }

    fun stop() {
        sensorManager.unregisterListener(this)
    }

    override fun onSensorChanged(event: SensorEvent) {

        when (event.sensor.type) {

            Sensor.TYPE_ACCELEROMETER -> {
                accX = event.values[0]
                accY = event.values[1]
                accZ = event.values[2]

                lastAcc = sqrt((accX * accX + accY * accY + accZ * accZ).toDouble())
                accUpdated = true
            }

            Sensor.TYPE_GYROSCOPE -> {
                gyroX = event.values[0]
                gyroY = event.values[1]
                gyroZ = event.values[2]

                lastGyro = sqrt((gyroX * gyroX + gyroY * gyroY + gyroZ * gyroZ).toDouble())
                gyroUpdated = true
            }

            Sensor.TYPE_HEART_RATE -> {
                val hrValue = event.values[0].toInt()

                Log.d("WEAR", "HR RAW: $hrValue")

                if (hrValue in 40..200) {
                    currentHR = hrValue
                    Log.d("WEAR", "HR VALID: $currentHR")

                    onData(buildData()) // envia imediatamente
                }
                hrUpdated = true
                return
            }
        }

        val now = System.currentTimeMillis()

        if (accUpdated && gyroUpdated && now - lastUpdateTime > updateInterval) {
            lastUpdateTime = now

            // fallback caso HR real não exista
            if (!hrUpdated) {
                currentHR = HrCalculator.calculate(lastAcc, lastGyro)
            }

            accUpdated = false
            gyroUpdated = false

            Log.d("WEAR", "DATA SENT → ACC: $lastAcc | GYRO: $lastGyro | HR: $currentHR")

            onData(buildData())
        }
    }

    private fun buildData(): SensorData {
        return SensorData(
            accX, accY, accZ,
            gyroX, gyroY, gyroZ,
            currentHR,
            lastAcc,
            lastGyro
        )
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}


}
package com.dance4life.core.domain.controller

import com.dance4life.core.data.model.LocationData
import com.dance4life.core.data.model.SensorData
import com.dance4life.core.data.repository.DataRepository
import com.dance4life.core.domain.device.DeviceProvider
import com.dance4life.core.domain.location.LocationProvider
import com.dance4life.core.domain.sensor.SensorProvider
import com.dance4life.core.utils.HrCalculator
import com.dance4life.core.utils.RitmoCalculator


class DanceController_2(
    private val sensorProvider: SensorProvider,
    private val locationProvider: LocationProvider,
    private val repository: DataRepository,
    private val ritmoCalculator: RitmoCalculator,
    private val deviceProvider: DeviceProvider
) {

    private var onLocationUpdate: ((LocationData) -> Unit)? = null

    private val accData = mutableListOf<Float>()
    private val gyroData = mutableListOf<Float>()
    private val hrData = mutableListOf<Int>()

    private var currentLat: Double = 0.0
    private var currentLon: Double = 0.0

    private var onSensorUpdate: ((SensorData) -> Unit)? = null
    private var onRitmoCalculated: ((Double) -> Unit)? = null

    fun setSensorListener(listener: (SensorData) -> Unit) {
        onSensorUpdate = listener
    }

    fun setRitmoListener(listener: (Double) -> Unit) {
        onRitmoCalculated = listener
    }

    fun start() {

        locationProvider.start { location ->
            currentLat = location.latitude
            currentLon = location.longitude

            onLocationUpdate?.invoke(location)
        }

        sensorProvider.setListener { data ->

            accData.add(data.accMagnitude.toFloat())
            gyroData.add(data.gyroMagnitude.toFloat())
            hrData.add(data.heartRate)

            onSensorUpdate?.invoke(data)


            if (accData.size > 50) {
                accData.removeAt(0)
                gyroData.removeAt(0)
                hrData.removeAt(0)
            }

            if (accData.size >= 1) {
                calcularRitmo()
            }
        }

        sensorProvider.start()
    }

    fun stop() {
        sensorProvider.stop()
    }

    fun calcularRitmo() {

        val result = ritmoCalculator.calcular(accData, gyroData, hrData)

        onRitmoCalculated?.invoke(result.ritmo)

        repository.enviarDados(
            deviceProvider.getUserId(),
            result.ritmo,
            result.avgAcc,
            result.avgGyro,
            result.avgHR,
            currentLat,
            currentLon
        )

        accData.clear()
        gyroData.clear()
        hrData.clear()
    }

    fun setLocationListener(listener: (LocationData) -> Unit) {
        onLocationUpdate = listener
    }
}
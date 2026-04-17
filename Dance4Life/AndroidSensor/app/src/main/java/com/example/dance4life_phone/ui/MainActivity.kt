package com.example.dance4life_phone.ui

import android.app.NotificationChannel
import android.app.NotificationManager
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.os.Build
import android.os.Bundle
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import com.example.dance4life_phone.data.rl.RlMetricsManager
import com.dance4life.core.data.model.MovementObservation
import com.dance4life.core.data.model.MovementRecommendation
import com.dance4life.core.data.model.SensorData
import com.dance4life.core.data.repository.DataRepository
import com.dance4life.core.domain.controller.DanceController
import com.example.dance4life_phone.R


import com.dance4life.core.domain.sensor.SensorProvider
import com.dance4life.core.domain.location.LocationProvider
import com.dance4life.core.utils.RitmoCalculator
import com.dance4life.core.domain.device.DeviceProvider
import com.example.dance4life_phone.domain.device.PhoneDeviceProvider
import com.example.dance4life_phone.domain.location.PhoneLocationProvider
import com.example.dance4life_phone.domain.sensor.PhoneSensorProvider
import com.example.dance4life_phone.ui.notifier.InviteNotifier

import com.dance4life.core.rlinference.RlCoachPolicy
import com.dance4life.core.rlinference.RlCoachPolicyFactory
import java.util.ArrayDeque
import kotlin.math.abs

class MainActivity : AppCompatActivity(), SensorEventListener {

    private lateinit var sensorProvider: SensorProvider
    private lateinit var locationProvider: LocationProvider
    private lateinit var deviceProvider: DeviceProvider
    private lateinit var controller: DanceController
    private lateinit var rlPolicy: RlCoachPolicy
    private lateinit var rlMetricsManager: RlMetricsManager

    // UI
    private lateinit var accelerometer_x_value : TextView
    private lateinit var accelerometer_y_value : TextView
    private lateinit var accelerometer_z_value : TextView
    private lateinit var rl_policy_value: TextView
    private lateinit var rl_steps_value: TextView
    private lateinit var rl_sedentary_value: TextView
    private lateinit var rl_energy_value: TextView
    private lateinit var rl_mobility_value: TextView
    private lateinit var rl_action_value: TextView
    private lateinit var rl_inference_count_value: TextView
    private lateinit var rl_source_value: TextView

    private lateinit var gyroscope_x_value: TextView
    private lateinit var gyroscope_y_value: TextView
    private lateinit var gyroscope_z_value: TextView

    private lateinit var latitude_value: TextView
    private lateinit var longitude_value: TextView
    private lateinit var country_value: TextView
    private lateinit var city_value: TextView
    private lateinit var street_value: TextView

    private lateinit var hr_value: TextView

    // RL inference state
    private var sedentaryMinutesEstimate: Int = 0
    private var lastSensorTimestampMs: Long = 0L
    private var lastCoachTimestampMs: Long = 0L
    private var lastActionId: String? = null
    private var currentStepsLastHour: Int = 0
    private var lastStepsWindowSnapshot: Int = 0
    private var lastRawStepCounter: Int? = null
    private val stepTimestampsMs = ArrayDeque<Long>()
    private var rlInferenceCount: Int = 0

    private var latestSensorSnapshot = SensorData(
        accX = 0f,
        accY = 0f,
        accZ = 0f,
        gyroX = 0f,
        gyroY = 0f,
        gyroZ = 0f,
        heartRate = 70,
        accMagnitude = 9.81,
        gyroMagnitude = 0.0,
    )

    private lateinit var sensorManager: SensorManager
    private var stepCounterSensor: Sensor? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_main)

        rl_policy_value = findViewById(R.id.rl_policy_value)
        rl_steps_value = findViewById(R.id.rl_steps_value)
        rl_sedentary_value = findViewById(R.id.rl_sedentary_value)
        rl_energy_value = findViewById(R.id.rl_energy_value)
        rl_mobility_value = findViewById(R.id.rl_mobility_value)
        rl_action_value = findViewById(R.id.rl_action_value)
        rl_inference_count_value = findViewById(R.id.rl_inference_count_value)
        rl_source_value = findViewById(R.id.rl_source_value)

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                "invite_channel",
                "Convites",
                NotificationManager.IMPORTANCE_HIGH
            )

            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
        //-------------------------
        rlPolicy = RlCoachPolicyFactory.create(this)
        sensorManager = getSystemService(SENSOR_SERVICE) as SensorManager
        stepCounterSensor = sensorManager.getDefaultSensor(Sensor.TYPE_STEP_COUNTER)
        rl_policy_value.text = rlPolicy.javaClass.simpleName

        // Providers
        deviceProvider = PhoneDeviceProvider(this)
        sensorProvider = PhoneSensorProvider(this)
        locationProvider = PhoneLocationProvider(this)

        rlMetricsManager = RlMetricsManager(
            context = this,
            repository = DataRepository(),
            userIdProvider = { deviceProvider.getUserId() },
        )

        // UI binding
        accelerometer_x_value = findViewById(R.id.accelerometer_x_value)
        accelerometer_y_value = findViewById(R.id.accelerometer_y_value)
        accelerometer_z_value = findViewById(R.id.accelerometer_z_value)

        gyroscope_x_value = findViewById(R.id.gyroscope_x_value)
        gyroscope_y_value = findViewById(R.id.gyroscope_y_value)
        gyroscope_z_value = findViewById(R.id.gyroscope_z_value)

        latitude_value = findViewById(R.id.latitude_value)
        longitude_value = findViewById(R.id.longitude_value)
        country_value = findViewById(R.id.country_value)
        city_value = findViewById(R.id.city_value)
        street_value = findViewById(R.id.street_value)

        hr_value = findViewById(R.id.hr_value)

        // Controller
        controller = DanceController(
            sensorProvider,
            locationProvider,
            DataRepository(),
            RitmoCalculator(),
            deviceProvider
        )

        controller.setInviteListener { id, user ->
            InviteNotifier.show(this, id, user)
        }
        controller.setMatchListener { user, score ->
            showMatchDialog(user, score)
        }

        // 🔥 SENSOR → UI
        controller.setSensorListener { data ->
            accelerometer_x_value.text = data.accX.toString()
            accelerometer_y_value.text = data.accY.toString()
            accelerometer_z_value.text = data.accZ.toString()

            gyroscope_x_value.text = data.gyroX.toString()
            gyroscope_y_value.text = data.gyroY.toString()
            gyroscope_z_value.text = data.gyroZ.toString()

            hr_value.text = "${data.heartRate} bpm"

                latestSensorSnapshot = data
                maybeRecommendCoaching(data)
        }

        // 📍 LOCATION → UI
        controller.setLocationListener { location ->
            latitude_value.text = location.latitude.toString()
            longitude_value.text = location.longitude.toString()

            country_value.text = location.country
            city_value.text = location.city
            street_value.text = location.street
        }

        // 🎵 RITMO → UI
        controller.setRitmoListener { ritmo ->
            Toast.makeText(this, "Ritmo: $ritmo", Toast.LENGTH_SHORT).show()
        }

        // Permissões
        if (checkSelfPermission(android.Manifest.permission.ACCESS_FINE_LOCATION)
            != android.content.pm.PackageManager.PERMISSION_GRANTED) {

            requestPermissions(
                arrayOf(android.Manifest.permission.ACCESS_FINE_LOCATION),
                100
            )
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q &&
            checkSelfPermission(android.Manifest.permission.ACTIVITY_RECOGNITION)
            != android.content.pm.PackageManager.PERMISSION_GRANTED
        ) {
            requestPermissions(
                arrayOf(android.Manifest.permission.ACTIVITY_RECOGNITION),
                300,
            )
        }

        if (checkSelfPermission(android.Manifest.permission.BODY_SENSORS)
            != android.content.pm.PackageManager.PERMISSION_GRANTED
        ) {
            requestPermissions(
                arrayOf(android.Manifest.permission.BODY_SENSORS),
                400,
            )
        }

        // polling matches
        /*
        handler = Handler(Looper.getMainLooper())
        runnable = object : Runnable {
            override fun run() {

                val userId = deviceProvider.getUserId()

                DataRepository().obterUpdates(userId) { body ->
                    runOnUiThread {
                        if (!body.isNullOrEmpty()) {
                            val jsonArray = JSONArray(body)

                            for (i in 0 until jsonArray.length()) {
                                val obj = jsonArray.getJSONObject(i)

                                if (obj.getString("type") == "match") {
                                    val user = obj.getString("user")
                                    val score = obj.getDouble("score")

                                    showMatchDialog(user, score)
                                }
                            }
                        }
                    }
                }

                handler.postDelayed(this, 5000)
            }
        }*/

        //Notificações
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
            if (checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)
                != android.content.pm.PackageManager.PERMISSION_GRANTED) {

                requestPermissions(
                    arrayOf(android.Manifest.permission.POST_NOTIFICATIONS),
                    200
                )
            }
        }
    }

    override fun onResume() {
        super.onResume()
        controller.start()
        rlMetricsManager.flushPending()
        stepCounterSensor?.also {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL)
        }
    }

    override fun onPause() {
        super.onPause()
        controller.stop()
        sensorManager.unregisterListener(this)
    }

    override fun onDestroy() {
        super.onDestroy()
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)

        if (requestCode == 100 &&
            grantResults.isNotEmpty() &&
            grantResults[0] == android.content.pm.PackageManager.PERMISSION_GRANTED) {

            controller.start()
        }
    }

    private fun showMatchDialog(user: String, score: Double) {
        AlertDialog.Builder(this)
            .setTitle("Novo Match!")
            .setMessage("Encontraste o $user!\nCompatibilidade: $score")
            .setPositiveButton("OK") { dialog, _ -> dialog.dismiss() }
            .show()
    }

    private fun maybeRecommendCoaching(data: SensorData) {
        val now = System.currentTimeMillis()
        updateSedentaryEstimate(now, currentStepsLastHour)

        if (now - lastCoachTimestampMs < RL_COACH_MIN_INTERVAL_MS) {
            return
        }

        val observation = MovementObservation(
            stepsLastHour = currentStepsLastHour,
            sedentaryMinutesToday = sedentaryMinutesEstimate,
            energyLevel = estimateEnergyLevel(data.heartRate),
            mobilityConfidence = estimateMobilityConfidence(data.accMagnitude, data.gyroMagnitude),
        )

        runRlInference(
            observation = observation,
            sensor = data,
            sourceLabel = getString(R.string.live_sensor),
            allowCadenceControl = true,
            nowMs = now,
        )
    }

    private fun runRlInference(
        observation: MovementObservation,
        sensor: SensorData,
        sourceLabel: String,
        allowCadenceControl: Boolean,
        nowMs: Long,
    ) {
        val recommendation = rlPolicy.recommend(observation)
        rlMetricsManager.recordInference(
            observation = observation,
            recommendation = recommendation,
            sensor = sensor,
            policyName = rlPolicy.javaClass.simpleName,
        )
        rlInferenceCount += 1
        updateRlMetricsUi(observation, recommendation, sourceLabel)

        val shouldNotify = recommendation.actionId != lastActionId ||
            nowMs - lastCoachTimestampMs >= RL_COACH_FORCE_NOTIFY_MS ||
            !allowCadenceControl

        if (shouldNotify) {
            Toast.makeText(
                this,
                "Coach: ${recommendation.title} (${recommendation.durationMinutes} min)",
                Toast.LENGTH_SHORT,
            ).show()
            lastActionId = recommendation.actionId
        }

        if (allowCadenceControl) {
            lastCoachTimestampMs = nowMs
        }
    }

    private fun updateRlMetricsUi(
        observation: MovementObservation,
        recommendation: MovementRecommendation,
        sourceLabel: String,
    ) {
        rl_policy_value.text = rlPolicy.javaClass.simpleName
        rl_steps_value.text = observation.stepsLastHour.toString()
        rl_sedentary_value.text = observation.sedentaryMinutesToday.toString()
        rl_energy_value.text = observation.energyLevel.toString()
        rl_mobility_value.text = observation.mobilityConfidence.toString()
        rl_action_value.text = recommendation.actionId
        rl_inference_count_value.text = rlInferenceCount.toString()
        rl_source_value.text = sourceLabel
    }

    private fun updateSedentaryEstimate(nowMs: Long, stepsLastHour: Int) {
        if (lastSensorTimestampMs == 0L) {
            lastSensorTimestampMs = nowMs
            lastStepsWindowSnapshot = stepsLastHour
            return
        }

        val elapsedMin = ((nowMs - lastSensorTimestampMs) / 60000f).coerceAtLeast(0f)
        lastSensorTimestampMs = nowMs
        val stepDelta = (stepsLastHour - lastStepsWindowSnapshot).coerceAtLeast(0)
        lastStepsWindowSnapshot = stepsLastHour

        if (stepDelta <= SEDENTARY_STEP_DELTA_THRESHOLD) {
            sedentaryMinutesEstimate += elapsedMin.toInt().coerceAtLeast(1)
        } else {
            sedentaryMinutesEstimate -= (elapsedMin * 2f).toInt().coerceAtLeast(1)
        }

        sedentaryMinutesEstimate = sedentaryMinutesEstimate.coerceIn(0, 480)
    }

    private fun estimateEnergyLevel(heartRate: Int): Int {
        val hr = heartRate.coerceIn(40, 200)
        return when {
            hr <= 65 -> 9
            hr <= 80 -> 8
            hr <= 95 -> 6
            hr <= 110 -> 4
            else -> 3
        }
    }

    private fun estimateMobilityConfidence(accMagnitude: Double, gyroMagnitude: Double): Int {
        val movementScore = (abs(accMagnitude - 9.81) * 1.5 + (gyroMagnitude * 0.5)).toInt()
        return movementScore.coerceIn(1, 10)
    }

    override fun onSensorChanged(event: SensorEvent) {
        if (event.sensor.type != Sensor.TYPE_STEP_COUNTER) return

        val now = System.currentTimeMillis()
        val totalSteps = event.values[0].toInt()

        val previous = lastRawStepCounter
        if (previous == null) {
            lastRawStepCounter = totalSteps
            return
        }

        val delta = (totalSteps - previous).coerceAtLeast(0)
        lastRawStepCounter = totalSteps

        if (delta > 0) {
            repeat(delta.coerceAtMost(200)) {
                stepTimestampsMs.addLast(now)
            }
        }

        val cutoff = now - ONE_HOUR_MS
        while (stepTimestampsMs.isNotEmpty() && stepTimestampsMs.first() < cutoff) {
            stepTimestampsMs.removeFirst()
        }

        currentStepsLastHour = stepTimestampsMs.size.coerceIn(0, 1000)
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) = Unit

    companion object {
        private const val RL_COACH_MIN_INTERVAL_MS = 20_000L
        private const val RL_COACH_FORCE_NOTIFY_MS = 60_000L
        private const val SEDENTARY_STEP_DELTA_THRESHOLD = 2
        private const val ONE_HOUR_MS = 3_600_000L
    }
}
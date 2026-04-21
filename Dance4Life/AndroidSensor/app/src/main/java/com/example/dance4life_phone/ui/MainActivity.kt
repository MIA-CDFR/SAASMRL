package com.example.dance4life_phone.ui

import android.app.NotificationChannel
import android.app.NotificationManager
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.widget.Toast
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.dance4life.core.data.model.EnvironmentData
import com.dance4life.core.data.model.LocationData
import com.dance4life.core.data.model.MovementRecommendation
import com.dance4life.core.data.model.SensorData
import com.dance4life.core.data.repository.DataRepository
import com.dance4life.core.domain.controller.DanceController
import com.dance4life.core.domain.device.DeviceProvider
import com.dance4life.core.domain.location.LocationProvider
import com.dance4life.core.domain.sensor.SensorProvider
import com.dance4life.core.rlinference.RlCoachPolicyFactory
import com.dance4life.core.utils.RitmoCalculator
import com.example.dance4life_phone.R
import com.example.dance4life_phone.domain.device.PhoneDeviceProvider
import com.example.dance4life_phone.domain.location.PhoneLocationProvider
import com.example.dance4life_phone.domain.sensor.PhoneSensorProvider
import com.example.dance4life_phone.ui.notifier.InviteNotifier

class MainActivity : AppCompatActivity() {

    private lateinit var sensorProvider: SensorProvider
    private lateinit var locationProvider: LocationProvider
    private lateinit var deviceProvider: DeviceProvider
    private lateinit var controller: DanceController

    private lateinit var handler: Handler
    private lateinit var runnable: Runnable

    private var sensorData by mutableStateOf<SensorData?>(null)
    private var locationData by mutableStateOf<LocationData?>(null)
    private var rhythm by mutableStateOf<Double?>(null)
    private var recommendation by mutableStateOf<MovementRecommendation?>(null)
    private var environmentData by mutableStateOf<EnvironmentData?>(null)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        setContent {
            DashboardScreen(
                sensorData = sensorData,
                locationData = locationData,
                rhythm = rhythm,
                recommendation = recommendation,
                environmentData = environmentData
            )
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                "invite_channel",
                "Convites",
                NotificationManager.IMPORTANCE_HIGH
            )

            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }

        deviceProvider = PhoneDeviceProvider(this)
        sensorProvider = PhoneSensorProvider(this)
        locationProvider = PhoneLocationProvider(this)

        controller = DanceController(
            sensorProvider,
            locationProvider,
            DataRepository(),
            RitmoCalculator(),
            deviceProvider,
            RlCoachPolicyFactory.create(this)
        )

        controller.setInviteListener { id, user ->
            InviteNotifier.show(this, id, user)
        }

        controller.setMatchListener { user, score ->
            showMatchDialog(user, score)
        }

        controller.setSensorListener { data ->
            sensorData = data
        }

        controller.setLocationListener { location ->
            locationData = location
        }

        controller.setRitmoListener { ritmoValue ->
            rhythm = ritmoValue
        }

        controller.setMovementRecommendationListener {
            recommendation = it
        }

        controller.setEnvironmentListener {
            environmentData = it
        }

        if (checkSelfPermission(android.Manifest.permission.ACCESS_FINE_LOCATION)
            != android.content.pm.PackageManager.PERMISSION_GRANTED
        ) {
            requestPermissions(
                arrayOf(android.Manifest.permission.ACCESS_FINE_LOCATION),
                100
            )
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)
                != android.content.pm.PackageManager.PERMISSION_GRANTED
            ) {
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
    }

    override fun onPause() {
        super.onPause()
        controller.stop()

        if (::handler.isInitialized) {
            handler.removeCallbacks(runnable)
        }
    }

    override fun onDestroy() {
        super.onDestroy()

        if (::handler.isInitialized) {
            handler.removeCallbacks(runnable)
        }
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)

        if (
            requestCode == 100 &&
            grantResults.isNotEmpty() &&
            grantResults[0] == android.content.pm.PackageManager.PERMISSION_GRANTED
        ) {
            controller.start()
        }
    }

    private fun showMatchDialog(user: String, score: Double) {
        AlertDialog.Builder(this)
            .setTitle("Novo Match!")
            .setMessage("Encontraste o $user!\nCompatibilidade: $score")
            .setPositiveButton("OK") { dialog, _ ->
                dialog.dismiss()
            }
            .show()
    }
}

@Composable
fun DashboardScreen(
    sensorData: SensorData?,
    locationData: LocationData?,
    rhythm: Double?,
    recommendation: MovementRecommendation?,
    environmentData: EnvironmentData?
) {
    Box(modifier = Modifier.fillMaxSize()) {

        Image(
            painter = painterResource(id = R.drawable.dance4life_android_background_3),
            contentDescription = null,
            modifier = Modifier.fillMaxSize(),
            contentScale = ContentScale.Crop
        )

        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black.copy(alpha = 0.45f))
        )

        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
            contentPadding = PaddingValues(top = 175.dp, bottom = 20.dp)
        ) {

            item {
                GlassCard {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {

                        Column(
                            verticalArrangement = Arrangement.spacedBy(16.dp),
                            modifier = Modifier.weight(1f)
                        ) {
                            Text(
                                text = "❤️ ${sensorData?.heartRate ?: "--"} bpm",
                                color = Color.White,
                                fontSize = 24.sp,
                                fontWeight = FontWeight.Bold
                            )

                            Text(
                                text = "💃 Ritmo ${rhythm?.let { "%.1f".format(it) } ?: "--"}",
                                color = Color(0xFFD7B4FF),
                                fontSize = 20.sp
                            )

                            if (recommendation != null) {
                                Text(
                                    text = "✨ ${recommendation.title}",
                                    color = Color(0xFFE8E6A7),
                                    fontSize = 18.sp,
                                    fontWeight = FontWeight.Medium
                                )
                            }
                        }

                        Box(
                            contentAlignment = Alignment.Center,
                            modifier = Modifier.size(180.dp)
                        ) {
                            CircularProgressIndicator(
                                progress = { ((sensorData?.heartRate ?: 0) / 120f).coerceIn(0f, 1f) },
                                modifier = Modifier.size(160.dp),
                                strokeWidth = 12.dp,
                                color = Color(0xFFC86BFF),
                                trackColor = Color.White.copy(alpha = 0.15f)
                            )

                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Text(
                                    text = "${sensorData?.heartRate ?: "--"}",
                                    color = Color.White,
                                    fontSize = 42.sp,
                                    fontWeight = FontWeight.Bold
                                )

                                Text(
                                    text = "bpm",
                                    color = Color.White.copy(alpha = 0.8f),
                                    fontSize = 18.sp
                                )
                            }
                        }
                    }
                }
            }

            item {
                GlassCard {
                    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {

                        SectionHeader("Sensores", "🧩")

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {

                            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                Text(
                                    text = "ACC: ${sensorData?.accMagnitude?.let { "%.2f".format(it) } ?: "--"}",
                                    color = Color.White,
                                    fontSize = 20.sp
                                )

                                Text("X: ${sensorData?.accX ?: "--"}", color = Color(0xFF7EB6FF))
                                Text("Y: ${sensorData?.accY ?: "--"}", color = Color(0xFF7EB6FF))
                                Text("Z: ${sensorData?.accZ ?: "--"}", color = Color(0xFF7EB6FF))
                            }

                            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                Text(
                                    text = "GYRO: ${sensorData?.gyroMagnitude?.let { "%.2f".format(it) } ?: "--"}",
                                    color = Color.White,
                                    fontSize = 20.sp
                                )

                                Text("X: ${sensorData?.gyroX ?: "--"}", color = Color(0xFFA8F0B3))
                                Text("Y: ${sensorData?.gyroY ?: "--"}", color = Color(0xFFA8F0B3))
                                Text("Z: ${sensorData?.gyroZ ?: "--"}", color = Color(0xFFA8F0B3))
                            }
                        }
                    }
                }
            }

            item {
                GlassCard {
                    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {

                        SectionHeader("Localização", "📍")

                        Text(
                            text = "${locationData?.city ?: "Desconhecido"}, ${locationData?.street ?: "--"}",
                            color = Color.White,
                            fontSize = 22.sp
                        )

                        Text(
                            text = "${locationData?.latitude ?: "--"}, ${locationData?.longitude ?: "--"}",
                            color = Color.White.copy(alpha = 0.7f),
                            fontSize = 16.sp
                        )
                    }
                }
            }

            item {
                GlassCard {
                    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {

                        SectionHeader("Ambiente", "🌡️")

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceAround
                        ) {
                            Text(
                                text = "☀️ ${environmentData?.temperature ?: "--"}°C",
                                color = Color.White,
                                fontSize = 28.sp
                            )

                            Text(
                                text = "💧 ${environmentData?.humidity ?: "--"}%",
                                color = Color.White,
                                fontSize = 28.sp
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun GlassCard(content: @Composable ColumnScope.() -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(28.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFF10182A).copy(alpha = 0.55f)
        ),
        border = BorderStroke(
            1.dp,
            Color.White.copy(alpha = 0.08f)
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp),
            content = content
        )
    }
}

@Composable
fun SectionHeader(title: String, icon: String) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Text(text = icon, fontSize = 24.sp)

        Text(
            text = title,
            color = Color.White,
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold
        )
    }
}
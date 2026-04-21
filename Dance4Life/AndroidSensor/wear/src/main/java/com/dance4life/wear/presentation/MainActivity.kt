package com.dance4life.wear.presentation

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.wear.compose.material3.Text
import androidx.wear.compose.material3.Button
import com.dance4life.core.data.model.LocationData
import com.dance4life.core.data.model.SensorData
import com.dance4life.core.data.repository.DataRepository
import com.dance4life.core.domain.controller.DanceController
import com.dance4life.core.utils.RitmoCalculator
import com.dance4life.wear.domain.device.WearDeviceProvider
import com.dance4life.wear.domain.location.WearLocationProvider
import com.dance4life.wear.domain.sensor.WearSensorProvider
import com.dance4life.wear.R
import kotlinx.coroutines.delay
import com.dance4life.wear.presentation.notifier.InviteNotifier
import androidx.compose.ui.platform.LocalContext
import com.dance4life.core.data.model.MovementRecommendation
import com.dance4life.core.rlinference.RlCoachPolicyFactory
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.pager.HorizontalPager
import com.dance4life.core.data.model.EnvironmentData
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.wear.compose.material.Card
import androidx.wear.compose.material.CircularProgressIndicator
import androidx.wear.compose.material.MaterialTheme


import androidx.compose.runtime.Composable

import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

class MainActivity : ComponentActivity() {

    private lateinit var controller: DanceController

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        window.addFlags(android.view.WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        controller = DanceController(
            sensorProvider = WearSensorProvider(this),
            locationProvider = WearLocationProvider(this), // ✅ REAL
            repository = DataRepository(),
            ritmoCalculator = RitmoCalculator(),
            deviceProvider = WearDeviceProvider(this),
            rlCoachPolicy = RlCoachPolicyFactory.create(this)
        )

        setContent {

            var hasPermission by remember { mutableStateOf(false) }

            val permissionLauncher = rememberLauncherForActivityResult(
                contract = ActivityResultContracts.RequestMultiplePermissions()
            ) { permissions ->
                hasPermission =
                    permissions[Manifest.permission.BODY_SENSORS] == true &&
                            permissions[Manifest.permission.ACCESS_FINE_LOCATION] == true
            }

            LaunchedEffect(Unit) {
                hasPermission =
                    checkSelfPermission(Manifest.permission.BODY_SENSORS) ==
                            android.content.pm.PackageManager.PERMISSION_GRANTED &&
                            checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) ==
                            android.content.pm.PackageManager.PERMISSION_GRANTED &&
                            (
                                Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU ||
                                    checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) ==
                                    PackageManager.PERMISSION_GRANTED
                            )

                while (true) {
                    delay(1000)
                }
            }

            WearApp(
                controller = controller,
                hasPermission = hasPermission,
                onRequestPermission = {

                    val permissions = mutableListOf(
                        Manifest.permission.BODY_SENSORS,
                        Manifest.permission.ACTIVITY_RECOGNITION,
                        Manifest.permission.ACCESS_FINE_LOCATION
                    )

                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                        permissions.add(Manifest.permission.POST_NOTIFICATIONS)
                    }

                    permissionLauncher.launch(permissions.toTypedArray())
                }
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
    }
}

@Composable
fun WearApp(
    controller: DanceController,
    hasPermission: Boolean,
    onRequestPermission: () -> Unit
) {
    if (!hasPermission) {
        PermissionScreen(onRequestPermission)
    } else {

        var sensorData by remember { mutableStateOf<SensorData?>(null) }
        var locationData by remember { mutableStateOf<LocationData?>(null) }
        var rhythm by remember { mutableStateOf<Double?>(null) }
        var recommendation by remember { mutableStateOf<MovementRecommendation?>(null) }
        var environmentData by remember { mutableStateOf<EnvironmentData?>(null) }

        val context = LocalContext.current
        val pagerState = rememberPagerState(pageCount = { 2 })

        LaunchedEffect(Unit) {

            controller.setSensorListener { data ->
                sensorData = data
            }

            controller.setLocationListener { location ->
                locationData = location
            }

            controller.setMovementRecommendationListener {
                recommendation = it
            }

            controller.setRitmoListener { ritmoValue ->
                rhythm = ritmoValue
            }

            controller.setInviteListener { id, user ->
                InviteNotifier.show(context, id, user)
            }

            controller.setEnvironmentListener { data ->
                environmentData = data
            }

            controller.start()
        }

        DisposableEffect(Unit) {
            onDispose {
                controller.stop()
            }
        }


        HorizontalPager(
            state = pagerState,
            modifier = Modifier.fillMaxSize()
        ) { page ->

            when (page) {
                0 -> {
                    MainScreen(
                        sensorData = sensorData,
                        locationData = locationData,
                        rhythm = rhythm,
                        recommendation = recommendation,
                        environmentData = environmentData
                    )
                }

                1 -> {
                    StatsScreen(
                        sensorData = sensorData,
                        locationData = locationData,
                        rhythm = rhythm,
                        recommendation = recommendation,
                        environmentData = environmentData
                    )
                }
            }
        }
    }
}

@Composable
fun PermissionScreen(onRequestPermission: () -> Unit) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black),
        contentAlignment = Alignment.Center
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {

            Text("Permissões necessárias", color = Color.White, fontSize = 14.sp)

            Spacer(Modifier.height(8.dp))

            Text("Sensores + Localização", color = Color.Gray, fontSize = 12.sp)

            Spacer(Modifier.height(12.dp))

            Button(onClick = onRequestPermission) {
                Text("Permitir")
            }
        }
    }
}

@Composable
fun MainScreen2(
    sensorData: SensorData?,
    locationData: LocationData?,
    rhythm: Double?,
    recommendation: MovementRecommendation?,
    environmentData: EnvironmentData?
) {

    Box(
        modifier = Modifier.fillMaxSize()
    ) {

        // BACKGROUND
        Image(
            painter = painterResource(id = R.drawable.dace4life_android_wear_background),
            contentDescription = null,
            modifier = Modifier.fillMaxSize(),
            contentScale = ContentScale.Crop
        )

        // OVERLAY
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black.copy(alpha = 0.4f))
        )

        Column(
            modifier = Modifier
                .fillMaxSize(),
                //.padding(8.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {

            Spacer(modifier = Modifier.height(60.dp))

            // SENSORES
            if (sensorData != null) {
                val d = sensorData

                Text(
                    text = "\u2764\uFE0F️ ${if (d.heartRate > 0) d.heartRate else "--"} bpm",
                    color = Color.White,
                    fontSize = 14.sp
                )

                Spacer(modifier = Modifier.height(6.dp))

                Text(
                    text = "\uD83D\uDCC8 ACC: ${"%.1f".format(d.accMagnitude)}",
                    color = Color.White,
                    fontSize = 12.sp
                )

                Spacer(modifier = Modifier.height(6.dp))

                Text(
                    text = "\uD83D\uDD04 GYRO: ${"%.1f".format(d.gyroMagnitude)}",
                    color = Color.White,
                    fontSize = 12.sp
                )
            } else {
                Text("A aguardar sensores...", color = Color.White)
            }

            if (rhythm != null) {
                Spacer(modifier = Modifier.height(6.dp))

                Text(
                    text = "\uD83D\uDC83 Ritmo: ${"%.1f".format(rhythm)}",
                    color = Color.White,
                    fontSize = 12.sp
                )
            }

            // LOCALIZAÇÃO
            if (locationData != null) {

                Spacer(modifier = Modifier.height(6.dp))

                Text(
                    text = "\uD83D\uDCCD ${locationData.city ?: "Desconhecido"}",
                    color = Color.White,
                    fontSize = 12.sp
                )

            } /*else {
                Spacer(modifier = Modifier.height(6.dp))
                Text("Sem localização...", color = Color.Gray, fontSize = 12.sp)
            }*/

            // AMBIENTE
            if (environmentData != null) {

                Spacer(modifier = Modifier.height(6.dp))

                Text(
                    text = "\uD83C\uDF21\uFE0F ${environmentData.temperature ?: "--"}°C",
                    color = Color.White,
                    fontSize = 12.sp
                )

            } /*else {
                Spacer(modifier = Modifier.height(6.dp))
                Text("Sem dados temp...", color = Color.Gray, fontSize = 12.sp)
            }*/

            if (recommendation != null) {
                Spacer(modifier = Modifier.height(6.dp))

                Text(
                    text = recommendation.title,
                    color = Color.Blue,
                    fontSize = 9.sp
                )
            }
        }
    }
}
@Composable
fun MainScreen(
    sensorData: SensorData?,
    locationData: LocationData?,
    rhythm: Double?,
    recommendation: MovementRecommendation?,
    environmentData: EnvironmentData?
) {
    Box(modifier = Modifier.fillMaxSize()) {

        Image(
            painter = painterResource(id = R.drawable.dace4life_android_wear_background),
            contentDescription = null,
            modifier = Modifier.fillMaxSize(),
            contentScale = ContentScale.Crop
        )

        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black.copy(alpha = 0.45f))
        )

        Column(
            modifier = Modifier
                .fillMaxSize()
                  .padding(horizontal = 40.dp, vertical = 40.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Top
        ) {

            Spacer(modifier = Modifier.height(38.dp))
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 2.dp),
                shape = RoundedCornerShape(12.dp),
                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFF10182A).copy(alpha = 0.65f)
                ),
                border = BorderStroke(
                    1.dp,
                    Color.White.copy(alpha = 0.08f)
                )
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 8.dp, vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {

                    Column(
                        verticalArrangement = Arrangement.spacedBy(4.dp),
                        modifier = Modifier.weight(1f)
                    ) {
                        Text(
                            text = "❤️ ${sensorData?.heartRate ?: "--"} bpm",
                            color = Color.White,
                            fontSize = 9.sp,
                            fontWeight = FontWeight.Bold
                        )

                        Text(
                            text = "💃 ${rhythm?.let { "%.1f".format(it) } ?: "--"}",
                            color = Color(0xFFD7B4FF),
                            fontSize = 9.sp
                        )

                        Text(
                            text = "📍 ${locationData?.city ?: "--"}",
                            color = Color.White.copy(alpha = 0.85f),
                            fontSize = 9.sp
                        )
                    }

                    Box(
                        contentAlignment = Alignment.Center,
                        modifier = Modifier.size(50.dp)
                    ) {
                        CircularProgressIndicator(
                            progress = ((sensorData?.heartRate ?: 0) / 120f).coerceIn(0f, 1f),
                            modifier = Modifier.size(45.dp),
                            strokeWidth = 5.dp,
                            indicatorColor = Color(0xFFC86BFF),
                            trackColor = Color.White.copy(alpha = 0.12f)
                        )

                        Text(
                            text = "${sensorData?.heartRate ?: "--"}",
                            color = Color.White,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                MiniGlassCard(
                    modifier = Modifier.weight(1f),
                    title = "ACC",
                    value = sensorData?.accMagnitude?.let { "%.1f".format(it) } ?: "--",
                    accent = Color(0xFF7EB6FF)
                )

                MiniGlassCard(
                    modifier = Modifier.weight(1f),
                    title = "GYRO",
                    value = sensorData?.gyroMagnitude?.let { "%.1f".format(it) } ?: "--",
                    accent = Color(0xFFA8F0B3)
                )
            }

            Spacer(modifier = Modifier.height(2.dp))

            Card(
                modifier = Modifier.fillMaxWidth().padding(bottom = 2.dp),
                shape = RoundedCornerShape(12.dp),

                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFF10182A).copy(alpha = 0.55f)
                )
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 8.dp, vertical = 5.dp),
                    verticalArrangement = Arrangement.spacedBy(1.dp)
                ) {
                    Text(
                        text = "🌡️ ${environmentData?.temperature ?: "--"}°C",
                        color = Color.White,
                        fontSize = 9.sp
                    )

                    if (recommendation != null) {
                        Text(
                            text = recommendation.title,
                            color = Color(0xFFE8E6A7),
                            fontSize = 9.sp,
                            fontWeight = FontWeight.Medium
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun MiniGlassCard(
    modifier: Modifier = Modifier,
    title: String,
    value: String,
    accent: Color
) {
    Card(
        modifier = modifier,
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFF10182A).copy(alpha = 0.55f)
        ),
        border = BorderStroke(
            1.dp,
            Color.White.copy(alpha = 0.06f)
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 2.dp, horizontal = 2.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = title,
                color = accent,
                fontSize = 9.sp,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(2.dp))

            Text(
                text = value,
                color = Color.White,
                fontSize = 9.sp,
                fontWeight = FontWeight.Bold
            )
        }
    }
}


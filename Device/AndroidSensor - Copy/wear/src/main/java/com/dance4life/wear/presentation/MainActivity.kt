package com.dance4life.wear.presentation

import android.Manifest
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
            deviceProvider = WearDeviceProvider(this)
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
                            android.content.pm.PackageManager.PERMISSION_GRANTED

                while (true) {
                    delay(1000)
                }
            }

            WearApp(
                controller = controller,
                hasPermission = hasPermission,
                onRequestPermission = {
                    permissionLauncher.launch(
                        arrayOf(
                            Manifest.permission.BODY_SENSORS,
                            Manifest.permission.ACTIVITY_RECOGNITION,
                            Manifest.permission.ACCESS_FINE_LOCATION // 🔥 IMPORTANTE
                        )
                    )
                }
            )
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
        MainScreen(controller)
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
fun MainScreen(controller: DanceController) {

    var sensorData by remember { mutableStateOf<SensorData?>(null) }
    var locationData by remember { mutableStateOf<LocationData?>(null) }
    var ritmo by remember { mutableStateOf<Double?>(null) }

    /*
    LaunchedEffect(Unit) {

        controller.setSensorListener { data ->
            sensorData = data
        }

        controller.setLocationListener { location ->
            Log.d("WEAR", "LOCATION: ${location.latitude}, ${location.longitude}")
            locationData = location
        }

        controller.start()
    }*/

    LaunchedEffect(Unit) {

        controller.setSensorListener { data ->
            sensorData = data
        }

        controller.setLocationListener { location ->
            Log.d("WEAR", "LOCATION: ${location.latitude}, ${location.longitude}")
            locationData = location
        }

        /*
        // 🔥 OPCIONAL: ouvir ritmo
        controller.setRitmoListener { ritmoValue ->
            Log.d("WEAR", "RITMO: $ritmoValue")
        }*/

        controller.setRitmoListener { ritmoValue ->
            ritmo = ritmoValue
        }


        controller.start()

        // 🔥 LOOP PARA CALCULAR RITMO (igual ao mobile)
        /*while (true) {
            delay(10000) // 10 segundos
            controller.calcularRitmo()
        }*/
        //controller.calcularRitmo()
    }

    DisposableEffect(Unit) {
        onDispose {
            controller.stop()
        }
    }

    Box(
        modifier = Modifier.fillMaxSize()
    ) {

        // 🖼️ BACKGROUND
        Image(
            painter = painterResource(id = R.drawable.dace4life_android_wear_background),
            contentDescription = null,
            modifier = Modifier.fillMaxSize(),
            contentScale = ContentScale.Crop
        )

        // 🔳 OVERLAY
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black.copy(alpha = 0.4f))
        )

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(8.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {

            // 📍 LOCALIZAÇÃO
            if (locationData != null) {
                Text(
                    text = "📍 ${locationData!!.city ?: "Desconhecido"}",
                    color = Color.White,
                    fontSize = 12.sp
                )

                Text(
                    text = "${locationData!!.latitude}, ${locationData!!.longitude}",
                    color = Color.LightGray,
                    fontSize = 10.sp
                )

                Spacer(modifier = Modifier.height(8.dp))
            } else {
                Text("Sem localização...", color = Color.Gray, fontSize = 10.sp)
                Spacer(modifier = Modifier.height(8.dp))
            }

            // ❤️ SENSORES
            if (sensorData != null) {
                val d = sensorData!!

                Text(
                    text = "❤️ ${if (d.heartRate > 0) d.heartRate else "--"}",
                    color = Color.White,
                    fontSize = 16.sp
                )

                Text(
                    text = "\uD83D\uDCC8 ACC:: ${"%.1f".format(d.accMagnitude)}",
                    color = Color.White,
                    fontSize = 12.sp
                )

                Text(
                    text = "X: ${"%.1f".format(d.accX)}",
                    color = Color.White,
                    fontSize = 12.sp
                )
                Text(
                    text = "Y: ${"%.1f".format(d.accY)}",
                    color = Color.White,
                    fontSize = 12.sp
                )
                Text(
                    text = "Z: ${"%.1f".format(d.accZ)}",
                    color = Color.White,
                    fontSize = 12.sp
                )

                Text(
                    text = "\uD83D\uDD04 GYRO: ${"%.1f".format(d.gyroMagnitude)}",
                    color = Color.White,
                    fontSize = 12.sp
                )
                Text(
                    text = "X: ${"%.1f".format(d.gyroX)}",
                    color = Color.White,
                    fontSize = 12.sp
                )
                Text(
                    text = "Y: ${"%.1f".format(d.gyroY)}",
                    color = Color.White,
                    fontSize = 12.sp
                )
                Text(
                    text = "Z: ${"%.1f".format(d.gyroZ)}",
                    color = Color.White,
                    fontSize = 12.sp
                )
            } else {
                Text("A aguardar sensores...", color = Color.White)
            }

            if (ritmo != null) {
                Text(
                    text = "💃 Ritmo: ${"%.1f".format(ritmo)}",
                    color = Color.White,
                    fontSize = 14.sp
                )
            }
        }
    }
}
/*
@Composable
fun MainScreen(controller: DanceController) {

    var sensorData by remember { mutableStateOf<SensorData?>(null) }
    var locationData by remember { mutableStateOf< LocationData?>(null) }

    LaunchedEffect(Unit) {

        // 🔥 ligar ao controller (já funciona com o teu código)
        controller.setSensorListener { data ->
            sensorData = data
        }

        controller.setLocationListener { location ->
            locationData = location
        }

        controller.start()
    }

    DisposableEffect(Unit) {
        onDispose {
            controller.stop()
        }
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black)
            .padding(8.dp),
        contentAlignment = Alignment.Center
    ) {

        if (sensorData == null) {

            Text(
                text = "A aguardar dados...",
                color = Color.Gray
            )

        } else {

            val d = sensorData!!

            Text(
                text = """
                    ❤️ HR: ${d.heartRate}

                    📈 ACC:
                    X: ${"%.2f".format(d.accX)}
                    Y: ${"%.2f".format(d.accY)}
                    Z: ${"%.2f".format(d.accZ)}

                    🔄 GYRO:
                    X: ${"%.2f".format(d.gyroX)}
                    Y: ${"%.2f".format(d.gyroY)}
                    Z: ${"%.2f".format(d.gyroZ)}

                    ⚡ ACC: ${"%.2f".format(d.accMagnitude)}
                    ⚡ GYRO: ${"%.2f".format(d.gyroMagnitude)}
                """.trimIndent(),
                color = Color.White,
                fontSize = 10.sp
            )
        }
    }
}*/

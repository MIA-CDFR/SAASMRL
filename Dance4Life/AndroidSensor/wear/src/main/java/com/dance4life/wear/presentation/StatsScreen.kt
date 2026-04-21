package com.dance4life.wear.presentation

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.runtime.Composable
import androidx.wear.compose.material3.Text
import com.dance4life.core.data.model.EnvironmentData
import com.dance4life.core.data.model.LocationData
import com.dance4life.core.data.model.MovementRecommendation
import com.dance4life.core.data.model.SensorData
import com.dance4life.wear.R
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextDecoration

@Composable
fun StatsScreen(
    sensorData: SensorData?,
    locationData: LocationData?,
    rhythm: Double?,
    recommendation: MovementRecommendation?,
    environmentData: EnvironmentData?
) {
    val scrollState = rememberScrollState()

    Box(
        modifier = Modifier.fillMaxSize()
    ) {

        Image(
            painter = painterResource(id = R.drawable.dace4life_android_wear_background),
            contentDescription = null,
            modifier = Modifier.fillMaxSize(),
            contentScale = ContentScale.Crop
        )

        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color.Black.copy(alpha = 0.4f))
        )

        Column(
            modifier = Modifier.fillMaxSize()
        ) {

            Spacer(modifier = Modifier.height(75.dp))

            Text(
                text = "Dados dos Sensores",
                color = Color.White,
                fontSize = 12.sp,
                fontWeight = FontWeight.Bold,
                textDecoration = TextDecoration.Underline,
                modifier = Modifier.align(Alignment.CenterHorizontally)
            )

            Spacer(modifier = Modifier.height(12.dp))

            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(scrollState)
                    .padding(horizontal = 8.dp),
                verticalArrangement = Arrangement.Top,
                horizontalAlignment = Alignment.CenterHorizontally
            ) {


                // SENSORES
                if (sensorData != null) {

                    val d = sensorData

                    Text(
                        text = "Frequência Cardiaca:",
                        color = Color.White,
                        fontSize = 12.sp,
                        textDecoration = TextDecoration.Underline
                    )

                    Spacer(modifier = Modifier.height(6.dp))

                    Text(
                        text = "HR: ${if (d.heartRate > 0) d.heartRate else "--"} bpm",
                        color = Color.White,
                        fontSize = 12.sp
                    )

                    Spacer(modifier = Modifier.height(6.dp))

                    Text(
                        text = "Acelerometro:",
                        color = Color.White,
                        fontSize = 12.sp,
                        textDecoration = TextDecoration.Underline
                    )

                    Spacer(modifier = Modifier.height(6.dp))

                    Text(
                        text = "X: ${"%.1f".format(d.accX)}",
                        color = Color.White,
                        fontSize = 10.sp
                    )
                    Spacer(modifier = Modifier.height(6.dp))

                    Text(
                        text = "Y: ${"%.1f".format(d.accY)}",
                        color = Color.White,
                        fontSize = 10.sp
                    )

                    Spacer(modifier = Modifier.height(6.dp))

                    Text(
                        text = "Z: ${"%.1f".format(d.accZ)}",
                        color = Color.White,
                        fontSize = 10.sp
                    )

                    Spacer(modifier = Modifier.height(6.dp))

                    Text(
                        text = "Giroscópio:",
                        color = Color.White,
                        fontSize = 12.sp,
                        textDecoration = TextDecoration.Underline
                    )

                    Spacer(modifier = Modifier.height(6.dp))

                    Text(
                        text = "X: ${"%.1f".format(d.gyroX)}",
                        color = Color.White,
                        fontSize = 10.sp
                    )

                    Spacer(modifier = Modifier.height(6.dp))

                    Text(
                        text = "Y: ${"%.1f".format(d.gyroY)}",
                        color = Color.White,
                        fontSize = 10.sp
                    )

                    Spacer(modifier = Modifier.height(6.dp))

                    Text(
                        text = "Z: ${"%.1f".format(d.gyroZ)}",
                        color = Color.White,
                        fontSize = 10.sp
                    )
                } else {
                    Spacer(modifier = Modifier.height(6.dp))
                    Text("A aguardar sensores...", color = Color.White)
                }

                // LOCALIZAÇÃO
                if (locationData != null) {

                    Spacer(modifier = Modifier.height(6.dp))

                    Text(
                        text = "Localização:",
                        color = Color.White,
                        fontSize = 12.sp,
                        textDecoration = TextDecoration.Underline
                    )

                    Spacer(modifier = Modifier.height(6.dp))

                    Text(
                        text = "Latitude: ${locationData.latitude}",
                        color = Color.LightGray,
                        fontSize = 10.sp
                    )

                    Text(
                        text = "Longitude: ${locationData.longitude}",
                        color = Color.LightGray,
                        fontSize = 10.sp
                    )

                    Spacer(modifier = Modifier.height(6.dp))

                    Text(
                        text = "Cidade: ${locationData.city ?: "Desconhecido"}",
                        color = Color.White,
                        fontSize = 12.sp
                    )

                    Spacer(modifier = Modifier.height(6.dp))

                    Text(
                        text = "Rua: ${locationData.street ?: "Desconhecido"}",
                        color = Color.White,
                        fontSize = 12.sp
                    )
                } /*else {
                    Spacer(modifier = Modifier.height(6.dp))
                    Text("Sem localização...", color = Color.Gray, fontSize = 10.sp)
                    Spacer(modifier = Modifier.height(8.dp))
                }*/

                // AMBIENTE
                if (environmentData != null) {

                    Spacer(modifier = Modifier.height(6.dp))

                    Text(
                        text = "Ambiente:",
                        color = Color.White,
                        fontSize = 12.sp,
                        textDecoration = TextDecoration.Underline
                    )

                    Spacer(modifier = Modifier.height(6.dp))

                    Text(
                        text = "Temperatura: ${environmentData.temperature ?: "--"}°C",
                        color = Color.White,
                        fontSize = 10.sp
                    )

                    Spacer(modifier = Modifier.height(6.dp))

                    Text(
                        text = "Humidade: ${environmentData.humidity ?: "--"}%",
                        color = Color.White,
                        fontSize = 10.sp
                    )


                }/* else {
                    Spacer(modifier = Modifier.height(6.dp))
                    Text("Sem temperatura...", color = Color.Gray, fontSize = 12.sp)
                }*/

                Spacer(modifier = Modifier.height(100.dp))
            }
        }
    }
}
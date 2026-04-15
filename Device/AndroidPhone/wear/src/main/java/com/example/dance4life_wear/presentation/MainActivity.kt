/* While this template provides a good starting point for using Wear Compose, you can always
 * take a look at https://github.com/android/wear-os-samples/tree/main/ComposeStarter to find the
 * most up to date changes to the libraries and their usages.
 */

package com.example.dance4life_wear.presentation

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.wear.compose.foundation.lazy.TransformingLazyColumn
import androidx.wear.compose.foundation.lazy.rememberTransformingLazyColumnState
import androidx.wear.compose.material3.AppScaffold
import androidx.wear.compose.material3.Button
import androidx.wear.compose.material3.ButtonDefaults
import androidx.wear.compose.material3.EdgeButton
import androidx.wear.compose.material3.ListHeader
import androidx.wear.compose.material3.MaterialTheme
import androidx.wear.compose.material3.ScreenScaffold
import androidx.wear.compose.material3.SurfaceTransformation
import androidx.wear.compose.material3.Text
import androidx.wear.compose.material3.lazy.rememberTransformationSpec
import androidx.wear.compose.material3.lazy.transformedHeight
import androidx.wear.compose.ui.tooling.preview.WearPreviewDevices
import androidx.wear.compose.ui.tooling.preview.WearPreviewFontScales
import com.example.dance4life_wear.R
import com.example.dance4life_wear.presentation.theme.Dance4Life_mobileTheme
import androidx.compose.runtime.*
import androidx.compose.runtime.DisposableEffect

class MainActivity : ComponentActivity() {

    private val ritmoCalculator = RitmoCalculator()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {

            var heartRate by remember { mutableStateOf(0) }
            var ritmo by remember { mutableStateOf(0.0) }

            val sensorHelper = remember {
                SensorHelper(this) { data ->

                    heartRate = data.heartRate

                    val result = ritmoCalculator.calcular(
                        listOf(data.accMagnitude.toFloat()),
                        listOf(data.gyroMagnitude.toFloat()),
                        listOf(data.heartRate)
                    )

                    ritmo = result.ritmo
                }
            }

            DisposableEffect(Unit) {
                sensorHelper.start()

                onDispose {
                    sensorHelper.stop()
                }
            }

            WearApp(heartRate, ritmo)
        }
    }
}

@Composable
fun WearApp(heartRate: Int, ritmo: Double) {

    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = "❤️ $heartRate bpm")
        Text(text = "🔥 Ritmo: ${"%.2f".format(ritmo)}")
    }
}

@WearPreviewDevices
@WearPreviewFontScales
@Composable
fun DefaultPreview() {
    WearApp(heartRate = 80, ritmo = 12.5)
}
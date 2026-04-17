package com.dance4life.core.rlinference

import android.content.Context
import com.dance4life.core.data.model.MovementObservation
import com.dance4life.core.data.model.MovementRecommendation
import ai.onnxruntime.OnnxTensor
import ai.onnxruntime.OrtEnvironment
import ai.onnxruntime.OrtSession
import java.io.File
import java.nio.FloatBuffer

class OnnxRlCoachPolicy(
    context: Context,
    modelAssetPath: String = DEFAULT_MODEL_ASSET_PATH,
) : RlCoachPolicy {

    private val ortEnvironment: OrtEnvironment = OrtEnvironment.getEnvironment()
    private val ortSession: OrtSession
    private val inputName: String

    init {
        val modelFile = copyAssetToCache(context.applicationContext, modelAssetPath)
        ortSession = ortEnvironment.createSession(modelFile.absolutePath, OrtSession.SessionOptions())
        inputName = ortSession.inputNames.first()
    }

    override fun recommend(observation: MovementObservation): MovementRecommendation {
        val input = floatArrayOf(
            toActivityLevel(observation),
            toPhysicalFatigue(observation),
            toIrritationLevel(observation),
        )

        val action = inferAction(input)
        return toRecommendation(action)
    }

    private fun inferAction(input: FloatArray): Int {
        val shape = longArrayOf(1, 3)
        val inputTensor = OnnxTensor.createTensor(ortEnvironment, FloatBuffer.wrap(input), shape)

        inputTensor.use { tensor ->
            ortSession.run(mapOf(inputName to tensor)).use { output ->
                @Suppress("UNCHECKED_CAST")
                val logits = (output[0].value as Array<FloatArray>)[0]
                return logits.indices.maxByOrNull { logits[it] } ?: 0
            }
        }
    }

    private fun toRecommendation(action: Int): MovementRecommendation {
        return when (action) {
            0 -> MovementRecommendation(
                actionId = "silence",
                title = "Silent recovery window",
                durationMinutes = 1,
                encouragementMessage = "Recovery is part of progress. We will check in again soon.",
            )

            1 -> MovementRecommendation(
                actionId = "low_intensity",
                title = "Low-intensity movement cue",
                durationMinutes = 2,
                encouragementMessage = "A gentle move keeps momentum without overload.",
            )

            2 -> MovementRecommendation(
                actionId = "medium_intensity",
                title = "Moderate coaching suggestion",
                durationMinutes = 5,
                encouragementMessage = "Great balance: this intensity supports healthy activity.",
            )

            else -> MovementRecommendation(
                actionId = "high_intensity",
                title = "High-intensity challenge",
                durationMinutes = 10,
                encouragementMessage = "Strong push detected. Keep it brief and controlled.",
            )
        }
    }

    // Model expects state features in [0, 10] ordered as
    // [activity_level, physical_fatigue, irritation_level].
    private fun toActivityLevel(observation: MovementObservation): Float {
        val steps = observation.stepsLastHour.coerceIn(0, 1000)
        return (steps / 100f).coerceIn(0f, 10f)
    }

    private fun toPhysicalFatigue(observation: MovementObservation): Float {
        val sedentaryPressure = (observation.sedentaryMinutesToday.coerceIn(0, 480) / 480f) * 5f
        val lowEnergyPressure = ((10 - observation.energyLevel.coerceIn(0, 10)) / 10f) * 5f
        return (sedentaryPressure + lowEnergyPressure).coerceIn(0f, 10f)
    }

    private fun toIrritationLevel(observation: MovementObservation): Float {
        val sedentaryBurden = (observation.sedentaryMinutesToday.coerceIn(0, 480) / 480f) * 6f
        val lowConfidenceBurden = ((10 - observation.mobilityConfidence.coerceIn(0, 10)) / 10f) * 4f
        return (sedentaryBurden + lowConfidenceBurden).coerceIn(0f, 10f)
    }

    private fun copyAssetToCache(context: Context, assetPath: String): File {
        val outFile = File(context.cacheDir, assetPath.substringAfterLast('/'))
        if (outFile.exists() && outFile.length() > 0L) {
            return outFile
        }

        context.assets.open(assetPath).use { input ->
            outFile.outputStream().use { output ->
                input.copyTo(output)
            }
        }

        return outFile
    }

    companion object {
        const val DEFAULT_MODEL_ASSET_PATH = "models/dance4life_coach_v2_ppo.onnx"
    }
}

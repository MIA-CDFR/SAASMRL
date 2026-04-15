package com.dance4life.plugins.rlinference

import android.content.Context
import com.dance4life.core.domain.model.MovementObservation
import com.dance4life.core.domain.model.MovementRecommendation
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
            normalizeSteps(observation.stepsLastHour),
            normalizeSedentary(observation.sedentaryMinutesToday),
            normalizeLevel(observation.energyLevel),
            normalizeLevel(observation.mobilityConfidence),
        )

        val action = inferAction(input)
        return toRecommendation(action)
    }

    private fun inferAction(input: FloatArray): Int {
        val shape = longArrayOf(1, 4)
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
                actionId = "rest",
                title = "Mindful breathing pause",
                durationMinutes = 1,
                encouragementMessage = "A short pause counts. We will move in the next cycle.",
            )

            1 -> MovementRecommendation(
                actionId = "stretch_2min",
                title = "2-minute stretch break",
                durationMinutes = 2,
                encouragementMessage = "Great choice. Gentle stretching improves mobility and comfort.",
            )

            2 -> MovementRecommendation(
                actionId = "walk_5min",
                title = "5-minute gentle walk",
                durationMinutes = 5,
                encouragementMessage = "Nice momentum. A short walk helps circulation and energy.",
            )

            else -> MovementRecommendation(
                actionId = "dance_10min",
                title = "10-minute dance session",
                durationMinutes = 10,
                encouragementMessage = "Amazing. Dancing boosts mood, balance, and cardiovascular health.",
            )
        }
    }

    private fun normalizeSteps(value: Int): Float = (value / 1000f).coerceIn(0f, 1f)

    private fun normalizeSedentary(value: Int): Float = (value / 480f).coerceIn(0f, 1f)

    private fun normalizeLevel(value: Int): Float = (value / 10f).coerceIn(0f, 1f)

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
        const val DEFAULT_MODEL_ASSET_PATH = "models/dance4life_coach_v1.onnx"
    }
}

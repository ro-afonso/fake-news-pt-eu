package com.example.fakenewsapp

import retrofit2.Call
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST

interface ApiService {
    @POST("/predict")
    fun getPrediction(@Body request: PredictionRequest): Call<PredictionResponse>

    @POST("/feedback")
    fun sendFeedback(@Body request: FeedbackRequest): Call<FeedbackResponse>
}

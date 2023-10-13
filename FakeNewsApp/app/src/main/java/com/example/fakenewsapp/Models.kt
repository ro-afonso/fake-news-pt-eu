package com.example.fakenewsapp

data class PredictionRequest(val text: String, val language: String)

data class PredictionResponse(val prediction: Int, val success: Boolean)

data class FeedbackRequest(val text: String, val label: Int, val language: String)

data class FeedbackResponse(val message: String, val success: Boolean)
package com.example.fakenewsapp

import android.content.Intent
import android.graphics.Color
import android.os.Build
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.EditText
import android.widget.Toast
import androidx.annotation.RequiresApi
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.databinding.DataBindingUtil
import com.example.fakenewsapp.databinding.ActivityMainBinding
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import org.jsoup.Jsoup
import org.jsoup.nodes.Element
import java.io.IOException

class MainActivity : AppCompatActivity() {
    private var currentMode = "Prediction"
    private var languageModel = "english"
    private lateinit var binding: ActivityMainBinding
    private val apiService: ApiService by lazy {
        RetrofitClient.create()
    }

    @RequiresApi(Build.VERSION_CODES.M)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = DataBindingUtil.setContentView(this, R.layout.activity_main)

        binding.submitButton.setOnClickListener {
            if (binding.inputEditText.text.toString().isNotEmpty()){
                val inputText = binding.inputEditText.text.toString()
                binding.predictionTextView.text = ""
                predictFakeNews(inputText)
            }
            else{
                Toast.makeText(this, "Please add text!", Toast.LENGTH_SHORT).show()
                binding.predictionTextView.text = ""
            }
        }

        binding.realTestButton.setOnClickListener {
            val inputText = "UNBELIEVABLE! OBAMAS ATTORNEY GENERAL SAYS MOST CHARLOTTE RIOTERS WERE PEACEFUL PROTESTERS.In Her Home State Of North Carolina [VIDEO]    Now, most of the demonstrators gathered last night were exercising their constitutional and protected right to peaceful protest in order to raise issues and create change. Loretta Lynch aka Eric Holder in a skirt"
            binding.inputEditText.setText(inputText)
            predictFakeNews(inputText)
        }

        binding.fakeTestButton.setOnClickListener {
            val inputText = "Donald Trump just couldn t wish all Americans a Happy New Year and leave it at that. Instead, he had to give a shout out to his enemies, haters and  the very dishonest fake news media.  The former reality show star had just one job to do and he couldn t do it. As our Country rapidly grows stronger and smarter, I want to wish all of my friends, supporters, enemies, haters, and even the very dishonest Fake News Media, a Happy and Healthy New Year,  President Angry Pants tweeted.  2018 will be a great year for America! As our Country rapidly grows stronger and smarter, I want to wish all of my friends, supporters, enemies, haters, and even the very dishonest Fake News Media, a Happy and Healthy New Year. 2018 will be a great year for America!  Donald J. Trump (@realDonaldTrump) December 31, 2017Trump s tweet went down about as welll as you d expect.What kind of president sends a New Year s greeting like this despicable, petty, infantile gibberish? Only Trump! His lack of decency won t even allow him to rise above the gutter long enough to wish the American citizens a happy new year!  Bishop Talbert Swan (@TalbertSwan) December 31, 2017no one likes you  Calvin (@calvinstowell) December 31, 2017Your impeachment would make 2018 a great year for America, but I ll also accept regaining control of Congress.  Miranda Yaver (@mirandayaver) December 31, 2017Do you hear yourself talk? When you have to include that many people that hate you you have to wonder? Why do the they all hate me?  Alan Sandoval (@AlanSandoval13) December 31, 2017Who uses the word Haters in a New Years wish??  Marlene (@marlene399) December 31, 2017You can t just say happy new year?  Koren pollitt (@Korencarpenter) December 31, 2017Here s Trump s New Year s Eve tweet from 2016.Happy New Year to all, including to my many enemies and those who have fought me and lost so badly they just don t know what to do. Love!  Donald J. Trump (@realDonaldTrump) December 31, 2016This is nothing new for Trump. He s been doing this for years.Trump has directed messages to his  enemies  and  haters  for New Year s, Easter, Thanksgiving, and the anniversary of 9/11. pic.twitter.com/4FPAe2KypA  Daniel Dale (@ddale8) December 31, 2017Trump s holiday tweets are clearly not presidential.How long did he work at Hallmark before becoming President?  Steven Goodine (@SGoodine) December 31, 2017He s always been like this . . . the only difference is that in the last few years, his filter has been breaking down.  Roy Schulze (@thbthttt) December 31, 2017Who, apart from a teenager uses the term haters?  Wendy (@WendyWhistles) December 31, 2017he s a fucking 5 year old  Who Knows (@rainyday80) December 31, 2017So, to all the people who voted for this a hole thinking he would change once he got into power, you were wrong! 70-year-old men don t change and now he s a year older.Photo by Andrew Burton/Getty Images."
            binding.inputEditText.setText(inputText)
            predictFakeNews(inputText)
        }

        binding.fakeFeedbackButton.setOnClickListener {
            val inputText = "Ukrainian President Volodymyr Zelenskyy wore a Nazi symbol in public appearances in 2022."
            binding.inputEditText.setText(inputText)
            binding.labelEditText.setText("Fake")
            sendFeedback(inputText, 0)
        }

        binding.fakeFeedbackButton2.setOnClickListener {
            val inputText = "Martial arts movie star Chuck Norris has died from the COVID-19 coronavirus disease."
            binding.inputEditText.setText(inputText)
            binding.labelEditText.setText("Fake")
            sendFeedback(inputText, 0)
        }

        binding.realFeedbackButton.setOnClickListener {
            val inputText = "Former U.S. President Donald Trump said of how to help Ukraine during Russia's invasion, \"Well what I would do, is I would, we would, we have tremendous military capability and what we can do without planes, to be honest with you, without 44-year-old jets, what we can do is enormous, and we should be doing it and we should be helping them to survive and they're doing an amazing job.\""
            binding.inputEditText.setText(inputText)
            binding.labelEditText.setText("Real")
            sendFeedback(inputText, 1)
        }

        binding.realFeedbackButton2.setOnClickListener {
            val inputText = "Populations of wild deer across North America have tested positive for SARS-CoV-2 antibodies."
            binding.inputEditText.setText(inputText)
            binding.labelEditText.setText("Real")
            sendFeedback(inputText, 1)
        }

        binding.clearTextButton.setOnClickListener {
            binding.inputEditText.setText("")
            if (currentMode == "Prediction"){
                binding.predictionTextView.text = ""
            }
            else{
                binding.labelEditText.setText("")
            }
        }

        binding.feedbackButton.setOnClickListener {
            if (binding.labelEditText.text.toString().lowercase() == "real" || binding.labelEditText.text.toString().lowercase() == "fake"){
                if (binding.inputEditText.text.toString().isNotEmpty()){
                    var inputText = binding.inputEditText.text.toString()
                    var label = 2
                    //Log.e("BRUH","label: ${binding.labelEditText.text.toString().lowercase()}")
                    if (binding.labelEditText.text.toString().lowercase() == "real"){
                        label = 1
                    }
                    else if (binding.labelEditText.text.toString().lowercase() == "fake"){
                        label = 0
                    }
                    if (label == 2){
                        Toast.makeText(this, "Uh oh", Toast.LENGTH_SHORT).show()
                    }
                    else{
                        sendFeedback(inputText, label)
                    }
                }
                else{
                    Toast.makeText(this, "Please add text!", Toast.LENGTH_SHORT).show()
                }
            }
            else{
                Toast.makeText(this, "Please set the label to Real or Fake!", Toast.LENGTH_SHORT).show()
                binding.labelEditText.setText("")
            }
        }

        binding.changeModeButton.setOnClickListener {
            binding.inputEditText.setText("")
            binding.inputEditText.hint = "Please report only real life statements and avoid changing the original text..."
            if (currentMode == "Prediction"){
                binding.predictionTextView.text = ""
                //binding.fakeTestButton.visibility = View.GONE
                //binding.realTestButton.visibility = View.GONE
                binding.submitButton.visibility = View.GONE
                binding.predictionTextView.visibility = View.GONE
                binding.feedbackButton.visibility = View.VISIBLE
                binding.labelEditText.visibility = View.VISIBLE
                //binding.fakeFeedbackButton.visibility = View.VISIBLE
                //binding.fakeFeedbackButton2.visibility = View.VISIBLE
                //binding.realFeedbackButton.visibility = View.VISIBLE
                //binding.realFeedbackButton2.visibility = View.VISIBLE
                binding.ModeTextView.text = "Feedback\nMode"
                currentMode = "Feedback"
            }
            else{
                binding.labelEditText.setText("")
                binding.inputEditText.hint = "Insert the text here..."
                binding.feedbackButton.visibility = View.GONE
                binding.labelEditText.visibility = View.GONE
                //binding.fakeFeedbackButton.visibility = View.GONE
                //binding.fakeFeedbackButton2.visibility = View.GONE
                //binding.realFeedbackButton.visibility = View.GONE
                //binding.realFeedbackButton2.visibility = View.GONE
                //binding.fakeTestButton.visibility = View.VISIBLE
                //binding.realTestButton.visibility = View.VISIBLE
                binding.submitButton.visibility = View.VISIBLE
                binding.predictionTextView.visibility = View.VISIBLE
                binding.ModeTextView.text = "Prediction\nMode"
                currentMode = "Prediction"
            }
        }

        // Hide the buttons for the final version
        binding.fakeFeedbackButton.visibility = View.GONE
        binding.fakeFeedbackButton2.visibility = View.GONE
        binding.realFeedbackButton.visibility = View.GONE
        binding.realFeedbackButton2.visibility = View.GONE
        binding.fakeTestButton.visibility = View.GONE
        binding.realTestButton.visibility = View.GONE

        // Assuming you have references to your ImageButton in your binding object
        val changeLanguageModelButton = binding.changeLanguageModelButton

        // Create variables to store the drawable resources
        val portugalFlagDrawable = R.drawable.portugal_flag
        val usUkFlagDrawable = R.drawable.us_uk_flag

        // Set an initial drawable for the button's foreground
        changeLanguageModelButton.foreground = ContextCompat.getDrawable(this, usUkFlagDrawable)

        // Set a click listener for the button
        changeLanguageModelButton.setOnClickListener {
            if (languageModel == "english") {
                // Change the button's foreground to the Portugal flag drawable
                changeLanguageModelButton.foreground = ContextCompat.getDrawable(this, portugalFlagDrawable)
                languageModel = "portuguese"
            } else {
                // Change the button's foreground to the US/UK flag drawable
                changeLanguageModelButton.foreground = ContextCompat.getDrawable(this, usUkFlagDrawable)
                languageModel = "english"
            }
        }

        //Hide feedbackButton and labelEditText since the currentMode is set to Prediction at the start
        binding.feedbackButton.visibility = View.GONE
        binding.labelEditText.visibility = View.GONE
        binding.fakeFeedbackButton.visibility = View.GONE
        binding.fakeFeedbackButton2.visibility = View.GONE
        binding.realFeedbackButton.visibility = View.GONE
        binding.realFeedbackButton2.visibility = View.GONE
        binding.ModeTextView.text = "Prediction\nMode"

        // Check if the activity was launched from a share action. If so, autofill the inputField with the website's news' article data
        if (Intent.ACTION_SEND == intent.action && intent.type == "text/plain") {
            handleSharedUrl(intent)
        }
    }

    @RequiresApi(Build.VERSION_CODES.M)
    override fun onNewIntent(intent: Intent?) {
        super.onNewIntent(intent)
        if (intent != null && Intent.ACTION_SEND == intent.action && intent.type == "text/plain") {
            handleSharedUrl(intent)
        }
    }

    @RequiresApi(Build.VERSION_CODES.M)
    private fun handleSharedUrl(intent: Intent) {
        val sharedUrl = intent.getStringExtra(Intent.EXTRA_TEXT)
        //Toast.makeText(this, "url: $sharedUrl", Toast.LENGTH_SHORT).show()
        // Create a coroutine to scrape the data in the background to avoid NetworkOnMainThreadException error
        CoroutineScope(Dispatchers.IO).launch {
            var document = Jsoup.connect(sharedUrl).get()
            var paragraphsElements = document.getElementsByTag("p")
            var titleElements = document.getElementsByTag("h1")

            // Count occurrences of each paragraph text and store their parent elements
            val paragraphOccurrences = mutableMapOf<String, Int>()
            val paragraphParents = mutableMapOf<String, String>() // Storing tag and class
            val parentTagClassOccurrences =
                mutableMapOf<String, Int>() // Storing occurrences

            for (paragraphElement in paragraphsElements) {
                val paragraphText = paragraphElement.text().trim()
                if (!paragraphText.isEmpty()) {
                    paragraphOccurrences[paragraphText] =
                        (paragraphOccurrences[paragraphText] ?: 0) + 1;
                    if (paragraphOccurrences[paragraphText] == 1) {
                        val parentElement = paragraphElement.parent()
                        val parentTagClass =
                            "${parentElement?.tagName()} [class=${parentElement?.className()}]"
                        paragraphParents[paragraphText] = parentTagClass;

                        parentTagClassOccurrences[parentTagClass] =
                            (parentTagClassOccurrences[parentTagClass] ?: 0) + 1
                    }
                }
            }

            // Find the parent tag and class with the highest occurrences
            val mostCommonParentTagClass =
                parentTagClassOccurrences.maxByOrNull { it.value }?.key

            // Gather paragraphs with the most common parent tag and class, as this often represents the article itself
            val finalParagraphsText = paragraphParents
                .filter { it.value == mostCommonParentTagClass }
                .keys.joinToString("\n\n")

            // Print the tag and class of the first parent element of each paragraph
            for ((paragraphText, parentTagClass) in paragraphParents) {
                println("Paragraph: $paragraphText")
                println("Parent Tag and Class: $parentTagClass")
            }

            // Print the occurrences of each parent tag and class
            for ((parentTagClass, occurrences) in parentTagClassOccurrences) {
                println("Parent Tag and Class: $parentTagClass - Occurrences: $occurrences")
            }

            // Use withContext to stop the coroutine cycle and set the inputField with the news' data
            withContext(Dispatchers.Main) {
                binding.inputEditText.setText(titleElements.text() + "\n\n" + finalParagraphsText)
            }
        }
    }

    private fun predictFakeNews(text: String) {
        val request = PredictionRequest(text, languageModel)

        apiService.getPrediction(request).enqueue(object : Callback<PredictionResponse> {
            override fun onResponse(
                call: Call<PredictionResponse>,
                response: Response<PredictionResponse>
            ) {
                if (response.isSuccessful) {
                    val prediction = response.body()?.prediction
                    runOnUiThread {
                        if (prediction == 1) {
                            binding.predictionTextView.text = "The news is REAL!"
                            binding.predictionTextView.setTextColor(Color.GREEN)
                        }
                        else if (prediction == 0){
                            binding.predictionTextView.text = "The news is FAKE!"
                            binding.predictionTextView.setTextColor(Color.RED)
                        }
                        else{
                            binding.predictionTextView.text = "Prediction: ${prediction ?: "N/A"}"
                        }
                    }
                } else {
                    runOnUiThread {
                        binding.predictionTextView.text = "Prediction request failed"
                    }
                }
            }

            override fun onFailure(call: Call<PredictionResponse>, t: Throwable) {
                runOnUiThread {
                    binding.predictionTextView.text = "Prediction request failed"
                }
            }
        })
    }

    private fun sendFeedback(inputText: String, label: Int) {
        val feedbackData = FeedbackRequest(inputText, label, languageModel)

        apiService.sendFeedback(feedbackData).enqueue(object : Callback<FeedbackResponse> {
            override fun onResponse(
                call: Call<FeedbackResponse>,
                response: Response<FeedbackResponse>
            ) {
                if (response.isSuccessful) {
                    runOnUiThread {
                        val message = response.body()?.message ?: "Feedback sent successfully."
                        Toast.makeText(this@MainActivity, message, Toast.LENGTH_SHORT).show()
                    }
                } else {
                    runOnUiThread {
                        Toast.makeText(this@MainActivity, "Feedback request failed", Toast.LENGTH_SHORT).show()
                    }
                }
            }

            override fun onFailure(call: Call<FeedbackResponse>, t: Throwable) {
                runOnUiThread {
                    Toast.makeText(this@MainActivity, "Feedback request failed", Toast.LENGTH_SHORT).show()
                }
            }
        })
    }
}
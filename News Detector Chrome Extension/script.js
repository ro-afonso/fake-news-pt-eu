async function fetchData() {
  console.log("Button clicked");
  const inputText = document.getElementById("inputText").value.trim();

  if (inputText === "") {
    alert("Please enter some text.");
    return;
  }

  try{
    if (isFeedbackMode) {
      const inputLabel = document.getElementById("inputLabel").value.trim().toLowerCase();
      
      let labelFeedback;
      if (inputLabel === "real") {
        labelFeedback = 1;
      } else if (inputLabel === "fake") {
        labelFeedback = 0;
      } else {
        alert("Invalid label. Please enter 'real' or 'fake'.");
        return;
      }

      const data = { text: inputText, label: labelFeedback, language: languageModel };
      const options = {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      };
      const response = await fetch("CLOUD-IP/feedback", options); //Replace CLOUD-IP with your full domain (for example, https://01-23-456-789.nip.io)

      if (!response.ok) {
        throw new Error("Failed to fetch");
      }

      const result = await response.json();

      console.log("Result:", result);

      document.getElementById("tableData1").innerHTML = result.message;
    } else {
      // Send the predict POST request in Predict Mode
      const data = { text: inputText, language: languageModel };
      const options = {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      };

      const response = await fetch("CLOUD-IP/predict", options); //Replace CLOUD-IP with your full domain (for example, https://01-23-456-789.nip.io)

      if (!response.ok) {
        throw new Error("Failed to fetch");
      }

      const result = await response.json();

      console.log("Result:", result);

      const label = result.prediction ? "REAL" : "FAKE";
      document.getElementById("tableData1").innerHTML = inputText;
      document.getElementById("tableData2").innerHTML = label;
    }
  } catch (error) {
    alert("An error occurred while fetching data. Please try again later.");
    console.error("Fetch Error:", error);
  }

  return false;
}

let isFeedbackMode = false;

function switchMode() {
  const submitButton = document.getElementById("submitButton");
  const modeSwitchButton = document.getElementById("modeSwitch");
  const tableHeader1 = document.getElementById("tableHeader1");
  const tableHeader2 = document.getElementById("tableHeader2");
  const tableData1 = document.getElementById("tableData1");
  const tableData2 = document.getElementById("tableData2");
  const inputTextField = document.getElementById("inputText");
  const inputLabelDiv = document.getElementById("inputLabelDiv");
  const inputLabel = document.getElementById("inputLabel");

  // Reset input text when switching modes
  inputTextField.value = "";

  if (isFeedbackMode) {
    // Switch to Predict Mode UI
    submitButton.textContent = "Check News";
    modeSwitchButton.textContent = "Switch to Feedback Mode";
    tableHeader1.textContent = "Text";
    tableHeader2.textContent = "Label";
    tableData1.textContent = "";
    tableData2.textContent = "";
    inputLabelDiv.style.display = "none";
    inputLabel.value = "";
    
  } else {
    // Switch to Feedback Mode UI
    submitButton.textContent = "Send Feedback";
    modeSwitchButton.textContent = "Switch to Predict Mode";
    tableHeader1.textContent = "Feedback Status";
    tableHeader2.textContent = "";
    tableData1.textContent = "";
    tableData2.textContent = "";
    inputLabelDiv.style.display = "block";
  }

  isFeedbackMode = !isFeedbackMode;
}

let languageModel = "english";
const languageButton = document.getElementById("languageButton");
languageButton.style.width = '90px';
languageButton.style.height = '50px';

languageButton.style.backgroundImage = 'url("Images/us_uk_flag.jpg")';
languageButton.style.backgroundSize = 'cover';

languageButton.addEventListener("click", function() {
  if (languageModel === "english") {
    languageButton.style.backgroundImage = 'url("Images/portugal_flag_resized.png")';
    languageModel = "portuguese";
  }
  else {
    languageButton.style.backgroundImage = 'url("Images/us_uk_flag.jpg")';
    languageModel = "english";
  }
})

document.querySelector("form").addEventListener("submit", (e) => {
  console.log("Hello");
  fetchData();
  e.preventDefault();
});

document.getElementById("modeSwitch").addEventListener("click", (e) => {
  switchMode();
  e.preventDefault();
});

// Establish a connection with the background script
const port = chrome.runtime.connect({ name: 'popupConnection' });

document.getElementById("autofillButton").addEventListener("click", async (e) => {
  // Notify the background script that the popup is ready to receive data
  port.postMessage({ type: 'ready' });
  e.preventDefault();
});

port.onMessage.addListener(message => {
  if (message.type === 'domData') {
    const inputTextField = document.getElementById("inputText");

    // Extract title and paragraphs data from the received domData
    const { title, paragraphs } = message.data;

    // Process the received paragraphs data
    const processedData = processParagraphsData(paragraphs);

    // Create a list of <li> elements from the processed data
    const uniqueParagraphsListItems = createUniqueListItems(processedData);
    
    // Extract the first three unique parent tag and class combinations
    const firstThreeUniqueParents = uniqueParagraphsListItems.slice(0, 8);

    // Find the parent tag and class with the most occurrences
    const mostCommonParent = findMostCommonParent(uniqueParagraphsListItems);

    // Find the most common parent tag and class among the first three unique parents
    const mostCommonParentInFirstThree = findMostCommonParent(firstThreeUniqueParents);

    // Use the most common parent from the first three if it's one of the top three
    const finalMostCommonParent = firstThreeUniqueParents.includes(mostCommonParentInFirstThree)
      ? mostCommonParentInFirstThree
      : mostCommonParent;

    // Extract paragraphs' text with the final most common parent tag and class
    const paragraphsTextWithMostCommonParent = processedData
      .filter(paragraph => `${paragraph.tag},${paragraph.class}` === finalMostCommonParent)
      .map(paragraph => paragraph.text);

    // Clean the title and add it to the paragraphsTextWithMostCommonParent if it isn't null
    const cleanedTitle = title.replace(/<\/?[^>]+(>|$)/g, '').trim();
    if(cleanedTitle){
      inputTextField.value = cleanedTitle + "\n\n" + paragraphsTextWithMostCommonParent.join("\n\n");
    }
    else{
      inputTextField.value = paragraphsTextWithMostCommonParent.join("\n\n");
    }
  }
});

function processParagraphsData(paragraphsData) {
  // Create an array of processed paragraphs
  const processedParagraphs = [];

  // Iterate through the paragraphs data
  for (const paragraph of paragraphsData) {
    const cleanedParagraph = paragraph.text.replace(/<\/?[^>]+(>|$)/g, '').trim(); // Remove HTML tags and trim whitespace

    // Include the paragraph if it's not empty after cleaning
    if (cleanedParagraph) {
      processedParagraphs.push({
        text: cleanedParagraph,
        tag: paragraph.tag,
        class: paragraph.class
      });
    }
  }

  return processedParagraphs;
}

function createUniqueListItems(paragraphs) {
  // Count the occurrences of each uniqueKey
  const uniqueKeyOccurrences = {};
  const uniqueParagraphs = [];

  for (const paragraph of paragraphs) {
    const cleanedParagraph = paragraph.text.trim();
    const uniqueKey = `${paragraph.tag}-${paragraph.class}-${cleanedParagraph}`;

    if (cleanedParagraph) {
      uniqueKeyOccurrences[uniqueKey] = (uniqueKeyOccurrences[uniqueKey] || 0) + 1;
    }
  }

  for (const paragraph of paragraphs) {
    const cleanedParagraph = paragraph.text.trim();
    const uniqueKey = `${paragraph.tag}-${paragraph.class}-${cleanedParagraph}`;

    if (cleanedParagraph && uniqueKeyOccurrences[uniqueKey] === 1) {
      uniqueParagraphs.push(paragraph);
    }
  }

  return uniqueParagraphs.map(paragraph => {
    return `${paragraph.tag},${paragraph.class}`;
  });
}

// adapt this function to return a list with the top three most common parent tags and classes
function findMostCommonParent(paragraphsListItems) {
  const parentOccurrences = {};

  for (const parentKey of paragraphsListItems) {
    parentOccurrences[parentKey] = (parentOccurrences[parentKey] || 0) + 1;
  }

  let mostCommonParent = '';
  let maxOccurrences = 0;

  for (const parentKey in parentOccurrences) {
    if (parentOccurrences[parentKey] > maxOccurrences) {
      mostCommonParent = parentKey;
      maxOccurrences = parentOccurrences[parentKey];
    }
  }

  return mostCommonParent
}
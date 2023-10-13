let popupPort; // Connection port to the popup script

chrome.runtime.onConnect.addListener(port => {
  if (port.name === 'popupConnection') {
    popupPort = port;

    popupPort.onMessage.addListener(message => {
      if (message.type === 'ready') {
        // Send data to the popup script
        getDOMDataAndSend();
      }
    });

    popupPort.onDisconnect.addListener(() => {
      popupPort = null;
    });
  }
});

async function getDOMDataAndSend() {
  const [activeTab] = await chrome.tabs.query({ active: true, currentWindow: true });

  if (activeTab) {
    const tabId = activeTab.id;

    try {
      const domData = await getDOM(tabId);
      sendDOMData(domData);
    } catch (error) {
      console.error(JSON.stringify(error)); // Log the error details
    }
  }
}

async function getDOM(tabId) {
  return new Promise((resolve, reject) => {
    chrome.scripting.executeScript(
      {
        target: { tabId: tabId },
        function: getDOMFunction,
      },
      result => {
        if (!chrome.runtime.lastError && result[0].result) {
          resolve(result[0].result);
        } else {
          reject(chrome.runtime.lastError || "Script execution failed");
        }
      }
    );
  });
}

function getDOMFunction() {
  const paragraphs = Array.from(document.getElementsByTagName('p'), p => ({
    text: p.innerText,
    tag: p.parentNode.tagName,
    class: p.parentNode.className
  }));

  // Get the title if it exists
  title = document.title;
  //const titleElement = document.querySelector('h1');
  //const title = titleElement ? titleElement.innerText : '';

  return {
    title,
    paragraphs
  };
}

function sendDOMData(domData) {
  if (popupPort) {
    popupPort.postMessage({ type: 'domData', data: domData });
  }
}

let chatLog = document.getElementById("chat-log");
let loadingIndicator = document.getElementById("loading");
let inputContainer = document.getElementById("input-container");
let feedbackContainer = document.getElementById("feedback-container");
let collapseContainer = document.getElementById("sidebarToggleTop");

// Check if the page is being reloaded
if (performance.navigation.type === 1) {
  window.location.href = "/";
}

function showMessage(message, messageType) {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add(
    "message",
    messageType === "user" ? "user-message" : "bot-message"
  );

  const messageText = document.createElement("div");
  messageText.classList.add("message-text");

  messageText.innerHTML = message.replace(/\n/g, "<br>");

  messageDiv.appendChild(messageText);
  chatLog.appendChild(messageDiv);

  chatLog.scrollTop = chatLog.scrollHeight;
}
let loadingInt;

function showLoading() {
  const messages = [
    "Querying the database...",
    "Searching the database...",
    "Retrieving records...",
    "Fetching database entries...",
    "Scanning for results...",
    "Executing database query...",
    "Compiling search results...",
  ];

  loadingInt = setInterval(() => {
    const randomMessage = messages[Math.floor(Math.random() * messages.length)];
    document.getElementById("loading-msg").innerText = randomMessage;
  }, 3000);

  loadingIndicator.style.display = "flex";
}

let currHeight = chatLog.scrollHeight;

function hideLoading() {
  loadingIndicator.style.display = "none";
  chatLog.scrollTop = currHeight - 30;
  clearInterval(loadingInt);
}

function submitInitialResponse() {
  const selectedOption = document.getElementById("initial-dropdown").value;
  if (selectedOption) {
    showMessage(` ${selectedOption}`, "user");
    document.getElementById("initial-dropdown").disabled = true;
    document.querySelector("#input-container button").disabled = true;
    showLoading();
    chatLog.scrollTop = chatLog.scrollHeight;
    currHeight = chatLog.scrollHeight;
    setTimeout(() => {
      fetch("/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: `session_id=${session_id}&user_response=${encodeURIComponent(
          selectedOption
        )}`,
      })
        .then((response) => response.json())
        .then((data) => {
          let botResponse = data.bot_response || "API error";
          handleBotResponse(
            botResponse,
            selectedOption,
            data.feedback_required
          );
        })
        .catch((error) => {
          console.error(
            "Error fetching bot response, Reload The Page...",
            error
          );
          showMessage(" An error occurred, Reload The Page...", "bot");
        })
        .finally(() => {
          hideLoading();
        });
    }, 1500);
  } else {
    alert("Please select an option");
  }
}

function handleBotResponse(botResponse, selectedOption, feedbackRequired) {
  showMessage(` ${botResponse}`, "bot");
  if (feedbackRequired) {
    showFeedbackForm();
  } else {
    if (
      selectedOption === "Student" ||
      selectedOption === "Passout" ||
      selectedOption === "Working Professional"
    ) {
      if (selectedOption === "Student") {
        addDropdown(["Bachelor's Degree", "Master's Degree"]);
      } else if (selectedOption === "Passout") {
        addDropdown(["Yes", "No"]);
      } else {
        addTextInput();
      }
    } else {
      addTextInput();
    }
  }
}

function showFeedbackForm() {
  inputContainer.style.display = "none";
  feedbackContainer.style.display = "block";
}

function addDropdown(options) {
  const dropdown = document.createElement("select");
  dropdown.id = "dynamic-dropdown";
  dropdown.innerHTML = '<option value="">Select an option</option>';
  options.forEach((option) => {
    dropdown.innerHTML += `<option value="${option}">${option}</option>`;
  });
  inputContainer.innerHTML = "";
  inputContainer.appendChild(dropdown);

  const button = document.createElement("button");
  button.innerText = "Submit";
  button.onclick = submitDropdownResponse;
  inputContainer.appendChild(button);
}

function submitDropdownResponse() {
  const selectedOption = document.getElementById("dynamic-dropdown").value;
  if (selectedOption) {
    showMessage(`${selectedOption}`, "user");
    document.getElementById("dynamic-dropdown").disabled = true;
    document.querySelector("#input-container button").disabled = true;
    showLoading();
    chatLog.scrollTop = chatLog.scrollHeight;
    currHeight = chatLog.scrollHeight;
    setTimeout(() => {
      fetch("/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: `session_id=${session_id}&user_response=${encodeURIComponent(
          selectedOption
        )}`,
      })
        .then((response) => response.json())
        .then((data) => {
          let botResponse = data.bot_response || "API error";
          showMessage(`${botResponse}`, "bot");
          if (data.feedback_required) {
            showFeedbackForm();
          } else {
            addTextInput();
          }
        })
        .catch((error) => {
          console.error(
            "Error fetching bot response, Reload The Page...",
            error
          );
          showMessage("An error occurred, Reload The Page...", "bot");
        })
        .finally(() => {
          hideLoading();
        });
    }, 1500);
  } else {
    alert("Please select an option");
  }
}

function addTextInput() {
  inputContainer.innerHTML = `
              <textarea id="user-input" placeholder="Type your response..." rows="1"></textarea>
              <button onclick="submitResponse()">Submit</button>
          `;

  const userInput = document.getElementById("user-input");
  userInput.addEventListener("input", autoResizeTextarea);

  function autoResizeTextarea() {
    userInput.style.height = "auto";
    userInput.style.height = `${userInput.scrollHeight}px`;
  }
}

function submitFeedback() {
  const rating = document.getElementById("rating").value;
  const feedback = document.getElementById("feedback").value;

  fetch("/feedback", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      session_id: session_id,
      rating: rating,
      feedback: feedback,
    }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      showMessage("Thank you for your feedback!", "bot");
      feedbackContainer.style.display = "none";
      inputContainer.style.display = "block";
      addTextInput();
    })
    .catch((error) => {
      console.error("Error submitting feedback:", error);
      showMessage("Error submitting feedback. Please try again.", "bot");
    });
}

function submitResponse() {
  let userInput = document.getElementById("user-input").value;
  showMessage(`You: ${userInput}`, "user");
  showLoading();
  chatLog.scrollTop = chatLog.scrollHeight;
  currHeight = chatLog.scrollHeight;
  setTimeout(() => {
    fetch("/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: `session_id=${session_id}&user_response=${encodeURIComponent(
        userInput
      )}`,
    })
      .then((response) => response.json())
      .then((data) => {
        let botResponse = data.bot_response || "API error";
        showMessage(`${botResponse}`, "bot");
        if (data.feedback_required) {
          showFeedbackForm();
        }
      })
      .catch((error) => {
        console.error("Error fetching bot response, Reload The Page...", error);
        showMessage("An error occurred, Reload The Page...", "bot");
      })
      .finally(() => {
        hideLoading();
      });

    document.getElementById("user-input").value = "";
    document.getElementById("user-input").style.height = "auto";
  }, 1500);
}

collapseContainer.addEventListener("click", function () {
  var sidebar = document.getElementById("nav");
  var content = document.getElementById("content");
  const w = window.innerWidth;
  const h = window.innerHeight;

  if (w <= 860) {
    console.log("her,");
    sidebar.classList.toggle("hide");
    console.log(content.classList);
    content.classList.toggle("content-expanded");
  } else {
    sidebar.classList.toggle("nav-collapsed");
    content.classList.toggle("content-expanded");
  }
});
document.addEventListener("DOMContentLoaded", () => {
  // Function to add click event to .bot-message elements
  const addClickEvent = (message) => {
    message.addEventListener("click", (e) => {
      console.log("clicked");
      if (
        e.target === message ||
        e.target === message.querySelector("::after")
      ) {
        console.log("cpy");
        const textToCopy = message.innerText;

        navigator.clipboard
          .writeText(textToCopy)
          .then(() => {
            // Optional: Provide visual feedback
            const originalEmoji = getComputedStyle(message, "::after").content;
            message.style.setProperty(
              "--copy-icon",
              ' url("https://img.icons8.com/?size=100&id=43513&format=png&color=737373")'
            );

            setTimeout(() => {
              message.style.setProperty("--copy-icon", originalEmoji);
            }, 2000);
          })
          .catch((err) => {
            console.error("Failed to copy text: ", err);
          });
      }
    });
  };

  // Initially add click event to existing .bot-message elements
  const botMessages = document.querySelectorAll(".bot-message");
  botMessages.forEach(addClickEvent);

  // Create a mutation observer to watch for new .bot-message elements
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType === 1 && node.classList.contains("bot-message")) {
          addClickEvent(node);
        }
      });
    });
  });

  // Configure the observer to watch for child list changes
  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });
});

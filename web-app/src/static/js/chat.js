var fileClicked = false;
var audioClicked = false;

const url = "152.42.235.175:5000"

let mediaRecorder;
let audioChunks = [];
let audioBlob;
let isRecording = false;

document
  .getElementById("uploadForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();
  });

// Create preview for audio recordings
function createAudioPreview(blob) {
  const previewContainer = document.getElementById("imagePreviewContainer");
  const audioURL = URL.createObjectURL(blob);

  previewContainer.innerHTML = `
    <div class="audio-preview">
      <audio controls src="${audioURL}"></audio>
      <div class="audio-status">Recording complete! Press send to submit.</div>
    </div>
  `;
}

// Initialize the recorder when the page loads
async function initRecorder() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
      audioBlob = new Blob(audioChunks, { type: "audio/wav" });
      audioChunks = [];
      // Create audio preview when recording stops
      createAudioPreview(audioBlob);
    };
  } catch (error) {
    console.error("Error initializing recorder:", error);
    alert(
      "Unable to access microphone. Please ensure microphone permissions are granted."
    );
  }
}

// Call initRecorder when the page loads
document.addEventListener("DOMContentLoaded", initRecorder);

document.getElementById("uploadIcon").addEventListener("click", function () {
  document.getElementById("fileInput").click();
  fileClicked = true;
  audioClicked = false; // Reset audio clicked state
});

document
  .getElementById("recordButton")
  .addEventListener("click", async function () {
    audioClicked = true;
    fileClicked = false; // Reset file clicked state

    if (!mediaRecorder) {
      await initRecorder();
    }

    if (mediaRecorder) {
      if (isRecording) {
        mediaRecorder.stop();
        this.textContent = "🎤";
        this.style.backgroundColor = "";
      } else {
        // Clear any existing preview
        document.getElementById("imagePreviewContainer").innerHTML = "";
        mediaRecorder.start();
        audioChunks = [];
        this.textContent = "⏹️";
        this.style.backgroundColor = "#ff4444";
      }
      isRecording = !isRecording;
    }
  });

document.getElementById("fileInput").addEventListener("change", function (e) {
  const file = e.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = function () {
      const previewContainer = document.getElementById("imagePreviewContainer");
      previewContainer.innerHTML = `<img src="${reader.result}" alt="Preview" class="image-preview" width="20%"/>`;
    };
  }
});

const createBotInput = (msg) => {
  let chatParent = document.querySelector(".chat-area-main");
  let div = document.createElement("div");
  div.className = "chat-msg-content";
  div.innerHTML = `
    <div class="chat-msg-profile">
      <img class="chat-msg-img" src="../static/images/bot.png" alt="" />
    </div>
    <div class="chat-msg-content">
      <div class="chat-msg-text">${msg}</div>
    </div>
  `;
  chatParent.append(div);
  scrollToBottom();
};

const createUserInput = (userMsg, userImg = null) => {
  let chatParent = document.querySelector(".chat-area-main");
  let div = document.createElement("div");
  div.className = "chat-msg owner";
  div.innerHTML = userImg
    ? `<div class="chat-msg-profile">
         <img class="chat-msg-img" src="../static/images/bmo.jpeg" alt="" />
       </div>
       <div class="chat-msg-content">
         <div class="chat-msg-text">
           <img src="${userImg}" alt="user image" />
         </div>
       </div>`
    : `<div class="chat-msg-profile">
         <img class="chat-msg-img" src="../static/images/bmo.jpeg" alt="" />
       </div>
       <div class="chat-msg-content">
         <div class="chat-msg-text">${userMsg}</div>
       </div>`;
  chatParent.append(div);
  scrollToBottom();
};

document.querySelector("#submitBtn").addEventListener("click", function () {
  const userInput = document.querySelector("#userInput").value ?? "";

  if (fileClicked) {
    const fileInput = document.querySelector("#fileInput");
    const file = fileInput.files[0];
    if (!file) {
      alert("No file selected");
      return;
    }

    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = function () {
      createUserInput(userInput, reader.result);

      const formData = new FormData();
      formData.append("file", file);

      const xhr = new XMLHttpRequest();
      xhr.open("POST", `http://${url}/chat/upload`, true);
      xhr.onload = function () {
        if (xhr.status === 200) {
          fetch(
            `http://${url}/chat/web_message?img=true&message=${userInput}`
          )
            .then((response) => response.json())
            .then((data) => {
              const res = data["message"];
              createBotInput(res);
            })
            .catch((error) => console.error("Error:", error));
        }
      };
      xhr.send(formData);
    };
  } else if (audioClicked && audioBlob) {
    // Create a custom preview of the audio message in the chat
    createUserInput(userInput || "🎤 Audio Message");

    const formData = new FormData();
    formData.append("audio", audioBlob, "recording.wav");

    const xhr = new XMLHttpRequest();
    xhr.open("POST", `http://${url}/chat/upload-audio`, true);
    xhr.onload = function () {
      if (xhr.status === 200) {
        fetch(`http://${url}/chat/web_message?audio=true&message=${userInput}`)
          .then((response) => response.json())
          .then((data) => {
            const res = data["message"];
            console.log('send?')
            createBotInput(res);
          })
          .catch((error) => console.error("Error uploading audio:", error));
      }
    }
      xhr.send(formData);
  } else {
    createUserInput(userInput);

    fetch(`http://${url}/chat/web_message?message=${userInput}`)
      .then((response) => {
        if (!response.ok) throw new Error("Network response was not ok");
        return response.json();
      })
      .then((data) => {
        const res = data["message"];
        createBotInput(res);
      })
      .catch((error) => console.error("Error:", error));
  }

  // Reset all states and clear preview
  document.getElementById("imagePreviewContainer").innerHTML = "";
  document.querySelector("#userInput").value = "";
  fileClicked = false;
  audioClicked = false;

  // Reset record button if it was recording
  if (isRecording) {
    mediaRecorder.stop();
    isRecording = false;
    const recordButton = document.getElementById("recordButton");
    recordButton.textContent = "🎤";
    recordButton.style.backgroundColor = "";
  }

  // Scroll to bottom
  scrollToBottom();
});

// Function to scroll to the bottom of the chat container
const scrollToBottom = () => {
  const chatParent = document.querySelector(".chat-area-main");

  chatParent.scrollIntoView(false);
};

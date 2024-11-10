var fileClicked = false;

document.getElementById("uploadIcon").addEventListener("click", function () {
  document.getElementById("fileInput").click();
  fileClicked = true;
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


document
  .getElementById("uploadForm")
  .addEventListener("submit", function (event) {
    console.log("submitted?");
    event.preventDefault();
  });

const createBotInput = (msg) => {
  let chatParent = document.querySelector(".chat-area-main");
  let div = document.createElement("div");

  div.className = "chat-msg-content";

  div.innerHTML = `
          <div class="chat-msg-profile">
            <img
              class="chat-msg-img"
              src="../static/images/bot.png"
              alt=""
            />

          </div>
           <div class="chat-msg-content">
            <div class="chat-msg-text">
              ${msg}
            </div>
          </div>

        `;

  chatParent.append(div);
};

const createUserInput = (userMsg, userImg = null) => {
  let chatParent = document.querySelector(".chat-area-main");
  let div = document.createElement("div");

  div.className = "chat-msg owner";

  if (userImg != null) {
    div.innerHTML = ` <div class="chat-msg-profile">
            <img
              class="chat-msg-img"
              src="../static/images/bmo.jpeg"
              alt=""
            />

          </div>
           <div class="chat-msg-content">
            <div class="chat-msg-text">
              <img src="${userImg}" alt="user image" />
            </div>
          </div>`;
  } else {
    div.innerHTML = `
          <div class="chat-msg-profile">
            <img
              class="chat-msg-img"
              src="../static/images/bmo.jpeg"
              alt=""
            />

          </div>
           <div class="chat-msg-content">
            <div class="chat-msg-text">
              ${userMsg}
            </div>
          </div>

        `;
  }

  chatParent.append(div);
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
    reader.readAsDataURL(file); // Read the file as a data URL (Base64 encoding)

    reader.onload = function () {
      // After the file is read, call createUserInput with the user input and the file content
      createUserInput(userInput, reader.result); // Pass the base64 encoded file (reader.result)

      // Now, upload the file to the backend
      const formData = new FormData();
      formData.append("file", file); // Append the file to FormData

      const xhr = new XMLHttpRequest();
      xhr.open("POST", "/chat/upload", true);

      xhr.onload = function () {
        if (xhr.status === 200) {
          console.log("File uploaded successfully");
          // Trigger the fetch after successful upload
          fetch("http://localhost:5000/chat/web_message?img=true&message=" + userInput)
            .then((response) => response.json())
            .then((data) => {
              console.log("Analysis result:", data);
              const res = data["message"];
              createBotInput(res);
            })
            .catch((error) => console.error("Error:", error));
        }
      };

      // Send the form data to the backend
      xhr.send(formData);
    };
  } else {
    // If no file is clicked, just send the text input
    createUserInput(userInput);

    fetch("http://localhost:5000/chat/web_message?message=" + userInput)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then((data) => {
        console.log("Analysis result:", data);
        const res = data["message"];
        createBotInput(res);
      })
      .catch((error) => {
        console.error("There was a problem with the fetch operation:", error);
      });
  }

  document.getElementById("imagePreviewContainer").innerHTML = "";
  document.querySelector("#userInput").value = "";
});

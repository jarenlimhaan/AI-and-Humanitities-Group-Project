var fileClicked = false;

document.getElementById("uploadIcon").addEventListener("click", function () {
  document.getElementById("fileInput").click();
  fileClicked = true;
});

document
  .getElementById("uploadForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();
  });

const createBotInput = (msg) => {
  let chatParent = document.querySelector(".chat-area-main");
  let div = document.createElement("div");

  div.className = "chat-msg-content"

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

const createUserInput = (userMsg, userImg=null) => {
  let chatParent = document.querySelector(".chat-area-main");
  let div = document.createElement("div");

  div.className = "chat-msg-owner"

  if(userImg != null) {
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
          </div>`

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
}

document.querySelector("#submitBtn").addEventListener("click", function () {

  const userInput = document.querySelector("#userInput").value ?? '';

  if(fileClicked) {
    const file = document.querySelector("#fileInput").files[0];
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = function () {
      createUserInput(userInput, reader.result);
    };
  }

  createUserInput(userInput);

  if (fileClicked) {
    fetch("http://localhost:5000/chat/analyze")
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
  } else {
    createBotInput("response from vertex ai");
  }
});

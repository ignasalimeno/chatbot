class Chatbox {
  constructor() {
    this.args = {
      openButton: document.querySelector(".chatbox__button"),
      chatBox: document.querySelector(".chatbox__support"),
      sendButton: document.querySelector(".send__button"),
    };

    this.state = false;
    this.messages = [];
  }

  display() {
    const { openButton, chatBox, sendButton } = this.args;

    openButton.addEventListener("click", () => this.toggleState(chatBox));

    sendButton.addEventListener("click", () => this.onSendButton(chatBox));

    const node = chatBox.querySelector("input");
    node.addEventListener("keyup", ({ key }) => {
      if (key === "Enter") {
        this.onSendButton(chatBox);
      }
    });
  }

  toggleState(chatbox) {
    this.state = !this.state;

    // show or hides the box
    if (this.state) {
      chatbox.classList.add("chatbox--active");
    } else {
      chatbox.classList.remove("chatbox--active");
    }
  }

  onSendButton_old(chatbox) {
    var textField = chatbox.querySelector("input");
    let text1 = textField.value;
    if (text1 === "") {
      return;
    }
    const token = sessionStorage.getItem("token");

    let msg1 = { name: "User", message: text1 };
    this.messages.push(msg1);

    if (!token) {
      fetch("http://127.0.0.1:5000/generate_token", {
        method: "POST",
        mode: "cors",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Error al generar el token");
          }
          return response.json();
        })
        .then((data) => {
          sessionStorage.setItem("token", data.token);

          fetch("http://127.0.0.1:5000/response", {
            method: "POST",
            body: JSON.stringify({ message: text1 }),
            mode: "cors",
            headers: {
              Authorization: "Bearer " + sessionStorage.getItem("token"),
              "Content-Type": "application/json",
            },
          })
            .then((r) => r.json())
            .then((r) => {
              if (data.token) {
                sessionStorage.setItem("token", data.token);
              }

              let msg2 = { name: "Sam", message: r.answer };
              this.messages.push(msg2);
              this.updateChatText(chatbox);
              textField.value = "";
            })
            .catch((error) => {
              console.error("Error:", error);
              this.updateChatText(chatbox);
              textField.value = "";
            });
        })
        .catch((error) => {
          console.error("Error:", error.message);
          alert("Error al obtener el token");
        });
    } else {
      fetch("http://127.0.0.1:5000/response", {
        method: "POST",
        body: JSON.stringify({ message: text1 }),
        mode: "cors",
        headers: {
          Authorization: "Bearer " + sessionStorage.getItem("token"),
          "Content-Type": "application/json",
        },
      })
        .then((r) => r.json())
        .then((r) => {
          if (r.token) {
            sessionStorage.setItem("token", data.token);
          }

          let msg2 = { name: "Sam", message: r.answer };
          this.messages.push(msg2);
          this.updateChatText(chatbox);
          textField.value = "";
        })
        .catch((error) => {
          console.error("Error:", error);
          this.updateChatText(chatbox);
          textField.value = "";
        });
    }
  }

  onSendButton(chatbox) {
    var textField = chatbox.querySelector("input");
    let text1 = textField.value;
    if (text1 === "") {
      return;
    }

    const token = sessionStorage.getItem("token");

    let msg1 = { name: "User", message: text1 };
    this.messages.push(msg1);

    fetch("http://127.0.0.1:5000/response", {
      method: "POST",
      body: JSON.stringify({ message: text1 }),
      mode: "cors",
      headers: {
        Authorization: "Bearer " + sessionStorage.getItem("token"),
        "Content-Type": "application/json",
      },
    })
      .then((r) => r.json())
      .then((r) => {
        if (r.hasOwnProperty('token')) {
          sessionStorage.setItem("token", r.token);
        }
        let msg2 = { name: "Sam", message: r.answer };
        this.messages.push(msg2);
        this.updateChatText(chatbox);
        textField.value = "";
      })
      .catch((error) => {
        console.error("Error:", error);
        this.updateChatText(chatbox);
        textField.value = "";
      });
  }

  updateChatText(chatbox) {
    var html = "";
    this.messages
      .slice()
      .reverse()
      .forEach(function (item, index) {
        if (item.name === "Sam") {
          html +=
            '<div class="messages__item messages__item--visitor">' +
            item.message +
            "</div>";
        } else {
          html +=
            '<div class="messages__item messages__item--operator">' +
            item.message +
            "</div>";
        }
      });

    const chatmessage = chatbox.querySelector(".chatbox__messages");
    chatmessage.innerHTML = html;
  }

  generateToken() {
    fetch("http://127.0.0.1:5000/generate_token", {
      method: "POST",
      mode: "cors",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}),
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Error al generar el token");
        }
        return response.json();
      })
      .then((data) => {
        localStorage.setItem("token", data.token);
        alert("Token obtenido y guardado: " + data.token);
      })
      .catch((error) => {
        console.error("Error:", error.message);
        alert("Error al obtener el token");
      });
  }
}

const chatbox = new Chatbox();
chatbox.display();

var speech = true;

function clearData() {
  localStorage.removeItem("db_name");
  location.href = "/";
}

document.addEventListener("DOMContentLoaded", async () => {
  const fileInput = document.getElementById("fileInput");
  const queryForm = document.getElementById("queryForm");
  const chatContainer = document.getElementById("chatContainer");
  const exportButton = document.getElementById("exportButton");
  const sppechButton = document.getElementById("speechButton");
  const previewFrame = document.getElementById("filePreview");
  const summaryButton = document.getElementById("summaryButton");

  sppechButton.addEventListener("click", () => {
    window.speechSynthesis.cancel();
  });

  let dbName = localStorage.getItem("db_name") || "";
  let history = [];

  function navToPage(pageNumber) {
    pageNumber = pageNumber.replace("p.", "");

    if (!dbName) return;
    try {
      previewFrame.src = `/preview/${dbName}#page=${pageNumber}`;
    } catch (e) {
      previewFrame.src = `/preview/${dbName}#page=1`;
    }
  }

  window.navToPage = navToPage;

  async function loadChatHistory() {
    try {
      const response = await fetch(`/get_history/${dbName}`);

      if (response.ok) {
        const result = await response.json();
        history = result.history;

        history.forEach(([query, response]) => {
          appendMessage(query, "user");
          appendFormattedMessage(response, (sources = []), "bot");
        });

        navToPage("p.1");
      } else {
        console.log("No history found or error fetching history.");
      }
    } catch (error) {
      console.error("Failed to load chat history:", error);
    }
  }

  async function verifyDb() {
    if (!dbName) return;

    try {
      const response = await fetch(`/check_db/${dbName}`);
      if (response.ok) {
        loadChatHistory();
      } else {
        console.log("DB not found, clearing cache.");
        localStorage.removeItem("db_name");
        dbName = "";
      }
    } catch (error) {
      console.error("Failed to verify DB:", error);
      localStorage.removeItem("db_name");
      dbName = "";
    }
  }

  if (dbName) {
    verifyDb();
  }

  // FIle Upload
  fileInput.addEventListener("change", async () => {
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const response = await fetch("/ingest", {
      method: "POST",
      body: formData,
    });

    const result = await response.json();

    if (response.ok) {
      dbName = result.db_name;
      localStorage.setItem("db_name", dbName);

      navToPage("p.1");
      appendMessage(`📄 File uploaded successfully`, "bot");
    } else {
      appendMessage(`❌ Error: ${result.error}`, "bot");
    }
  });

  exportButton.addEventListener("click", async () => {
    if (!dbName) return;

    const url = `/export_chat/${dbName}`;
    const link = document.createElement("a");
    link.href = url;
    link.download = `chat_history_${dbName}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  });

  // RAG Queries
  queryForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const queryInput = document.getElementById("queryInput").value;

    appendMessage(queryInput, "user");

    const response = await fetch("/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: queryInput, db_name: dbName }),
    });

    const result = await response.json();

    if (response.ok) {
      appendFormattedMessage(result.response, result.sources, "bot");

      if (result.sources.length > 0) {
        navToPage(result.sources[0]);
      }

      history.push({
        query: queryInput,
        response: result.response,
        sources: result.sources,
      });
    } else {
      appendMessage(`❌ Error: ${result.error}`, "bot");
    }
  });

  // Response
  function appendFormattedMessage(message, sources, type) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add(
      "chat-message",
      type === "user" ? "user-message" : "bot-message"
    );

    const contentDiv = document.createElement("div");
    contentDiv.classList.add("message-content");

    contentDiv.innerHTML = message.replace("\n", "<br>");

    const speakButton = document.createElement("button");
    speakButton.innerText = "🔊";
    speakButton.classList.add("speak-button");
    speakButton.style.marginLeft = "8px";
    speakButton.onclick = () => speakText(message);

    contentDiv.appendChild(speakButton);

    if (sources.length > 0) {
      const sourceDiv = document.createElement("div");
      sourceDiv.classList.add("source-info");
      sourceDiv.innerHTML = `<small>Sources: </small>`;

      sources.forEach((source) => {
        sourceDiv.innerHTML += `<small class="source" onclick="navToPage('${source}')"> ${source}</small>`;
      });

      contentDiv.appendChild(sourceDiv);
    }

    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }

  // Message
  function appendMessage(message, type) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add(
      "chat-message",
      type === "user" ? "user-message" : "bot-message"
    );

    const contentDiv = document.createElement("div");
    contentDiv.innerHTML = `<p>${message}</p>`;

    const speakButton = document.createElement("button");
    speakButton.innerText = "🔊";
    speakButton.classList.add("speak-button");
    speakButton.style.marginLeft = "8px";
    speakButton.onclick = () => speakText(message);

    contentDiv.appendChild(speakButton);

    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }

  function speakText(text) {
    if (!speech) return;
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.cancel(); // cancel previous speech
    window.speechSynthesis.speak(utterance);
  }

  summaryButton.addEventListener("click", async () => {
    if (!dbName || dbName === "0") {
      appendMessage("❌ No file selected to summarize.", "bot");
      return;
    }

    try {
      const url = `/summarize/${dbName}`;
      const link = document.createElement("a");
      link.href = url;
      link.download = `summary_${dbName}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      summaryButton.disabled = true;
      summaryButton.innerText = "⏳ Summarizing...";
      setTimeout(() => {
        summaryButton.disabled = false;
        summaryButton.innerText = "Summarize";
      }, 15000);
    } catch (err) {
      appendMessage(`❌ Error while fetching summary: ${err}`, "bot");
    }
  });
});

document.addEventListener('DOMContentLoaded', () => {

    const fileInput = document.getElementById('fileInput');
    const queryForm = document.getElementById('queryForm');
    const chatContainer = document.getElementById('chatContainer');
    let dbName = "";
    let history = [];

    // Handle File Upload
    fileInput.addEventListener('change', async () => {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        const response = await fetch('/ingest', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            dbName = result.db_name;
            document.getElementById('filePreview').src = `/preview/${dbName}`;

            appendMessage(`📄 File uploaded successfully: ${dbName}`, 'bot');
        } else {
            appendMessage(`❌ Error: ${result.error}`, 'bot');
        }
    });

    // Handle RAG Queries
    queryForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const queryInput = document.getElementById('queryInput').value;

        appendMessage(queryInput, 'user');

        const response = await fetch('/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: queryInput, db_name: dbName })
        });

        const result = await response.json();

        if (response.ok) {
            appendFormattedMessage(result.response, result.sources, 'bot');
            history.push({ query: queryInput, response: result.response, sources: result.sources });
        } else {
            appendMessage(`❌ Error: ${result.error}`, 'bot');
        }
    });

    // Append Chat Message with Sources
    function appendFormattedMessage(message, sources, type) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chat-message', type === 'user' ? 'user-message' : 'bot-message');

        // Display message content
        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        contentDiv.innerHTML = `<p>${message}</p>`;

        // Display source page numbers
        if (sources.length > 0) {
            const sourceDiv = document.createElement('div');
            sourceDiv.classList.add('source-info');
            sourceDiv.innerHTML = `<small>Sources: ${sources.join(', ')}</small>`;
            contentDiv.appendChild(sourceDiv);
        }

        messageDiv.appendChild(contentDiv);
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Append Basic Chat Message
    function appendMessage(message, type) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chat-message', type === 'user' ? 'user-message' : 'bot-message');
        messageDiv.innerHTML = `<p>${message}</p>`;
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
});

# 📄 **Docxpert: Document Query bot with RAG**

**Docxpert** is an AI-powered document query chatbot that leverages **Retrieval-Augmented Generation (RAG)** to provide precise and context-aware responses from PDF, Word, and Text documents. It uses **OpenAI's API** for language processing, **ChromaDB** for efficient vector storage and retrieval, and a **Flask server** to deliver a clean and interactive UI.

---
## 🚀 **Deployed at HuggingFace Space**
- You can run the application [here](https://huggingface.co/spaces/Rahul-Samedavar/Docxpert)




![](Images/Home.png)
![](Images/demo.png)

## 🚀 **Features**

✅ **Multi-File Support:**  
- Supports **PDF**, **Word (.docx)**, and **Text (.txt)** file formats for querying.  

✅ **Context-Aware Queries:**  
- Each new query continues from the previous context, maintaining the conversation flow.  

✅ **File Preview with Navigation:**  
- Document preview with **full view tools** for easier access.  
- Auto-scroll to RAG references: Clicking on a source in the response navigates directly to the corresponding page.  

✅ **Temporary Sessions:**  
- Sessions persist as long as the server is running, allowing users to **reload the page** and continue where they left off.  

✅ **Exportable Chat History:**  
- Save the entire conversation as a **PDF file** for reference.  

✅ **Multi-PDF Interaction:**  
- Interact with **multiple PDFs** without clearing previous chat history, making cross-document queries seamless.  

✅ **Chat Clearing Option:**  
- Users can **clear the chat** and reset the context when required.  

---

## ⚙️ **Tech Stack**

- **LLM:** OpenAI GPT  
- **LLM Framework:** Langchain  
- **Backend:** Flask (Python)  
- **Vector Store:** ChromaDB  
- **UI:** HTML, CSS, JavaScript  
- **File Processing:** PyMuPDF, pdf-kit, python-docx , docx2txt 

---

## 🛠️ **Installation & Setup**

### 1️⃣ **Clone the Repository**
```bash
git clone https://github.com/Rahul-Samedavar/Docxpert.git
cd Docxpert
```

### 2️⃣ **Create Virtual Environment**
```bash
python -m venv env
source env/bin/activate  # Linux
env\Scripts\activate     # Windows
```

### 3️⃣ **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4️⃣ **Run the Server**
```bash
python app.py
```
Open your browser and visit:  
```
http://127.0.0.1:5000
```

---

## 🔥 **Usage Guide**

1. **Upload Document:** Click the 📎 icon to upload PDF, DOCX, or TXT files.  
2. **Ask Queries:** Type your questions in the chat input.  
3. **Auto-Navigation:** Click the source reference to auto-scroll to the relevant page in the preview.  
4. **Export History:** Click the **Export to PDF** button to save the chat history.  
5. **Clear Chat:** Use the **Clear Chat** button to reset the context.  

---

## 📜 **License**
This project is licensed under the [**MIT License**](LICENSE).  

---

✅ **Docxpert** – Your AI-Powered Document Assistant! 🚀
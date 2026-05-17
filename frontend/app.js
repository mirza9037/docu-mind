document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const fileInput = document.getElementById('fileInput');
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadStatus = document.getElementById('uploadStatus');
    const documentList = document.getElementById('documentList');
    const refreshBtn = document.getElementById('refreshBtn');
    
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatHistory = document.getElementById('chatHistory');
    const welcomeState = document.getElementById('welcomeState');
    const activeDocBadge = document.getElementById('activeDocBadge');
    const activeDocName = document.getElementById('activeDocName');

    // State
    let currentDocumentId = null;

    // --- File Upload Logic ---
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileNameDisplay.textContent = e.target.files[0].name;
            uploadBtn.disabled = false;
        } else {
            fileNameDisplay.textContent = 'No file chosen';
            uploadBtn.disabled = true;
        }
    });

    uploadBtn.addEventListener('click', async () => {
        const file = fileInput.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Ingesting...';
        showStatus('Uploading and embedding...', 'info');

        try {
            const res = await fetch('/documents/upload', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();

            if (res.ok) {
                showStatus('Success! Document ingested.', 'success');
                fileInput.value = '';
                fileNameDisplay.textContent = '';
                loadDocuments(); // Refresh list
            } else {
                showStatus(data.detail || 'Upload failed', 'error');
            }
        } catch (err) {
            showStatus('Network error during upload', 'error');
        } finally {
            uploadBtn.disabled = false;
            uploadBtn.innerHTML = '<i class="fa-solid fa-bolt"></i> Ingest Document';
        }
    });

    function showStatus(msg, type) {
        uploadStatus.textContent = msg;
        uploadStatus.className = `status-msg ${type}`;
        uploadStatus.classList.remove('hidden');
        setTimeout(() => uploadStatus.classList.add('hidden'), 5000);
    }

    // --- Document List Logic ---
    async function loadDocuments() {
        documentList.innerHTML = '<div class="loading-docs"><i class="fa-solid fa-circle-notch fa-spin"></i> Loading...</div>';
        try {
            const res = await fetch('/documents/');
            const data = await res.json();
            
            documentList.innerHTML = '';
            if (data.documents.length === 0) {
                documentList.innerHTML = '<div class="status-msg">No documents found. Upload one!</div>';
                return;
            }

            data.documents.forEach(doc => {
                const docEl = document.createElement('div');
                docEl.className = 'doc-item' + (doc.document_id === currentDocumentId ? ' active' : '');
                docEl.dataset.id = doc.document_id;
                
                // Determine icon
                const ext = doc.filename.split('.').pop().toLowerCase();
                const icon = ext === 'pdf' ? 'fa-file-pdf' : 'fa-file-lines';

                docEl.innerHTML = `
                    <div class="doc-info" title="${doc.filename}">
                        <i class="fa-solid ${icon} doc-icon"></i>
                        <span class="doc-name">${doc.filename}</span>
                    </div>
                    <button class="doc-delete" title="Delete" data-id="${doc.document_id}">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                `;

                // Select document
                docEl.addEventListener('click', (e) => {
                    if (e.target.closest('.doc-delete')) return; // Ignore delete clicks
                    selectDocument(doc.document_id, doc.filename);
                });

                // Delete document
                const deleteBtn = docEl.querySelector('.doc-delete');
                deleteBtn.addEventListener('click', async (e) => {
                    e.stopPropagation();
                    await deleteDocument(doc.document_id);
                });

                documentList.appendChild(docEl);
            });
        } catch (err) {
            documentList.innerHTML = '<div class="status-msg error">Failed to load documents</div>';
        }
    }

    refreshBtn.addEventListener('click', loadDocuments);

    async function deleteDocument(id) {
        if (!confirm('Are you sure you want to delete this document?')) return;
        try {
            await fetch(`/documents/${id}`, { method: 'DELETE' });
            if (currentDocumentId === id) {
                currentDocumentId = null;
                resetChatState();
            }
            loadDocuments();
        } catch (err) {
            console.error("Delete failed", err);
        }
    }

    function selectDocument(id, filename) {
        currentDocumentId = id;
        
        // Update UI
        document.querySelectorAll('.doc-item').forEach(el => {
            el.classList.toggle('active', el.dataset.id === id);
        });

        activeDocBadge.classList.remove('hidden');
        activeDocName.textContent = filename;
        chatInput.disabled = false;
        sendBtn.disabled = false;
        chatInput.placeholder = "Ask a question about " + filename + "...";
        chatInput.focus();

        if (welcomeState && welcomeState.parentNode) {
            welcomeState.classList.add('hidden');
        }
        
        // Clear chat history for new doc (optional, but good for context isolation)
        chatHistory.innerHTML = '';
        appendMessage('ai', `I'm ready! What would you like to know about <strong>${filename}</strong>?`);
    }

    function resetChatState() {
        activeDocBadge.classList.add('hidden');
        chatInput.disabled = true;
        sendBtn.disabled = true;
        chatInput.placeholder = "Select a document first...";
        chatHistory.innerHTML = '';
        if (welcomeState) {
            welcomeState.classList.remove('hidden');
            chatHistory.appendChild(welcomeState);
        }
    }

    // --- Chat Logic ---
    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text || !currentDocumentId) return;

        // Add User Message
        appendMessage('user', text);
        chatInput.value = '';
        chatInput.disabled = true;
        sendBtn.disabled = true;

        // Add Loading Indicator
        const loadingId = appendTypingIndicator();

        try {
            const res = await fetch('/chat/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question: text,
                    document_id: currentDocumentId
                })
            });
            const data = await res.json();
            
            removeElement(loadingId);
            
            if (res.ok) {
                appendMessage('ai', data.answer, data.sources);
            } else {
                appendMessage('ai', '❌ Error: ' + (data.detail || 'Failed to get response'));
            }
        } catch (err) {
            removeElement(loadingId);
            appendMessage('ai', '❌ Network error connecting to chat API.');
        } finally {
            chatInput.disabled = false;
            sendBtn.disabled = false;
            chatInput.focus();
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    function appendMessage(role, text, sources = []) {
        const msgEl = document.createElement('div');
        msgEl.className = `message ${role}`;
        
        const icon = role === 'user' ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-robot"></i>';
        
        let sourcesHtml = '';
        if (sources && sources.length > 0) {
            sourcesHtml = `
                <div class="sources-box">
                    <strong>Sources:</strong> ${sources.map(s => `[Page ${s.page}]`).join(', ')}
                </div>
            `;
        }

        // Format newlines
        const formattedText = text.replace(/\n/g, '<br>');

        msgEl.innerHTML = `
            <div class="avatar">${icon}</div>
            <div class="msg-content">
                <p>${formattedText}</p>
                ${sourcesHtml}
            </div>
        `;
        
        chatHistory.appendChild(msgEl);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    function appendTypingIndicator() {
        const id = 'typing-' + Date.now();
        const msgEl = document.createElement('div');
        msgEl.className = 'message ai';
        msgEl.id = id;
        
        msgEl.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="msg-content">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        
        chatHistory.appendChild(msgEl);
        chatHistory.scrollTop = chatHistory.scrollHeight;
        return id;
    }

    function removeElement(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    // Initialize
    loadDocuments();
});

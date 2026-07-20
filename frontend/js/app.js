/* ==========================================================
   Stellar Agri AI - Main Application Controller
   ========================================================== */

document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const loader = document.getElementById('loader');
    const resultsArea = document.getElementById('results-area');
    const toggleJsonBtn = document.getElementById('toggle-json-btn');
    const jsonPreview = document.getElementById('json-preview');

    // 1. Form Submission Handler
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = userInput.value.trim();
        if (!query) return;

        await processQuery(query);
    });

    // 2. Sample Prompt Chips Click Handler
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', async () => {
            const prompt = chip.getAttribute('data-prompt');
            if (prompt) {
                userInput.value = prompt;
                await processQuery(prompt);
            }
        });
    });

    // 3. Raw JSON Toggle Button Handler
    toggleJsonBtn.addEventListener('click', () => {
        const isHidden = jsonPreview.classList.contains('hidden');
        if (isHidden) {
            jsonPreview.classList.remove('hidden');
            toggleJsonBtn.querySelector('span').textContent = 'Hide Raw JSON Output';
        } else {
            jsonPreview.classList.add('hidden');
            toggleJsonBtn.querySelector('span').textContent = 'Show Raw JSON Output';
        }
    });

    // Main Query Execution Flow
    async function processQuery(query) {
        // UI State: Loading
        sendBtn.disabled = true;
        loader.classList.remove('hidden');
        resultsArea.classList.add('hidden');

        try {
            const responseData = await ApiService.sendQuery(query);
            
            // UI State: Success Render
            UIRenderer.renderResponse(responseData);
        } catch (error) {
            alert(`Error communicating with Stellar Agri AI backend: ${error.message}\n\nPlease ensure the backend server is running on http://localhost:8000.`);
        } finally {
            sendBtn.disabled = false;
            loader.classList.add('hidden');
        }
    }
});

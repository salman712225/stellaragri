/* ==========================================================
   Stellar Agri AI - API Service
   ========================================================== */

class ApiService {
    static async sendQuery(question) {
        const isHosted = typeof window !== 'undefined' && 
                         window.location.protocol.startsWith('http') && 
                         window.location.hostname !== 'localhost' && 
                         window.location.hostname !== '127.0.0.1';

        const endpoints = isHosted 
            ? ['/chat'] 
            : ['/chat', 'http://127.0.0.1:8000/chat', 'http://localhost:8000/chat'];

        let lastError = null;

        for (const endpoint of endpoints) {
            try {
                // 1. Try JSON body POST first
                let response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({ question: question })
                });

                if (response.ok) {
                    return await response.json();
                }

                // If non-ok response, attempt to extract error detail from server
                let errorDetail = null;
                try {
                    const errData = await response.json();
                    errorDetail = errData.error || errData.detail || errData.message;
                } catch (_) {}

                if (response.status >= 400 && response.status < 600) {
                    if (isHosted) {
                        throw new Error(errorDetail || `Server error (${response.status}) while generating advice.`);
                    }
                }

                // Fallback to query param POST (for local testing)
                const queryUrl = `${endpoint}?question=${encodeURIComponent(question)}`;
                response = await fetch(queryUrl, {
                    method: 'POST',
                    headers: { 'Accept': 'application/json' }
                });

                if (response.ok) {
                    return await response.json();
                }
            } catch (err) {
                lastError = err;
                console.warn(`Attempt failed for endpoint ${endpoint}:`, err);
                if (isHosted) {
                    throw err;
                }
            }
        }

        throw lastError || new Error('Failed to connect to backend server. Please verify network connection.');
    }
}


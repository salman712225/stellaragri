/* ==========================================================
   Stellar Agri AI - API Service
   ========================================================== */

class ApiService {
    static async sendQuery(question) {
        const endpoints = [
            '/chat',
            'http://127.0.0.1:8000/chat',
            'http://localhost:8000/chat'
        ];

        let lastError = null;

        for (const endpoint of endpoints) {
            try {
                // Try JSON body POST first
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

                // Fallback to query param POST
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
            }
        }

        throw lastError || new Error('Failed to connect to backend server on http://127.0.0.1:8000');
    }
}

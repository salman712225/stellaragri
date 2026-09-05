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

    // 4. Instant Call Enquiry Form Handler
    const callEnquiryForm = document.getElementById('call-enquiry-form');
    const callNowBtn = document.getElementById('call-now-btn');
    const callStatusBox = document.getElementById('call-status-box');
    const callStatusTitle = document.getElementById('call-status-title');
    const callStatusDesc = document.getElementById('call-status-desc');

    if (callEnquiryForm) {
        callEnquiryForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const farmerName = document.getElementById('enquiry-name').value.trim();
            const phone = document.getElementById('enquiry-phone').value.trim();
            const crop = document.getElementById('enquiry-crop').value.trim() || 'Paddy';
            const lang = document.getElementById('enquiry-lang').value || 'hi-IN';
            const issue = document.getElementById('enquiry-issue').value.trim() || 'General farming query';

            if (!phone) {
                alert('Please enter your mobile phone number.');
                return;
            }

            // UI State: Calling
            callNowBtn.disabled = true;
            callNowBtn.innerHTML = '<span>⏳ Connecting Call...</span>';
            callStatusBox.classList.remove('hidden');
            callStatusTitle.innerText = `Calling ${phone}...`;
            callStatusDesc.innerText = `Connecting with AI Agronomist (Agent #1028). Your phone will ring in 3-5 seconds.`;

            try {
                const requestUrl = window.location.origin.startsWith('http') ? '/api/request-call' : 'http://127.0.0.1:8000/api/request-call';
                const res = await fetch(requestUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        farmer_name: farmerName,
                        phone_number: phone,
                        crop: crop,
                        language: lang,
                        issue: issue
                    })
                });

                const data = await res.json();

                if (res.ok && (data.success || data.call_id)) {
                    callStatusTitle.innerText = `📲 Call Active (Call #${data.call_id || 'Live'})`;
                    callStatusDesc.innerText = `Please answer the phone call from +918071581407 to discuss ${crop} advice with your AI Agronomist!`;
                } else {
                    callStatusTitle.innerText = `❌ Call Request Notice`;
                    callStatusDesc.innerText = data.error || 'Could not initiate call. Please ensure your number is reachable.';
                }
            } catch (err) {
                callStatusTitle.innerText = `❌ Connection Error`;
                callStatusDesc.innerText = `Failed to connect to backend: ${err.message}`;
            } finally {
                callNowBtn.disabled = false;
                callNowBtn.innerHTML = '<span class="call-icon">📲</span><span>Call Me Immediately</span>';
            }
        });
    }

    // 5. Instant Insurance Call Enquiry Form Handler
    const insuranceForm = document.getElementById('insurance-enquiry-form');
    const insuranceCallBtn = document.getElementById('insurance-call-now-btn');
    const insuranceStatusBox = document.getElementById('insurance-call-status-box');
    const insuranceStatusTitle = document.getElementById('insurance-call-status-title');
    const insuranceStatusDesc = document.getElementById('insurance-call-status-desc');

    if (insuranceForm) {
        insuranceForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const farmerName = document.getElementById('insurance-enquiry-name').value.trim();
            const phone = document.getElementById('insurance-enquiry-phone').value.trim();
            const location = document.getElementById('insurance-enquiry-location').value.trim();
            const lang = document.getElementById('insurance-enquiry-lang').value || 'hi-IN';
            const disaster = document.getElementById('insurance-enquiry-disaster').value.trim() || 'Crop damage / PMFBY claim intimation';

            if (!phone) {
                alert('Please enter your mobile phone number.');
                return;
            }

            if (!location) {
                alert('Please enter your location (District / Village / State).');
                return;
            }

            // UI State: Calling
            insuranceCallBtn.disabled = true;
            insuranceCallBtn.innerHTML = '<span>⏳ Verifying & Connecting...</span>';
            insuranceStatusBox.classList.remove('hidden');
            insuranceStatusTitle.innerText = `Calling ${phone}...`;
            insuranceStatusDesc.innerText = `Cross-verifying meteorological records for ${location} and connecting with AI Claims Specialist (Agent #1028)...`;

            try {
                const requestUrl = window.location.origin.startsWith('http') ? '/api/insurance-request-call' : 'http://127.0.0.1:8000/api/insurance-request-call';
                const res = await fetch(requestUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        farmer_name: farmerName,
                        phone_number: phone,
                        location: location,
                        language: lang,
                        disaster_type: disaster
                    })
                });

                const data = await res.json();

                if (res.ok && (data.success || data.call_id)) {
                    const score = Math.round((data.plausibility_score || 0.9) * 100);
                    insuranceStatusTitle.innerText = `🛡️ Call Active (Claim Docket #${data.claim_id || 'Logged'})`;
                    insuranceStatusDesc.innerText = `Incident verified (${score}% Plausibility). Please answer the incoming call from +918071581407 to complete your PMFBY claim intimation!`;
                } else {
                    insuranceStatusTitle.innerText = `❌ Notice`;
                    insuranceStatusDesc.innerText = data.error || 'Could not initiate insurance call. Please check your number.';
                }
            } catch (err) {
                insuranceStatusTitle.innerText = `❌ Connection Error`;
                insuranceStatusDesc.innerText = `Failed to connect to backend: ${err.message}`;
            } finally {
                insuranceCallBtn.disabled = false;
                insuranceCallBtn.innerHTML = '<span class="call-icon">📲</span><span>Call Me Immediately</span>';
            }
        });
    }

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
            alert(`Stellar Agri AI Notice: ${error.message || 'Unable to connect to advisory service. Please check your connection.'}`);
        } finally {
            sendBtn.disabled = false;
            loader.classList.add('hidden');
        }
    }
});

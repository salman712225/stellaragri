/* ==========================================================
   Stellar Agri AI - Dynamic UI Renderer
   ========================================================== */

class UIRenderer {
    static renderResponse(data) {
        const resultsArea = document.getElementById('results-area');
        resultsArea.classList.remove('hidden');

        // Scroll to results
        resultsArea.scrollIntoView({ behavior: 'smooth', block: 'start' });

        // 1. Badges
        const intentBadge = document.getElementById('intent-badge');
        const confidenceBadge = document.getElementById('confidence-badge');

        intentBadge.textContent = `Intent: ${(data.intent || 'General').toUpperCase().replace('_', ' ')}`;
        const confidenceVal = data.confidence ? Math.round(data.confidence * 100) : 100;
        confidenceBadge.textContent = `Confidence: ${confidenceVal}%`;

        // 2. Executive Summary
        const summaryContent = document.getElementById('summary-content');
        summaryContent.textContent = data.summary || 'Summary unavailable.';

        // 3. Key Recommendations / Answers
        const answersList = document.getElementById('answers-list');
        answersList.innerHTML = '';
        const answers = Array.isArray(data.answer) ? data.answer : (data.answer ? [data.answer] : []);
        if (answers.length > 0) {
            answers.forEach(ans => {
                const li = document.createElement('li');
                li.textContent = ans;
                answersList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = 'Follow specific domain cards below for complete advice.';
            answersList.appendChild(li);
        }

        // Helper to show/hide cards
        const setupCard = (cardId, hasData, populateFn) => {
            const card = document.getElementById(cardId);
            if (hasData) {
                card.classList.remove('hidden');
                populateFn();
            } else {
                card.classList.add('hidden');
            }
        };

        // 4. Crop Recommendation Card
        const cropData = data.crop_recommendation;
        setupCard('card-crop', cropData && (cropData.crop || cropData.reason), () => {
            document.getElementById('crop-name').textContent = cropData.crop ? cropData.crop.toUpperCase() : 'N/A';
            document.getElementById('crop-reason').textContent = cropData.reason || 'Recommended based on soil and climatic conditions.';
        });

        // 5. Fertilizer Advice Card
        const fertData = data.fertilizer_advice;
        setupCard('card-fertilizer', fertData && (
            (Array.isArray(fertData.recommended) && fertData.recommended.length > 0) || fertData.application
        ), () => {
            const pillsContainer = document.getElementById('fertilizer-pills');
            pillsContainer.innerHTML = '';

            const items = Array.isArray(fertData.recommended) ? fertData.recommended : [fertData.recommended];
            items.forEach(item => {
                if (!item) return;
                const pill = document.createElement('span');
                pill.className = 'pill-item';
                if (typeof item === 'object' && item.name) {
                    pill.textContent = `${item.name}${item.reason ? ': ' + item.reason : ''}`;
                } else {
                    pill.textContent = String(item);
                }
                pillsContainer.appendChild(pill);
            });

            document.getElementById('fertilizer-application').textContent = fertData.application || 'Apply as per prescribed dosage.';
        });

        // 6. Disease Analysis Card
        const diseaseData = data.disease_analysis;
        setupCard('card-disease', diseaseData && (diseaseData.disease || diseaseData.recommendation), () => {
            document.getElementById('disease-name').textContent = diseaseData.disease || 'Unknown';
            
            const symptoms = Array.isArray(diseaseData.symptoms) ? diseaseData.symptoms.join(', ') : (diseaseData.symptoms || '');
            document.getElementById('disease-symptoms').textContent = symptoms ? `Symptoms: ${symptoms}` : '';
            document.getElementById('disease-recommendation').textContent = diseaseData.recommendation || '';
        });

        // 7. Pest Analysis Card
        const pestData = data.pest_analysis;
        setupCard('card-pest', pestData && (pestData.pest || pestData.recommendation), () => {
            document.getElementById('pest-name').textContent = pestData.pest || 'Detected Pest';
            document.getElementById('pest-recommendation').textContent = pestData.recommendation || 'Follow organic pest management.';
        });

        // 8. Weather Insights Card
        const weatherData = data.weather_analysis;
        setupCard('card-weather', weatherData && (weatherData.impact || weatherData.recommendation), () => {
            document.getElementById('weather-impact').textContent = weatherData.impact || 'Weather condition analysis active.';
            document.getElementById('weather-recommendation').textContent = weatherData.recommendation || '';
        });

        // 9. Market Analysis Card
        const marketData = data.market_analysis;
        setupCard('card-market', marketData && (marketData.current_price || marketData.recommendation), () => {
            document.getElementById('market-price').textContent = marketData.current_price || 'Live Prices Checked';
            document.getElementById('market-recommendation').textContent = marketData.recommendation || 'Market trend analysis.';
        });

        // 10. Irrigation Advice Card
        const irrData = data.irrigation_advice;
        setupCard('card-irrigation', irrData && (irrData.schedule || irrData.recommendation), () => {
            document.getElementById('irrigation-schedule').textContent = irrData.schedule ? `Schedule: ${irrData.schedule}` : '';
            document.getElementById('irrigation-recommendation').textContent = irrData.recommendation || '';
        });

        // 11. Crop Management Card
        const mgmtData = data.crop_management;
        setupCard('card-management', mgmtData && (mgmtData.growth_stage || mgmtData.recommendation), () => {
            document.getElementById('management-stage').textContent = mgmtData.growth_stage ? `Stage: ${mgmtData.growth_stage}` : '';
            document.getElementById('management-recommendation').textContent = mgmtData.recommendation || '';
        });

        // 12. Warnings
        const warningsBox = document.getElementById('warnings-box');
        const warningsList = document.getElementById('warnings-list');
        warningsList.innerHTML = '';
        if (Array.isArray(data.warnings) && data.warnings.length > 0) {
            warningsBox.classList.remove('hidden');
            data.warnings.forEach(w => {
                const li = document.createElement('li');
                li.textContent = w;
                warningsList.appendChild(li);
            });
        } else {
            warningsBox.classList.add('hidden');
        }

        // 13. Next Steps
        const nextstepsBox = document.getElementById('nextsteps-box');
        const nextstepsList = document.getElementById('nextsteps-list');
        nextstepsList.innerHTML = '';
        if (Array.isArray(data.next_steps) && data.next_steps.length > 0) {
            nextstepsBox.classList.remove('hidden');
            data.next_steps.forEach(s => {
                const li = document.createElement('li');
                li.textContent = s;
                nextstepsList.appendChild(li);
            });
        } else {
            nextstepsBox.classList.add('hidden');
        }

        // 14. Raw JSON Preview
        document.getElementById('json-preview').textContent = JSON.stringify(data, null, 2);
    }
}

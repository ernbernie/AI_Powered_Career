document.getElementById('uploadForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    const formData = new FormData(this);
    const errorDiv = document.getElementById('error');
    const outputContainer = document.getElementById('roadmapCardContainer');

    errorDiv.textContent = '';
    outputContainer.innerHTML = '<p>Loading roadmap...</p>';

    // Client-side validation
    const resume = document.getElementById('resume').files[0];
    if (!resume) {
        errorDiv.textContent = 'Please upload a resume.';
        outputContainer.innerHTML = '';
        return;
    }
    if (resume.size > 500 * 1024) {
        errorDiv.textContent = 'Resume file too large (max 500KB).';
        outputContainer.innerHTML = '';
        return;
    }
    const goal = document.getElementById('goal').value.trim();
    if (goal.length < 10) {
        errorDiv.textContent = 'Goal must be at least 10 characters.';
        outputContainer.innerHTML = '';
        return;
    }
    const location = document.getElementById('location').value.trim();
    const locRegex = /^[A-Za-z\s\-]{2,},\s*[A-Z]{2}$/;
    if (!locRegex.test(location)) {
        errorDiv.textContent = 'Location must be in "City, ST" format.';
        outputContainer.innerHTML = '';
        return;
    }

    try {
        const response = await fetch('/generate_prompt', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        outputContainer.innerHTML = '';

        if (data.error) {
            errorDiv.textContent = data.error;
        } else {
            try {
                const roadmapData = JSON.parse(data.roadmap);
                renderRoadmap(formatRoadmapData(roadmapData));
            } catch (e) {
                errorDiv.textContent = 'Error parsing roadmap data.';
                console.error('JSON parsing error:', e, 'Raw data:', data.roadmap);
            }
        }
    } catch (err) {
        outputContainer.innerHTML = '';
        errorDiv.textContent = 'Error connecting to server. Please try again.';
        console.error('Fetch error:', err);
    }
});

/**
 * Formats and validates the roadmap data to prevent rendering errors.
 * @param {Object} data - Raw roadmap data from OpenAI
 * @returns {Object} - A safe, structured roadmap data object
 */
function formatRoadmapData(data) {
    const formatted = {
        five_year_goal: data.five_year_goal || 'Goal not specified.',
        location: data.location || 'Location not specified.',
        yearly_goals: Array.isArray(data.yearly_goals) ? data.yearly_goals : []
    };

    // FIX: Corrected typo from 'yearsly_goals' to 'yearly_goals'
    formatted.yearly_goals = formatted.yearly_goals
        .sort((a, b) => (b.year || 0) - (a.year || 0))
        .map(year => {
            const yearData = {
                year: year.year || 'N/A',
                year_goal: year.year_goal || 'Yearly goal not specified.',
                quarterly_smart_goals: []
            };
            if (year.year === 1 && Array.isArray(year.quarterly_smart_goals)) {
                yearData.quarterly_smart_goals = year.quarterly_smart_goals.map(q => ({
                    quarter: q.quarter || 'Q?',
                    goal: q.goal || 'Quarterly goal not specified.',
                    smart: q.smart || { S: '', M: '', A: '', R: '', T: '' }
                }));
            }
            return yearData;
        });

    return formatted;
}

/**
 * Renders the interactive roadmap card component.
 * @param {Object} data - The formatted roadmap data object.
 */
function renderRoadmap(data) {
    console.log('Rendering roadmap:', data); // Debug log
    const container = document.getElementById('roadmapCardContainer');
    container.innerHTML = ''; // Clear loading text

    const card = document.createElement('div');
    card.className = 'roadmap-card';

    // --- 1. Header ---
    const header = document.createElement('div');
    header.className = 'roadmap-header';
    const title = document.createElement('h1');
    title.className = 'roadmap-title';
    title.textContent = data.five_year_goal;
    const location = document.createElement('p');
    location.className = 'roadmap-location';
    location.textContent = data.location;
    header.appendChild(title);
    header.appendChild(location);
    card.appendChild(header);

    // --- 2. Yearly Goals Section ---
    const yearlyGoalsSection = document.createElement('div');
    yearlyGoalsSection.className = 'goals-section';
    data.yearly_goals.forEach(yearData => {
        const goalItem = document.createElement('div');
        goalItem.className = 'goal-item';
        const details = document.createElement('details');
        details.className = 'details-container';
        const summary = document.createElement('summary');
        summary.className = 'summary-container';
        const yearText = document.createElement('span');
        yearText.textContent = `Year ${yearData.year}: ${yearData.year_goal}`;
        summary.appendChild(yearText);
        const chevron = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        chevron.setAttribute('class', 'chevron');
        chevron.setAttribute('viewBox', '0 0 24 24');
        chevron.innerHTML = '<path d="M7 14l5-5 5 5z"/>';
        summary.appendChild(chevron);
        details.appendChild(summary);
        goalItem.appendChild(details);
        yearlyGoalsSection.appendChild(goalItem);
    });
    card.appendChild(yearlyGoalsSection);

    // --- 3. Quarterly SMART Goals Section ---
    const year1Data = data.yearly_goals.find(y => y.year === 1);
    if (year1Data && year1Data.quarterly_smart_goals.length > 0) {
        const quarterlyGoalsSection = document.createElement('div');
        quarterlyGoalsSection.className = 'goals-section';
        const quarterlyTitle = document.createElement('h3');
        quarterlyTitle.className = 'section-title';
        quarterlyTitle.textContent = 'Quarterly SMART Goals for Year 1';
        quarterlyGoalsSection.appendChild(quarterlyTitle);

        year1Data.quarterly_smart_goals.forEach(quarterData => {
            const goalItem = document.createElement('div');
            goalItem.className = 'goal-item';
            const details = document.createElement('details');
            details.className = 'details-container';
            const summary = document.createElement('summary');
            summary.className = 'summary-container';
            const quarterText = document.createElement('span');
            const quarterLabel = document.createElement('span');
            quarterLabel.className = 'quarter-label';
            quarterLabel.textContent = quarterData.quarter + ':';
            quarterText.appendChild(quarterLabel);
            quarterText.appendChild(document.createTextNode(' ' + quarterData.goal));
            summary.appendChild(quarterText);
            const chevron = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            chevron.setAttribute('class', 'chevron');
            chevron.setAttribute('viewBox', '0 0 24 24');
            chevron.innerHTML = '<path d="M7 14l5-5 5 5z"/>';
            summary.appendChild(chevron);
            details.appendChild(summary);
            
            const content = document.createElement('div');
            content.className = 'details-content';
            if (quarterData.smart) {
                const smartList = document.createElement('ul');
                smartList.className = 'smart-breakdown';
                ['S', 'M', 'A', 'R', 'T'].forEach(key => {
                    if (quarterData.smart[key]) {
                        const smartItem = document.createElement('li');
                        smartItem.className = 'smart-item';
                        const smartLabel = document.createElement('span');
                        smartLabel.className = 'smart-label';
                        smartLabel.textContent = key + ':';
                        smartItem.appendChild(smartLabel);
                        const smartText = document.createElement('span');
                        smartText.className = 'smart-text';
                        smartText.textContent = quarterData.smart[key];
                        smartItem.appendChild(smartText);
                        smartList.appendChild(smartItem);
                    }
                });
                content.appendChild(smartList);
            }
            details.appendChild(content);
            goalItem.appendChild(details);
            quarterlyGoalsSection.appendChild(goalItem);
        });
        card.appendChild(quarterlyGoalsSection);
    }
    
    container.appendChild(card);
}
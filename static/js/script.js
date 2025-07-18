/* static/js/script.js */

/* ---------- 1. FORM SUBMIT & ROADMAP RENDER (Existing Code) ---------- */
document.getElementById('uploadForm').addEventListener('submit', async function (event) {
    event.preventDefault();
    const formData  = new FormData(this);
    const errorDiv  = document.getElementById('error');
    const outputDiv = document.getElementById('roadmapCardContainer');

    errorDiv.textContent = '';
    outputDiv.innerHTML  = '<p>Loading roadmap…</p>';

    /* ----- client‑side validation ----- */
    const resume   = formData.get('resume');
    const goal     = formData.get('goal').trim();
    const location = formData.get('location').trim();
    const locRegex = /^[A-Za-z\s\-]{2,},\s*[A-Z]{2}$/;

    if (!resume)              { errorDiv.textContent = 'Please upload a resume.'; return; }
    if (resume.size > 500*1024){ errorDiv.textContent = 'Resume too large (max 500 KB).'; return; }
    if (goal.length < 10)     { errorDiv.textContent = 'Goal must be at least 10 characters.'; return; }
    if (!locRegex.test(location)){ errorDiv.textContent = 'Location must be in "City, ST" format.'; return; }

    try {
        const res  = await fetch('/generate_prompt', { method:'POST', body: formData });
        const data = await res.json();
        outputDiv.innerHTML = '';

        if (data.error) throw new Error(data.error);

        /* ----- roadmap render ----- */
        const roadmapObj = JSON.parse(data.roadmap);
        renderRoadmap(formatRoadmapData(roadmapObj));

        /* ----- NEW: start polling for the market intelligence report ----- */
        window.currentJobId = data.job_id; // Stash job_id globally
        if (window.pollInterval) clearInterval(window.pollInterval); // Clear any old timers
        window.pollInterval = setInterval(() => pollReportStatus(data.job_id), 4000); // Poll every 4s

    } catch (err) {
        outputDiv.innerHTML = '';
        errorDiv.textContent = err.message || 'Server error – try again.';
        console.error(err);
    }
});


/* ---------- 2. POLLING & MODAL DISPLAY (NEW LOGIC) ---------- */
async function pollReportStatus(jobId) {
    try {
        const res = await fetch(`/report_status?id=${jobId}`);
        if (!res.ok) { // Handle server errors during polling
            console.error(`Polling failed with status: ${res.status}`);
            clearInterval(window.pollInterval);
            return;
        }
        const data = await res.json();

        console.log(`Polling job ${jobId}, status: ${data.status}`);

        if (data.status === 'ready') {
            clearInterval(window.pollInterval); // Stop polling
            document.getElementById('emailModal').classList.remove('hidden'); // Show the modal
        } else if (data.status === 'error') {
            clearInterval(window.pollInterval); // Stop polling on error
            // Optionally, show an error message to the user
            document.getElementById('error').textContent = 'Could not generate market report. Please try again.';
        }
        // If status is 'running' or 'sent', do nothing and let the polling continue or timeout naturally
    } catch (err) {
        console.error('Error during polling:', err);
        clearInterval(window.pollInterval); // Stop polling on network error
    }
}


/* ---------- 3. SEND REPORT BUTTON HANDLER (NEW LOGIC) ---------- */
document.getElementById('sendReportBtn').addEventListener('click', async function() {
    const emailInput = document.getElementById('emailInput');
    const email = emailInput.value.trim();
    const emailStatus = document.getElementById('emailStatus');
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/; // Simple email validation regex

    if (!emailRegex.test(email)) {
        emailStatus.textContent = 'Please enter a valid email address.';
        return;
    }

    emailStatus.textContent = 'Sending...';
    this.disabled = true; // Disable button to prevent multiple clicks

    try {
        const res = await fetch('/send_report', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: window.currentJobId, email: email })
        });
        const data = await res.json();

        if (data.error) throw new Error(data.error);

        if (data.status === 'sent') {
            emailStatus.textContent = '✅ Report sent! Check your inbox.';
            // Hide the modal after a short delay
            setTimeout(() => {
                document.getElementById('emailModal').classList.add('hidden');
            }, 3000);
        }
    } catch (err) {
        emailStatus.textContent = `Error: ${err.message}`;
        this.disabled = false; // Re-enable button on failure
    }
});


/* ---------- 4. ROADMAP FORMATTING & RENDERING (Existing Code, No Changes) ---------- */
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
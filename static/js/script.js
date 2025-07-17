document.getElementById('uploadForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const formData = new FormData(this);
    const errorDiv = document.getElementById('error');
    const promptOutput = document.getElementById('promptOutput');

    errorDiv.textContent = '';
    promptOutput.textContent = '';

    // Basic client-side validation (file type and size)
    const resume = document.getElementById('resume').files[0];
    if (!resume) {
        errorDiv.textContent = 'Please upload a resume.';
        return;
    }
    if (resume.size > 500 * 1024) {  // 500KB ~2 pages
        errorDiv.textContent = 'Resume file too large (max 500KB).';
        return;
    }
    const goal = document.getElementById('goal').value.trim();
    if (goal.length < 10) {
        errorDiv.textContent = 'Goal must be at least 10 characters.';
        return;
    }
    const location = document.getElementById('location').value.trim();
    const locRegex = /^[A-Za-z\s\-]{2,},\s*[A-Z]{2}$/;
    if (!locRegex.test(location)) {
        errorDiv.textContent = 'Location must be in "City, ST" format.';
        return;
    }

    try {
        const response = await fetch('/generate_prompt', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            errorDiv.textContent = data.error;
        } else {
            promptOutput.textContent = data.prompt;
        }
    } catch (err) {
        errorDiv.textContent = 'Error connecting to server. Please try again.';
    }
});
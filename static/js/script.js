document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('generator-form');
    const generateBtn = document.getElementById('generate-btn');
    const outputSection = document.getElementById('output-section');
    const resultContent = document.getElementById('result-content');
    const loadingDiv = document.getElementById('loading');
    const copyBtn = document.getElementById('copy-btn');
    const pdfBtn = document.getElementById('pdf-btn');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // UI Updates
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating... (This may take a moment)';
        outputSection.style.display = 'block';
        resultContent.innerHTML = '';
        loadingDiv.classList.remove('hidden');
        copyBtn.style.display = 'none';
        pdfBtn.style.display = 'none';

        // Collect Data
        const formData = {
            subject: document.getElementById('subject').value,
            level: document.getElementById('level').value,
            duration: document.getElementById('duration').value,
            unit: document.getElementById('unit').value, // Get the unit (Weeks/Months/Semesters)
            goal: document.getElementById('goal').value
        };

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Something went wrong');
            }

            // Render Markdown
            resultContent.innerHTML = marked.parse(data.content);
            copyBtn.style.display = 'inline-block';
            pdfBtn.style.display = 'inline-block';

        } catch (error) {
            resultContent.innerHTML = `<div style="color: red; padding: 1rem; border: 1px solid red; border-radius: 4px;">
                <strong>Error:</strong> ${error.message}
            </div>`;
        } finally {
            loadingDiv.classList.add('hidden');
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate Curriculum';
        }
    });

    // Copy to Clipboard Logic
    copyBtn.addEventListener('click', () => {
        const text = resultContent.innerText;
        navigator.clipboard.writeText(text).then(() => {
            const originalText = copyBtn.textContent;
            copyBtn.textContent = 'Copied!';
            setTimeout(() => {
                copyBtn.textContent = originalText;
            }, 2000);
        });
    });

    // Download PDF Logic
    pdfBtn.addEventListener('click', () => {
        const element = document.getElementById('result-content');

        // Options for pdf generation
        const opt = {
            margin: 1,
            filename: 'curriculum.pdf',
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2 },
            jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
        };

        // Use html2pdf library
        html2pdf().set(opt).from(element).save();
    });
});

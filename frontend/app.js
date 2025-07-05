document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('shorten-form');
    const urlInput = document.getElementById('url-input');
    const resultDiv = document.getElementById('result');
    const errorDiv = document.getElementById('error');
    const errorMessage = document.getElementById('error-message');
    const shortUrlLink = document.getElementById('short-url');
    const adminUrlLink = document.getElementById('admin-url');
    const copyButton = document.getElementById('copy-button');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const longUrl = urlInput.value;

        // Reset UI
        resultDiv.classList.add('hidden');
        errorDiv.classList.add('hidden');

        try {
            const response = await fetch('http://127.0.0.1:8000/shorten', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ target_url: longUrl }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'An error occurred.');
            }

            shortUrlLink.href = data.url;
            shortUrlLink.textContent = data.url;
            adminUrlLink.href = data.admin_url;
            adminUrlLink.textContent = data.admin_url;
            resultDiv.classList.remove('hidden');

        } catch (err) {
            errorMessage.textContent = err.message;
            errorDiv.classList.remove('hidden');
        }
    });

    copyButton.addEventListener('click', () => {
        navigator.clipboard.writeText(shortUrlLink.href).then(() => {
            copyButton.textContent = 'Copied!';
            setTimeout(() => {
                copyButton.textContent = 'Copy';
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy: ', err);
        });
    });
});

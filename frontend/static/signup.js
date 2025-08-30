// --- DOM Element References ---
const signupForm = document.getElementById('signup-form');
const nameInput = document.getElementById('name');
const phoneInput = document.getElementById('phone');
const emailInput = document.getElementById('email');
const genderInput = document.getElementById('gender');
const passwordInput = document.getElementById('password');
const errorMessage = document.getElementById('error-message');

// Use relative URL for backend
const SIGNUP_URL = '/signup';

// --- Event Listener for Form Submission ---
signupForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    errorMessage.textContent = '';

    const formData = {
        name: nameInput.value,
        phone: phoneInput.value,
        email: emailInput.value,
        gender: genderInput.value,
        password: passwordInput.value,
    };

    try {
        const response = await fetch(SIGNUP_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData),
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
            console.log('Signup successful, redirecting to login...');
            window.location.href = 'login.html';
        } else {
            errorMessage.textContent = data.message || 'An error occurred.';
        }
    } catch (error) {
        console.error('Signup request failed:', error);
        errorMessage.textContent = 'Could not connect to the server.';
    }
});

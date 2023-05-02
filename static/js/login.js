const form = document.getElementById('login-form');
const errorMessage = document.getElementById('error-message');
form.addEventListener('submit', async (event) => {
event.preventDefault();
    const formData = new FormData(form);
    const response = await fetch(form.action, {
        method: form.method,
        body: formData,
    });
    if (response.ok) {
    // Redirect to homepage on successful login
        window.location = response.url; 
    } else {
        const error = await response.json();
        errorMessage.textContent = error.message;
        errorMessage.style.display = 'block';
        errorMessage.style.color = 'red';
        errorMessage.style.textAlign = 'center';
        // alert('Error: Could not complete the request.');
    }
});

const registerForm = document.getElementById('register-form');
const errorRegister = document.getElementById('error-register');
registerForm.addEventListener('submit', async (event) => {
event.preventDefault();
    const formData = new FormData(registerForm);
    const response = await fetch(registerForm.action, {
        method: registerForm.method,
        body: formData,
    });
    if (response.ok) {
    // Redirect to homepage on successful register
        window.location = response.url; 
    } else {
        const error = await response.json();
        errorRegister.textContent = error.message;
        errorRegister.style.display = 'block';
        errorRegister.style.color = 'red';
        errorRegister.style.textAlign = 'center';
        // alert('Error: Could not complete the request.');
    }
});
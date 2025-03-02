// Counter Animation
function animateCounter(element) {
    const target = parseInt(element.getAttribute('data-target'));
    const duration = 2000; // Animation duration in milliseconds
    const step = target / (duration / 16); // Update every 16ms (60fps)
    let current = 0;

    const timer = setInterval(() => {
        current += step;
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, 16);
}

// Intersection Observer for scroll animations
const observerOptions = {
    threshold: 0.2,
    rootMargin: '0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
            
            // Animate counters if they exist
            const counters = entry.target.querySelectorAll('.counter');
            counters.forEach(counter => animateCounter(counter));
            
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Apply animations to elements
document.querySelectorAll('.animate-on-scroll').forEach(element => {
    element.style.opacity = '0';
    element.style.transform = 'translateY(20px)';
    element.style.transition = 'all 0.6s ease-out';
    observer.observe(element);
});

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Navbar scroll effect
const navbar = document.querySelector('.navbar');
let lastScroll = 0;

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll <= 0) {
        navbar.style.boxShadow = 'none';
    } else {
        navbar.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
    }
    
    lastScroll = currentScroll;
});

// Toggle between login and register forms
function toggleForms(form) {
    const loginForm = document.querySelector('.login-form');
    const registerForm = document.querySelector('.register-form');
    
    if (form === 'register') {
        loginForm.classList.add('hidden');
        registerForm.classList.remove('hidden');
    } else {
        registerForm.classList.add('hidden');
        loginForm.classList.remove('hidden');
    }
}

// Form validation and submission
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', (e) => {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);

        // Simple validation for register form
        if (form.classList.contains('register-form')) {
            if (data.password.length < 6) {
                showAlert('Password must be at least 6 characters long', 'danger');
                form.querySelector('input[name="password"]').parentElement.classList.add('shake');
                setTimeout(() => {
                    form.querySelector('input[name="password"]').parentElement.classList.remove('shake');
                }, 500);
                return; 
            }
        }
        // If validation passes, submit the form
        form.submit();
    });
});

// Show alert message
function showAlert(message, type) {
    const alert = document.getElementById('alert');
    alert.textContent = message;
    alert.className = `alert ${type}`;
    alert.classList.add('show');
    setTimeout(() => {
        alert.classList.remove('show');
    }, 3000);
}

// Remove shake animation when input changes
document.querySelectorAll('input').forEach(input => {
    input.addEventListener('input ', () => {
        input.parentElement.classList.remove('shake');
    });
});

document.addEventListener('DOMContentLoaded', () => {
    // Automatically hide alerts
    const alerts = document.querySelectorAll('.alert.show');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => {
                alert.remove();
            }, 500); // Remove from DOM after animation ends
        }, 3000); // Show for 3 seconds
    });

    // Clear flash message containers after rendering
    const flashContainers = document.querySelectorAll('.flash-messages');
    flashContainers.forEach(container => {
        if (container.innerHTML.trim() === '') {
            container.style.display = 'none'; // Hide empty containers
        }
    });
});
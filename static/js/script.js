// Quiz Timer
class QuizTimer {
    constructor(duration, displayElement, onTimeUp) {
        this.duration = duration;
        this.display = displayElement;
        this.onTimeUp = onTimeUp;
        this.timeLeft = duration;
        this.timer = null;
    }

    start() {
        this.timer = setInterval(() => {
            this.timeLeft--;
            this.updateDisplay();
            
            if (this.timeLeft <= 0) {
                this.stop();
                if (this.onTimeUp) this.onTimeUp();
            }
        }, 1000);
    }

    stop() {
        if (this.timer) {
            clearInterval(this.timer);
            this.timer = null;
        }
    }

    updateDisplay() {
        const minutes = Math.floor(this.timeLeft / 60);
        const seconds = this.timeLeft % 60;
        this.display.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        // Add warning colors
        if (this.timeLeft <= 30) {
            this.display.classList.add('text-danger');
        } else if (this.timeLeft <= 60) {
            this.display.classList.add('text-warning');
        }
    }
}

// Form Validation
document.addEventListener('DOMContentLoaded', function() {
    // Password strength indicator
    const passwordInput = document.querySelector('input[type="password"]');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const strength = calculatePasswordStrength(this.value);
            updatePasswordStrengthIndicator(strength);
        });
    }

    // Quiz form submission
    const quizForm = document.querySelector('#quiz-form');
    if (quizForm) {
        quizForm.addEventListener('submit', function(e) {
            if (!validateQuizForm()) {
                e.preventDefault();
            }
        });

        // Initialize quiz timer if time limit is set
        const timerElement = document.querySelector('#quiz-timer');
        const timeLimitElement = document.querySelector('#time-limit');
        if (timerElement && timeLimitElement) {
            const timeLimit = parseInt(timeLimitElement.value) * 60;
            const timer = new QuizTimer(timeLimit, timerElement, () => {
                quizForm.submit();
            });
            timer.start();
        }
    }

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add('fade');
            setTimeout(() => alert.remove(), 150);
        }, 5000);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Add animation to feature cards
    const cards = document.querySelectorAll('.feature-card, .category-card');
    const animateCards = () => {
        cards.forEach(card => {
            const rect = card.getBoundingClientRect();
            if (rect.top <= window.innerHeight * 0.85) {
                card.classList.add('fade-in');
            }
        });
    };

    window.addEventListener('scroll', animateCards);
    animateCards(); // Initial check
});

// Password strength calculator
function calculatePasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength++;
    if (password.match(/[a-z]/)) strength++;
    if (password.match(/[A-Z]/)) strength++;
    if (password.match(/[0-9]/)) strength++;
    if (password.match(/[^a-zA-Z0-9]/)) strength++;
    
    return strength;
}

function updatePasswordStrengthIndicator(strength) {
    const indicator = document.querySelector('.password-strength');
    if (!indicator) return;

    const strengthClasses = [
        'bg-danger',
        'bg-warning',
        'bg-info',
        'bg-primary',
        'bg-success'
    ];

    indicator.className = 'password-strength progress-bar ' + strengthClasses[strength - 1];
    indicator.style.width = `${strength * 20}%`;
}

// Quiz form validation
function validateQuizForm() {
    const questions = document.querySelectorAll('.question');
    let isValid = true;

    questions.forEach(question => {
        const answered = question.querySelector('input[type="radio"]:checked');
        if (!answered) {
            isValid = false;
            question.classList.add('border-danger');
        } else {
            question.classList.remove('border-danger');
        }
    });

    if (!isValid) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger';
        alert.textContent = 'Please answer all questions before submitting.';
        document.querySelector('#quiz-alerts').appendChild(alert);
    }

    return isValid;
}

// Profile image preview
function previewImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.querySelector('#profile-image-preview').src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Leaderboard filters
function updateLeaderboard(timeframe) {
    const url = new URL(window.location.href);
    url.searchParams.set('timeframe', timeframe);
    window.location.href = url.toString();
}

// Session management
function confirmEndSession(sessionId) {
    return confirm('Are you sure you want to end this session?');
}

function confirmEndAllSessions() {
    return confirm('Are you sure you want to end all other sessions? This will log you out from all other devices.');
}

// Handle quiz navigation
function navigateQuestion(direction) {
    const currentQuestion = document.querySelector('.question.active');
    const questions = document.querySelectorAll('.question');
    const currentIndex = Array.from(questions).indexOf(currentQuestion);
    
    let newIndex = direction === 'next' ? currentIndex + 1 : currentIndex - 1;
    
    if (newIndex >= 0 && newIndex < questions.length) {
        currentQuestion.classList.remove('active');
        questions[newIndex].classList.add('active');
        
        // Update progress
        const progress = ((newIndex + 1) / questions.length) * 100;
        document.querySelector('.progress-bar').style.width = `${progress}%`;
        
        // Update navigation buttons
        document.querySelector('.prev-question').disabled = newIndex === 0;
        document.querySelector('.next-question').disabled = newIndex === questions.length - 1;
    }
}

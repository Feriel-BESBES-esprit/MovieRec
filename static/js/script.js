// ==================== UTILITY FUNCTIONS ====================

/**
 * Get CSRF token from cookies
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Show notification message
 */
function showNotification(message, type = 'success', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        <span>${message}</span>
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('removing');
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

/**
 * Toggle watchlist for a movie
 */
function toggleWatchlist(movieId) {
    if (!isUserAuthenticated()) {
        window.location.href = '/login/';
        return;
    }

    const csrftoken = getCookie('csrftoken');
    
    fetch(`/movie/${movieId}/watchlist/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            const message = data.added ? 'Added to watchlist' : 'Removed from watchlist';
            showNotification(message, 'success');
            
            // Update button appearance if it exists
            const buttons = document.querySelectorAll(`button[onclick*="${movieId}"]`);
            buttons.forEach(btn => {
                if (btn.querySelector('#watchlist-text')) {
                    btn.querySelector('#watchlist-text').textContent = 
                        data.added ? 'Remove from Watchlist' : 'Add to Watchlist';
                }
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred', 'error');
    });
}

/**
 * Check if user is authenticated
 */
function isUserAuthenticated() {
    // Check if there's a user element in the navbar
    return document.querySelector('.nav-user') !== null;
}

/**
 * Rate a movie
 */
function rateMovie(movieId, rating) {
    if (!isUserAuthenticated()) {
        window.location.href = '/login/';
        return;
    }

    const csrftoken = getCookie('csrftoken');
    
    const formData = new FormData();
    formData.append('rating', rating);

    fetch(`/movie/${movieId}/rate/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification('Rating saved successfully!', 'success');
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred while saving your rating', 'error');
    });
}

// ==================== DOM READY ====================
document.addEventListener('DOMContentLoaded', function() {
    // Initialize event listeners
    initializeRatingStars();
    initializeSearchForm();
    initializeNavigation();
});

/**
 * Initialize rating stars interaction
 */
function initializeRatingStars() {
    const starLabels = document.querySelectorAll('.star-label');
    const form = document.getElementById('rating-form');

    starLabels.forEach(label => {
        label.addEventListener('click', function(e) {
            // Don't submit the form on star click, just select it
            if (form) {
                form.addEventListener('submit', function(e) {
                    e.preventDefault();
                    const rating = document.querySelector('input[name="rating"]:checked');
                    
                    if (!rating) {
                        showNotification('Please select a rating', 'error');
                        return;
                    }

                    const movieId = form.action.split('/movie/')[1].split('/')[0];
                    rateMovie(movieId, rating.value);
                });
            }
        });
    });
}

/**
 * Initialize search form
 */
function initializeSearchForm() {
    const searchForm = document.querySelector('.search-form');
    const searchInput = document.querySelector('.search-input');

    if (searchForm && searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchForm.submit();
            }
        });
    }
}

/**
 * Initialize navigation
 */
function initializeNavigation() {
    const navbar = document.querySelector('.navbar');
    
    // Add shadow on scroll
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.3)';
            navbar.style.backgroundColor = 'rgba(20, 20, 20, 0.95)';
        } else {
            navbar.style.boxShadow = 'none';
            navbar.style.backgroundColor = 'linear-gradient(180deg, rgba(20, 20, 20, 0.8) 0%, rgba(20, 20, 20, 0) 100%)';
        }
    });
}

/**
 * Lazy load images
 */
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}

/**
 * Smooth scroll to element
 */
function smoothScroll(target) {
    const element = document.querySelector(target);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// ==================== ANALYTICS ====================
/**
 * Track movie view
 */
function trackMovieView(movieId) {
    if (window.location.pathname.includes(`/movie/${movieId}/`)) {
        // Add analytics tracking here
        console.log(`Viewing movie: ${movieId}`);
    }
}

/**
 * Track search
 */
function trackSearch(query) {
    console.log(`Searched for: ${query}`);
}

// ==================== KEYBOARD SHORTCUTS ====================
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + K to focus search
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.focus();
        }
    }

    // Escape to close any open modals
    if (event.key === 'Escape') {
        closeAllModals();
    }
});

/**
 * Close all open modals
 */
function closeAllModals() {
    const modals = document.querySelectorAll('.modal.open');
    modals.forEach(modal => {
        modal.classList.remove('open');
    });
}

// ==================== PERFORMANCE ====================
/**
 * Debounce function for search input
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

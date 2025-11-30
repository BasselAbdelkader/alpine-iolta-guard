/**
 * TAMS API Client with Session Authentication (No JWT)
 * Uses Django session cookies instead of tokens
 */

class TAMSApiClient {
    constructor() {
        // Backend API base URL - use nginx proxy for same-origin requests
        this.baseURL = '/api';
        this.csrfToken = null;
    }

    /**
     * Get CSRF token from cookies
     */
    getCsrfToken() {
        const name = 'csrftoken';
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
     * Check if user is authenticated
     */
    async isAuthenticated() {
        try {
            const response = await fetch(`${this.baseURL}/auth/check/`, {
                credentials: 'include',
            });
            const data = await response.json();
            return data.authenticated === true;
        } catch (error) {
            return false;
        }
    }

    /**
     * Login with username and password
     */
    async login(username, password) {
        try {
            const response = await fetch(`${this.baseURL}/auth/login/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Login failed');
            }

            const data = await response.json();
            // Get CSRF token from cookie for future requests
            this.csrfToken = this.getCsrfToken();
            return data;
        } catch (error) {
            // console.error('Login error:', error);
            throw error;
        }
    }

    /**
     * Make authenticated API request
     */
    async request(endpoint, options = {}) {
        // Ensure endpoint starts with /
        if (!endpoint.startsWith('/')) {
            endpoint = '/' + endpoint;
        }

        const url = `${this.baseURL}${endpoint}`;

        // Prepare headers
        const headers = {
            ...options.headers,
        };

        // Add CSRF token for non-GET requests
        if (options.method && options.method !== 'GET') {
            const csrfToken = this.getCsrfToken();
            if (csrfToken) {
                headers['X-CSRFToken'] = csrfToken;
            }
        }

        // Add Content-Type for JSON requests
        if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
            headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(options.body);
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers,
                credentials: 'include', // Important: include cookies
            });

            // Handle 401/403 - redirect to login with return URL
            if (response.status === 401 || response.status === 403) {
                const returnUrl = encodeURIComponent(window.location.pathname);
                window.location.href = `/login?returnUrl=${returnUrl}`;
                throw new Error('Authentication required');
            }

            // Handle non-OK responses
            if (!response.ok) {
                const contentType = response.headers.get('content-type');
                let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
                let validationErrors = null;

                if (contentType && contentType.includes('application/json')) {
                    const errorData = await response.json();
                    // Store validation errors for proper frontend handling
                    validationErrors = errorData;

                    // Try to extract a clean error message
                    if (errorData.error) {
                        errorMessage = errorData.error;
                    } else if (errorData.detail) {
                        errorMessage = errorData.detail;
                    } else if (errorData.message) {
                        errorMessage = errorData.message;
                    } else {
                        // Check for DRF field validation errors: {field: ["message"]}
                        for (const field in errorData) {
                            if (Array.isArray(errorData[field]) && errorData[field].length > 0) {
                                errorMessage = errorData[field][0];
                                break;
                            } else if (typeof errorData[field] === 'string') {
                                errorMessage = errorData[field];
                                break;
                            }
                        }
                    }
                } else {
                    errorMessage = await response.text();
                }

                const error = new Error(errorMessage);
                error.validationErrors = validationErrors;
                error.status = response.status;
                throw error;
            }

            // Handle 204 No Content (successful delete with no body)
            if (response.status === 204) {
                return { success: true, message: 'Operation completed successfully' };
            }

            // Parse response based on content type
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }

        } catch (error) {
            // console.error('API request error:', error);
            throw error;
        }
    }

    /**
     * GET request
     */
    async get(endpoint, params = {}) {
        // Build query string
        const queryString = new URLSearchParams(params).toString();
        const url = queryString ? `${endpoint}?${queryString}` : endpoint;

        return this.request(url, {
            method: 'GET'
        });
    }

    /**
     * POST request
     */
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: data
        });
    }

    /**
     * PUT request
     */
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: data
        });
    }

    /**
     * PATCH request
     */
    async patch(endpoint, data) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: data
        });
    }

    /**
     * DELETE request
     */
    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }

    /**
     * BUG #11 FIX: Enhanced logout with back button prevention
     */
    async logout() {
        try {
            await this.post('/auth/logout/', {});
        } catch (error) {
            // console.error('Logout error:', error);
        }

        // Clear all session data
        sessionStorage.clear();
        localStorage.clear();

        // Mark as logged out
        sessionStorage.setItem('loggedOut', 'true');

        // Redirect and prevent back button (use replace to avoid history entry)
        window.location.replace('/html/login.html');
    }

    /**
     * Setup back button prevention for authenticated pages
     */
    setupPageProtection() {
        // Disable browser cache for this page
        if (window.history && window.history.pushState) {
            window.history.pushState(null, null, window.location.href);
            window.onpopstate = function() {
                window.history.pushState(null, null, window.location.href);
            };
        }

        // Check if user was just logged out
        if (sessionStorage.getItem('loggedOut') === 'true') {
            sessionStorage.removeItem('loggedOut');
            window.location.replace('/html/login.html');
            return false;
        }

        return true;
    }
}

// Create global API client instance
const api = new TAMSApiClient();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TAMSApiClient;
}

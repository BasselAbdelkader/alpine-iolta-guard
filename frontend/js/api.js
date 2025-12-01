/**
 * Simple API Client without authentication
 * Handles all API communication with the backend
 */

const api = {
    baseURL: '/api',

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
    },

    /**
     * Generic fetch wrapper
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;

        const defaultOptions = {
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
            },
        };

        // Add CSRF token for non-GET requests
        const csrfToken = this.getCsrfToken();
        if (csrfToken && options.method && options.method !== 'GET') {
            defaultOptions.headers['X-CSRFToken'] = csrfToken;
        }

        const config = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, config);

            // Handle non-JSON responses
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return await response.text();
            }

            const data = await response.json();

            if (!response.ok) {
                // Extract clean error message from DRF validation errors
                let errorMessage = `HTTP error! status: ${response.status}`;

                if (data.message) {
                    errorMessage = data.message;
                } else if (data.detail) {
                    errorMessage = data.detail;
                } else if (data.error) {
                    errorMessage = data.error;
                } else {
                    // Check for DRF field validation errors: {field: ["message"]}
                    for (const field in data) {
                        if (Array.isArray(data[field]) && data[field].length > 0) {
                            errorMessage = data[field][0];
                            break;
                        } else if (typeof data[field] === 'string') {
                            errorMessage = data[field];
                            break;
                        }
                    }
                }

                const error = new Error(errorMessage);
                error.validationErrors = data;
                error.status = response.status;
                throw error;
            }

            return data;
        } catch (error) {
            // console.error('API request failed:', error);
            throw error;
        }
    },

    /**
     * GET request
     */
    async get(endpoint) {
        return this.request(endpoint, {
            method: 'GET',
        });
    },

    /**
     * POST request
     */
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    /**
     * PUT request
     */
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    /**
     * PATCH request
     */
    async patch(endpoint, data) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    },

    /**
     * DELETE request
     */
    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE',
        });
    }
};

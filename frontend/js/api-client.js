/**
 * TAMS API Client with JWT Authentication
 * Handles all API communication with automatic token management
 */

class TAMSApiClient {
    constructor() {
        // Backend API base URL (proxied through Nginx)
        this.baseURL = '/api';

        // Token storage keys
        this.accessTokenKey = 'tams_access_token';
        this.refreshTokenKey = 'tams_refresh_token';
    }

    /**
     * Get stored access token
     */
    getAccessToken() {
        return localStorage.getItem(this.accessTokenKey);
    }

    /**
     * Get stored refresh token
     */
    getRefreshToken() {
        return localStorage.getItem(this.refreshTokenKey);
    }

    /**
     * Store authentication tokens
     */
    storeTokens(accessToken, refreshToken) {
        localStorage.setItem(this.accessTokenKey, accessToken);
        if (refreshToken) {
            localStorage.setItem(this.refreshTokenKey, refreshToken);
        }
    }

    /**
     * Clear authentication tokens (logout)
     */
    clearTokens() {
        localStorage.removeItem(this.accessTokenKey);
        localStorage.removeItem(this.refreshTokenKey);
    }

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!this.getAccessToken();
    }

    /**
     * Login with username and password
     */
    async login(username, password) {
        try {
            const response = await fetch(`${this.baseURL}/auth/token/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Login failed');
            }

            const data = await response.json();
            this.storeTokens(data.access, data.refresh);
            return data;
        } catch (error) {
            // console.error('Login error:', error);
            throw error;
        }
    }

    /**
     * Refresh access token using refresh token
     */
    async refreshAccessToken() {
        const refreshToken = this.getRefreshToken();

        if (!refreshToken) {
            throw new Error('No refresh token available');
        }

        try {
            const response = await fetch(`${this.baseURL}/auth/token/refresh/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ refresh: refreshToken })
            });

            if (!response.ok) {
                // Refresh token expired or invalid - user must login again
                this.clearTokens();
                window.location.href = '/html/login.html';
                throw new Error('Session expired. Please login again.');
            }

            const data = await response.json();
            this.storeTokens(data.access, data.refresh || refreshToken);
            return data.access;
        } catch (error) {
            // console.error('Token refresh error:', error);
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
        const accessToken = this.getAccessToken();

        // Prepare headers
        const headers = {
            ...options.headers,
        };

        // Add Authorization header if token exists
        if (accessToken) {
            headers['Authorization'] = `Bearer ${accessToken}`;
        }

        // Add Content-Type for JSON requests
        if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
            headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(options.body);
        }

        try {
            let response = await fetch(url, {
                ...options,
                headers,
                credentials: 'include', // Include cookies for session auth fallback
            });

            // If 401 Unauthorized, try refreshing token
            if (response.status === 401 && accessToken) {
                // console.log('Access token expired, refreshing...');
                await this.refreshAccessToken();

                // Retry request with new token
                const newAccessToken = this.getAccessToken();
                headers['Authorization'] = `Bearer ${newAccessToken}`;

                response = await fetch(url, {
                    ...options,
                    headers,
                    credentials: 'include',
                });
            }

            // Handle non-OK responses
            if (!response.ok) {
                const contentType = response.headers.get('content-type');
                let errorMessage = `HTTP ${response.status}: ${response.statusText}`;

                if (contentType && contentType.includes('application/json')) {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorData.message || JSON.stringify(errorData);
                } else {
                    errorMessage = await response.text();
                }

                throw new Error(errorMessage);
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
     * Logout (clear tokens)
     */
    logout() {
        this.clearTokens();
        window.location.href = '/html/login.html';
    }
}

// Create global API client instance
const api = new TAMSApiClient();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TAMSApiClient;
}

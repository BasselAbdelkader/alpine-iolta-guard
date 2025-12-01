/**
 * TAMS API Client Library
 * Professional JavaScript client for Trust Account Management System API
 * 
 * Usage:
 * const api = new TAMSApiClient();
 * await api.authenticate('username', 'password');
 * const clients = await api.getClients();
 */

class TAMSApiClient {
    constructor(baseUrl = '/api/v1', options = {}) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.accessToken = localStorage.getItem('tams_access_token');
        this.refreshToken = localStorage.getItem('tams_refresh_token');
        this.options = {
            timeout: 30000,
            retries: 3,
            retryDelay: 1000,
            debug: false,
            ...options
        };
        
        // Auto-authenticate if tokens exist
        if (this.accessToken && this.refreshToken) {
            this.validateTokens();
        }
    }

    /**
     * Authentication and token management
     */
    async validateTokens() {
        try {
            // Test current token
            await this.request('/clients/?page=1&page_size=1');
        } catch (error) {
            if (error.status === 401) {
                await this.refreshAccessToken();
            }
        }
    }

    setTokens(accessToken, refreshToken = null) {
        this.accessToken = accessToken;
        if (refreshToken) this.refreshToken = refreshToken;
        
        localStorage.setItem('tams_access_token', accessToken);
        if (refreshToken) localStorage.setItem('tams_refresh_token', refreshToken);
        
        this.log('Tokens updated successfully');
    }

    clearTokens() {
        this.accessToken = null;
        this.refreshToken = null;
        localStorage.removeItem('tams_access_token');
        localStorage.removeItem('tams_refresh_token');
        
        this.log('Tokens cleared');
    }

    getAuthHeaders() {
        const headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCSRFToken()
        };
        
        if (this.accessToken) {
            headers['Authorization'] = `Bearer ${this.accessToken}`;
        }
        
        return headers;
    }

    getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }

    async refreshAccessToken() {
        if (!this.refreshToken) {
            throw new APIError('No refresh token available', 401);
        }

        try {
            const response = await fetch(`${this.baseUrl}/auth/token/refresh/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ refresh: this.refreshToken })
            });

            if (response.ok) {
                const data = await response.json();
                this.setTokens(data.access, this.refreshToken);
                return data.access;
            } else {
                throw new APIError('Token refresh failed', response.status);
            }
        } catch (error) {
            this.clearTokens();
            throw error;
        }
    }

    /**
     * Core request method with retry logic and error handling
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            method: 'GET',
            headers: this.getAuthHeaders(),
            ...options
        };

        // Handle request body
        if (config.body && typeof config.body === 'object' && !(config.body instanceof FormData)) {
            config.body = JSON.stringify(config.body);
        }

        this.log(`Making ${config.method} request to ${url}`, config);

        let lastError;
        
        for (let attempt = 0; attempt < this.options.retries; attempt++) {
            try {
                let response = await fetch(url, config);

                // Handle 401 by attempting token refresh
                if (response.status === 401 && this.refreshToken && attempt === 0) {
                    this.log('Token expired, attempting refresh...');
                    await this.refreshAccessToken();
                    config.headers = this.getAuthHeaders();
                    response = await fetch(url, config);
                }

                if (response.ok) {
                    const contentType = response.headers.get('content-type');
                    const result = contentType && contentType.includes('application/json') ? 
                        await response.json() : await response.text();
                    
                    this.log(`Request successful:`, result);
                    return result;
                }

                // Handle error responses
                const errorData = await response.json().catch(() => ({}));
                throw new APIError(
                    errorData.detail || `Request failed with status ${response.status}`,
                    response.status,
                    response,
                    errorData
                );

            } catch (error) {
                lastError = error;
                
                if (error instanceof APIError) {
                    this.log('API Error:', error);
                    throw error;
                }
                
                // Retry on network errors
                if (attempt < this.options.retries - 1) {
                    this.log(`Attempt ${attempt + 1} failed, retrying in ${this.options.retryDelay}ms...`);
                    await new Promise(resolve => setTimeout(resolve, this.options.retryDelay * (attempt + 1)));
                    continue;
                }
            }
        }

        this.log('All retry attempts failed:', lastError);
        throw lastError;
    }

    /**
     * Authentication API
     */
    async authenticate(username, password) {
        try {
            const data = await this.request('/auth/token/', {
                method: 'POST',
                body: { username, password }
            });
            
            this.setTokens(data.access, data.refresh);
            return data;
        } catch (error) {
            this.clearTokens();
            throw error;
        }
    }

    async logout() {
        this.clearTokens();
        // Could call logout endpoint if implemented
        return true;
    }

    /**
     * Client Management API
     */
    async getClients(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? `/clients/?${queryString}` : '/clients/';
        return await this.request(endpoint);
    }

    async getClient(id) {
        return await this.request(`/clients/${id}/`);
    }

    async searchClients(query, limit = 20) {
        if (!query || query.length < 2) {
            throw new APIError('Search query must be at least 2 characters', 400);
        }
        const params = new URLSearchParams({ q: query, limit }).toString();
        return await this.request(`/clients/search/?${params}`);
    }

    async getClientBalanceHistory(id) {
        return await this.request(`/clients/${id}/balance_history/`);
    }

    async getClientCases(id, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? 
            `/clients/${id}/cases/?${queryString}` : 
            `/clients/${id}/cases/`;
        return await this.request(endpoint);
    }

    async getTrustSummary() {
        return await this.request('/clients/trust_summary/');
    }

    async createClient(clientData) {
        return await this.request('/clients/', {
            method: 'POST',
            body: clientData
        });
    }

    async updateClient(id, clientData) {
        return await this.request(`/clients/${id}/`, {
            method: 'PATCH',
            body: clientData
        });
    }

    /**
     * Case Management API
     */
    async getCases(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? `/cases/?${queryString}` : '/cases/';
        return await this.request(endpoint);
    }

    async getCase(id) {
        return await this.request(`/cases/${id}/`);
    }

    async getCasesByClient(clientId) {
        return await this.request(`/cases/by_client/?client_id=${clientId}`);
    }

    async getCaseTransactions(id) {
        return await this.request(`/cases/${id}/transactions/`);
    }

    async createCase(caseData) {
        return await this.request('/cases/', {
            method: 'POST',
            body: caseData
        });
    }

    async updateCase(id, caseData) {
        return await this.request(`/cases/${id}/`, {
            method: 'PATCH',
            body: caseData
        });
    }

    /**
     * Transaction Management API
     */
    async getTransactions(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? `/transactions/?${queryString}` : '/transactions/';
        return await this.request(endpoint);
    }

    async getTransaction(id) {
        return await this.request(`/transactions/${id}/`);
    }

    async searchTransactions(query, limit = 50) {
        if (!query || query.length < 2) {
            throw new APIError('Search query must be at least 2 characters', 400);
        }
        const params = new URLSearchParams({ q: query, limit }).toString();
        return await this.request(`/transactions/search/?${params}`);
    }

    async getMonthlyTransactionSummary(year = new Date().getFullYear()) {
        return await this.request(`/transactions/monthly_summary/?year=${year}`);
    }

    async getUnbalancedTransactions() {
        return await this.request('/transactions/unbalanced/');
    }

    async createTransaction(transactionData) {
        return await this.request('/transactions/', {
            method: 'POST',
            body: transactionData
        });
    }

    async voidTransaction(id, reason, voidedBy) {
        return await this.request(`/transactions/${id}/void/`, {
            method: 'POST',
            body: { void_reason: reason, voided_by: voidedBy }
        });
    }

    async clearTransaction(id) {
        return await this.request(`/transactions/${id}/clear/`, {
            method: 'POST'
        });
    }

    /**
     * Bank Account Management API
     */
    async getBankAccounts() {
        return await this.request('/bank-accounts/accounts/');
    }

    async getBankAccount(id) {
        return await this.request(`/bank-accounts/accounts/${id}/`);
    }

    async getBankAccountTransactions(id, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? 
            `/bank-accounts/accounts/${id}/transactions/?${queryString}` : 
            `/bank-accounts/accounts/${id}/transactions/`;
        return await this.request(endpoint);
    }

    async getBankAccountBalanceHistory(id) {
        return await this.request(`/bank-accounts/accounts/${id}/balance_history/`);
    }

    async getBankAccountsSummary() {
        return await this.request('/bank-accounts/accounts/summary/');
    }

    /**
     * Vendor Management API
     */
    async getVendors(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? `/vendors/vendors/?${queryString}` : '/vendors/vendors/';
        return await this.request(endpoint);
    }

    async getVendor(id) {
        return await this.request(`/vendors/vendors/${id}/`);
    }

    async searchVendors(query, limit = 10) {
        if (!query || query.length < 2) {
            throw new APIError('Search query must be at least 2 characters', 400);
        }
        const params = new URLSearchParams({ q: query, limit }).toString();
        return await this.request(`/vendors/vendors/search/?${params}`);
    }

    async getVendorPayments(id) {
        return await this.request(`/vendors/vendors/${id}/payments/`);
    }

    async createVendor(vendorData) {
        return await this.request('/vendors/vendors/', {
            method: 'POST',
            body: vendorData
        });
    }

    async getVendorTypes() {
        return await this.request('/vendors/vendor-types/');
    }

    /**
     * Utility methods
     */
    formatCurrency(amount, currency = 'USD') {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(parseFloat(amount) || 0);
    }

    formatDate(dateString, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            ...options
        };
        return new Intl.DateTimeFormat('en-US', defaultOptions).format(new Date(dateString));
    }

    formatDateTime(dateString) {
        return this.formatDate(dateString, {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    debounce(func, wait) {
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

    log(...args) {
        if (this.options.debug) {
            console.log('[TAMS API]', ...args);
        }
    }

    /**
     * Event system for real-time updates
     */
    on(event, callback) {
        if (!this.events) this.events = {};
        if (!this.events[event]) this.events[event] = [];
        this.events[event].push(callback);
    }

    off(event, callback) {
        if (!this.events || !this.events[event]) return;
        this.events[event] = this.events[event].filter(cb => cb !== callback);
    }

    emit(event, data) {
        if (!this.events || !this.events[event]) return;
        this.events[event].forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error('Event callback error:', error);
            }
        });
    }

    /**
     * Batch operations for efficiency
     */
    async batch(operations) {
        const results = await Promise.allSettled(
            operations.map(op => this.request(op.endpoint, op.options))
        );
        
        return results.map((result, index) => ({
            operation: operations[index],
            success: result.status === 'fulfilled',
            data: result.status === 'fulfilled' ? result.value : null,
            error: result.status === 'rejected' ? result.reason : null
        }));
    }
}

/**
 * Custom API Error class
 */
class APIError extends Error {
    constructor(message, status = 500, response = null, data = {}) {
        super(message);
        this.name = 'APIError';
        this.status = status;
        this.response = response;
        this.data = data;
    }

    get isAuthError() {
        return this.status === 401;
    }

    get isValidationError() {
        return this.status === 400;
    }

    get isForbidden() {
        return this.status === 403;
    }

    get isNotFound() {
        return this.status === 404;
    }

    toString() {
        return `${this.name}: ${this.message} (Status: ${this.status})`;
    }
}

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TAMSApiClient, APIError };
}

// Create global instance
if (typeof window !== 'undefined') {
    window.TAMSApiClient = TAMSApiClient;
    window.APIError = APIError;
    
    // Create default instance
    window.tamsAPI = new TAMSApiClient();
    
    // Debug mode from localStorage
    if (localStorage.getItem('tams_debug') === 'true') {
        window.tamsAPI.options.debug = true;
    }
    
    console.log('TAMS API Client loaded successfully');
}
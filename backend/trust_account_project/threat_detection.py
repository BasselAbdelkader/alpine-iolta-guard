"""
TAMS Advanced Threat Detection System
Real-time detection and response to sophisticated attacks
"""

import time
import json
import logging
import hashlib
import re
from datetime import datetime, timedelta
from collections import defaultdict, deque
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import SuspiciousOperation
from django.http import JsonResponse, HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.signals import user_login_failed, user_logged_in
from django.dispatch import receiver
from django.db import connection
from trust_account_project.validators import SQLInjectionValidator  # SECURITY FIX M3
import ipaddress

logger = logging.getLogger(__name__)

class AdvancedThreatDetectionMiddleware(MiddlewareMixin):
    """
    Advanced threat detection and response system
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Threat detection configuration
        # SECURITY FIX M3: SQL injection patterns now from centralized SQLInjectionValidator
        self.threat_patterns = {
            'sql_injection': SQLInjectionValidator.PATTERNS,  # Use centralized patterns
            'xss_attempts': [
                r'<script[^>]*>',
                r'javascript:',
                r'vbscript:',
                r'on\w+\s*=',
                r'<iframe[^>]*>',
                r'<object[^>]*>',
                r'<embed[^>]*>',
                r'eval\s*\(',
                r'alert\s*\(',
                r'document\.cookie',
                r'document\.write',
            ],
            'path_traversal': [
                r'\.\./\.\.',
                r'\.\.\\\.\.\\',
                r'/etc/passwd',
                r'/etc/shadow',
                r'windows\\system32',
                r'..\\windows',
                r'../usr',
            ],
            'command_injection': [
                r';\s*rm\s+',
                r';\s*cat\s+',
                r';\s*ls\s+',
                r';\s*wget\s+',
                r';\s*curl\s+',
                r'\|\s*nc\s+',
                r'`.*`',
                r'\$\(.*\)',
                r';\s*id\s*;',
            ]
        }
        
        # Behavioral anomaly thresholds
        self.anomaly_thresholds = {
            'requests_per_minute': 100,
            'unique_params_per_hour': 500,
            'error_rate_threshold': 0.50,  # 50% error rate
            'suspicious_pattern_count': 3,
        }
        
        # Known attack signatures
        self.attack_signatures = {
            'bot_patterns': [
                r'sqlmap',
                r'nmap',
                r'nikto',
                r'gobuster',
                r'dirbuster',
                r'burpsuite',
                r'acunetix',
                r'nessus',
            ],
            'suspicious_user_agents': [
                r'python-requests',
                r'curl/',
                r'wget/',
                r'scanner',
                r'bot',
                r'crawler',
                r'spider',
            ]
        }
        
        super().__init__(get_response)
    
    def process_request(self, request):
        """Analyze request for threats"""
        
        client_ip = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Check if IP is already blocked
        if self.is_ip_blocked(client_ip):
            logger.error(f"THREAT: Blocked IP attempted access: {client_ip}")
            return self.threat_response('Access denied', 403)
        
        # Threat analysis
        threat_score = 0
        detected_threats = []
        
        # 1. Pattern-based detection
        pattern_threats = self.detect_attack_patterns(request)
        threat_score += len(pattern_threats) * 10
        detected_threats.extend(pattern_threats)
        
        # 2. Behavioral anomaly detection
        behavioral_threats = self.detect_behavioral_anomalies(request, client_ip)
        threat_score += len(behavioral_threats) * 5
        detected_threats.extend(behavioral_threats)
        
        # 3. Signature-based detection
        signature_threats = self.detect_attack_signatures(request)
        threat_score += len(signature_threats) * 8
        detected_threats.extend(signature_threats)
        
        # 4. Geographic and time-based analysis
        geo_threats = self.detect_geographic_anomalies(request, client_ip)
        threat_score += len(geo_threats) * 3
        detected_threats.extend(geo_threats)
        
        # 5. Session-based threat detection
        session_threats = self.detect_session_anomalies(request)
        threat_score += len(session_threats) * 7
        detected_threats.extend(session_threats)
        
        # Record threat intelligence
        self.record_threat_intelligence(client_ip, user_agent, threat_score, detected_threats)
        
        # Response based on threat level
        if threat_score >= 50:  # Critical threat
            self.block_ip(client_ip, duration=3600)  # 1 hour block
            logger.critical(f"THREAT: Critical threat detected from {client_ip}: Score {threat_score}, Threats: {detected_threats}")
            return self.threat_response('Suspicious activity detected', 403)
        
        elif threat_score >= 20:  # High threat
            logger.error(f"THREAT: High threat detected from {client_ip}: Score {threat_score}, Threats: {detected_threats}")
            # Add to watchlist but allow request
            self.add_to_watchlist(client_ip)
        
        elif threat_score >= 10:  # Medium threat
            logger.warning(f"THREAT: Medium threat detected from {client_ip}: Score {threat_score}, Threats: {detected_threats}")
        
        return None
    
    def detect_attack_patterns(self, request):
        """Detect attack patterns in request"""
        detected_patterns = []
        
        # Get all request data
        all_data = {}
        all_data.update(request.GET.dict())
        all_data.update(request.POST.dict())
        
        # Include request path and headers
        all_data['__path__'] = request.path
        all_data['__user_agent__'] = request.META.get('HTTP_USER_AGENT', '')
        all_data['__referer__'] = request.META.get('HTTP_REFERER', '')
        
        # Check body for JSON data
        # BUG FIX: Skip body access for file uploads (multipart/form-data)
        # Django reads request.FILES first, making request.body inaccessible
        # Check content_type BEFORE accessing body (hasattr triggers access!)
        content_type = getattr(request, 'content_type', '')
        if content_type.startswith('application/json'):
            try:
                body_data = json.loads(request.body.decode('utf-8'))
                if isinstance(body_data, dict):
                    all_data.update(body_data)
            except:
                pass
        
        # Check each pattern category
        for pattern_type, patterns in self.threat_patterns.items():
            for pattern in patterns:
                for key, value in all_data.items():
                    if isinstance(value, str):
                        if re.search(pattern, value, re.IGNORECASE):
                            detected_patterns.append(f"{pattern_type}:{pattern}")
        
        return detected_patterns
    
    def detect_behavioral_anomalies(self, request, client_ip):
        """Detect behavioral anomalies"""
        anomalies = []
        
        # Request frequency analysis
        minute_key = f"requests_per_minute_{client_ip}_{int(time.time() // 60)}"
        requests_this_minute = cache.get(minute_key, 0) + 1
        cache.set(minute_key, requests_this_minute, 60)
        
        if requests_this_minute > self.anomaly_thresholds['requests_per_minute']:
            anomalies.append('excessive_request_rate')
        
        # Parameter diversity analysis
        hour_key = f"unique_params_{client_ip}_{int(time.time() // 3600)}"
        # Get param_set from cache (stored as list for JSON serialization)
        param_list = cache.get(hour_key, [])
        param_set = set(param_list)  # Convert list back to set

        # Add current parameters to set
        current_params = set()
        current_params.update(request.GET.keys())
        current_params.update(request.POST.keys())

        param_set.update(current_params)
        # Store as list for Redis JSON serialization
        cache.set(hour_key, list(param_set), 3600)
        
        if len(param_set) > self.anomaly_thresholds['unique_params_per_hour']:
            anomalies.append('parameter_enumeration')
        
        # Error rate analysis
        error_key = f"error_rate_{client_ip}"
        error_data = cache.get(error_key, {'total': 0, 'errors': 0})
        error_data['total'] += 1
        
        # This will be updated in process_response if there's an error
        cache.set(error_key, error_data, 3600)
        
        if error_data['total'] > 10:  # Only analyze after 10+ requests
            error_rate = error_data['errors'] / error_data['total']
            if error_rate > self.anomaly_thresholds['error_rate_threshold']:
                anomalies.append('high_error_rate')
        
        return anomalies
    
    def detect_attack_signatures(self, request):
        """Detect known attack tool signatures"""
        signatures = []
        
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        
        # Check for bot patterns
        for pattern in self.attack_signatures['bot_patterns']:
            if re.search(pattern, user_agent, re.IGNORECASE):
                signatures.append(f"bot_signature:{pattern}")
        
        # Check for suspicious user agents
        for pattern in self.attack_signatures['suspicious_user_agents']:
            if re.search(pattern, user_agent, re.IGNORECASE):
                signatures.append(f"suspicious_ua:{pattern}")
        
        # Check for unusual request patterns
        if request.method in ['POST', 'PUT'] and not request.content_type:
            signatures.append('missing_content_type')
        
        # Check for suspicious headers
        suspicious_headers = [
            'X-Forwarded-For',
            'X-Originating-IP', 
            'X-Remote-IP',
            'X-Cluster-Client-IP'
        ]
        
        header_count = sum(1 for header in suspicious_headers if request.META.get(f'HTTP_{header.upper().replace("-", "_")}'))
        if header_count > 2:
            signatures.append('header_manipulation')
        
        return signatures
    
    def detect_geographic_anomalies(self, request, client_ip):
        """Detect geographic and temporal anomalies"""
        anomalies = []
        
        try:
            # Basic IP validation
            ip_obj = ipaddress.ip_address(client_ip)
            
            # Check for private/local IPs making external-like requests
            if ip_obj.is_private and request.META.get('HTTP_HOST', '').lower() not in ['localhost', '127.0.0.1']:
                anomalies.append('private_ip_external_request')
        
        except ValueError:
            anomalies.append('invalid_ip_format')
        
        # Time-based analysis
        current_hour = datetime.now().hour
        
        # Unusual hours for business application (optional)
        if current_hour < 5 or current_hour > 23:
            # Check if this user typically accesses during these hours
            unusual_time_key = f"unusual_time_{client_ip}"
            unusual_count = cache.get(unusual_time_key, 0)
            if unusual_count > 10:  # Regular off-hours user
                pass
            else:
                cache.set(unusual_time_key, unusual_count + 1, 86400)  # 24 hours
                anomalies.append('unusual_access_time')
        
        return anomalies
    
    def detect_session_anomalies(self, request):
        """Detect session-based anomalies"""
        anomalies = []

        # SECURITY FIX: Check if user attribute exists before accessing
        if not hasattr(request, 'user'):
            return []  # AuthenticationMiddleware hasn't run yet

        if hasattr(request, 'session') and request.user.is_authenticated:
            # Session hijacking indicators
            session_ip = request.session.get('_threat_detection_ip')
            current_ip = self.get_client_ip(request)
            
            if session_ip and session_ip != current_ip:
                anomalies.append('session_ip_change')
            else:
                request.session['_threat_detection_ip'] = current_ip
            
            # Session age validation
            session_start = request.session.get('_threat_detection_start')
            if not session_start:
                request.session['_threat_detection_start'] = time.time()
            else:
                session_age = time.time() - session_start
                if session_age > 28800:  # 8 hours
                    anomalies.append('stale_session')
            
            # Concurrent session detection
            user_sessions_key = f"user_sessions_{request.user.id}"
            # Get from cache as list, convert to set for operations
            user_sessions_list = cache.get(user_sessions_key, [])
            user_sessions = set(user_sessions_list)
            current_session = request.session.session_key

            if current_session:
                user_sessions.add(current_session)
                # Convert set back to list for Redis JSON serialization
                cache.set(user_sessions_key, list(user_sessions), 3600)

                if len(user_sessions) > 3:  # More than 3 concurrent sessions
                    anomalies.append('multiple_concurrent_sessions')
        
        return anomalies
    
    def record_threat_intelligence(self, client_ip, user_agent, threat_score, detected_threats):
        """Record threat intelligence for analysis"""
        
        # Store in cache for immediate access
        threat_data = {
            'timestamp': time.time(),
            'ip': client_ip,
            'user_agent': user_agent,
            'threat_score': threat_score,
            'threats': detected_threats,
        }
        
        # Add to threat history
        history_key = f"threat_history_{client_ip}"
        history = cache.get(history_key, [])
        history.append(threat_data)
        
        # Keep only last 100 entries
        if len(history) > 100:
            history = history[-100:]
        
        cache.set(history_key, history, 86400)  # 24 hours
        
        # Global threat tracking
        if threat_score > 0:
            global_threats_key = "global_threats"
            global_threats = cache.get(global_threats_key, [])
            global_threats.append(threat_data)
            
            # Keep only last 1000 global threats
            if len(global_threats) > 1000:
                global_threats = global_threats[-1000:]
            
            cache.set(global_threats_key, global_threats, 86400)
    
    def process_response(self, request, response):
        """Update threat intelligence based on response"""
        
        client_ip = self.get_client_ip(request)
        
        # Update error rate tracking
        error_key = f"error_rate_{client_ip}"
        error_data = cache.get(error_key, {'total': 0, 'errors': 0})
        
        if response.status_code >= 400:
            error_data['errors'] += 1
            cache.set(error_key, error_data, 3600)
        
        return response
    
    def block_ip(self, ip, duration=3600):
        """Block IP address"""
        cache_key = f"blocked_ip_{ip}"
        cache.set(cache_key, time.time() + duration, duration)
        
        # Log security incident
        logger.critical(f"SECURITY: IP {ip} blocked for {duration} seconds due to threat detection")
    
    def is_ip_blocked(self, ip):
        """Check if IP is blocked"""
        cache_key = f"blocked_ip_{ip}"
        block_until = cache.get(cache_key)
        return block_until and time.time() < block_until
    
    def add_to_watchlist(self, ip):
        """Add IP to watchlist for monitoring"""
        watchlist_key = "security_watchlist"
        # Get from cache as list, convert to set for operations
        watchlist_list = cache.get(watchlist_key, [])
        watchlist = set(watchlist_list)
        watchlist.add(ip)
        # Convert set back to list for Redis JSON serialization
        cache.set(watchlist_key, list(watchlist), 86400)  # 24 hours
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or 'unknown'
    
    def threat_response(self, message, status_code):
        """Create threat response"""
        return JsonResponse({
            'error': message,
            'code': 'threat_detected',
            'status': status_code
        }, status=status_code)


class ThreatIntelligenceManager:
    """
    Manage threat intelligence data and analysis
    """
    
    @staticmethod
    def get_threat_summary():
        """Get threat intelligence summary"""
        global_threats = cache.get("global_threats", [])
        
        # Analyze threats from last 24 hours
        current_time = time.time()
        recent_threats = [
            threat for threat in global_threats 
            if current_time - threat['timestamp'] < 86400
        ]
        
        # Count threat types
        threat_counts = defaultdict(int)
        ip_counts = defaultdict(int)
        
        for threat in recent_threats:
            ip_counts[threat['ip']] += 1
            for threat_type in threat['threats']:
                threat_counts[threat_type] += 1
        
        return {
            'total_threats': len(recent_threats),
            'unique_ips': len(ip_counts),
            'top_threat_types': dict(sorted(threat_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            'top_threat_ips': dict(sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
        }
    
    @staticmethod
    def get_ip_threat_profile(ip):
        """Get threat profile for specific IP"""
        history_key = f"threat_history_{ip}"
        history = cache.get(history_key, [])
        
        if not history:
            return None
        
        total_score = sum(threat['threat_score'] for threat in history)
        threat_types = []
        for threat in history:
            threat_types.extend(threat['threats'])
        
        threat_type_counts = defaultdict(int)
        for threat_type in threat_types:
            threat_type_counts[threat_type] += 1
        
        return {
            'ip': ip,
            'total_incidents': len(history),
            'total_threat_score': total_score,
            'average_threat_score': total_score / len(history),
            'first_seen': min(threat['timestamp'] for threat in history),
            'last_seen': max(threat['timestamp'] for threat in history),
            'threat_types': dict(threat_type_counts),
        }


# Signal handlers for additional threat detection
@receiver(user_login_failed)
def detect_login_threats(sender, credentials, request, **kwargs):
    """Detect threats in failed login attempts"""
    client_ip = request.META.get('REMOTE_ADDR', 'unknown')
    username = credentials.get('username', 'unknown')
    
    # Check for suspicious login patterns
    suspicious_indicators = []
    
    # SQL injection in username
    sql_patterns = [
        r"admin'\s*--",
        r"'\s*or\s*'1'\s*=\s*'1",
        r"union\s+select",
        r"drop\s+table",
    ]
    
    for pattern in sql_patterns:
        if re.search(pattern, username, re.IGNORECASE):
            suspicious_indicators.append(f"sql_injection_login:{pattern}")
    
    # Common attack usernames
    attack_usernames = [
        'admin', 'administrator', 'root', 'test', 'guest', 'user',
        'sa', 'postgres', 'mysql', 'oracle', 'demo'
    ]
    
    if username.lower() in attack_usernames:
        suspicious_indicators.append("common_attack_username")
    
    if suspicious_indicators:
        logger.warning(f"THREAT: Suspicious login attempt from {client_ip} - Username: {username}, Indicators: {suspicious_indicators}")
        
        # Record threat intelligence
        threat_data = {
            'timestamp': time.time(),
            'ip': client_ip,
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'threat_score': len(suspicious_indicators) * 5,
            'threats': suspicious_indicators,
        }
        
        # Add to threat history
        history_key = f"threat_history_{client_ip}"
        history = cache.get(history_key, [])
        history.append(threat_data)
        cache.set(history_key, history, 86400)


@receiver(user_logged_in)
def detect_successful_login_threats(sender, user, request, **kwargs):
    """Detect threats in successful logins"""
    client_ip = request.META.get('REMOTE_ADDR', 'unknown')
    
    # Check login timing patterns
    current_time = datetime.now()
    
    # Check for unusual login times
    if current_time.hour < 5 or current_time.hour > 23:
        logger.info(f"SECURITY: Off-hours login by {user} from {client_ip}")
    
    # Check for geographic anomalies (basic)
    last_login_ip = cache.get(f"last_login_ip_{user.id}")
    if last_login_ip and last_login_ip != client_ip:
        logger.info(f"SECURITY: IP change for user {user}: {last_login_ip} -> {client_ip}")
    
    cache.set(f"last_login_ip_{user.id}", client_ip, 86400)
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from datetime import datetime
import time

class CommunicationAgent:
    """
    Communication Agent: Handles all notifications, alerts, and advisory communications
    Supports SMS, Email, API notifications, and WebSocket real-time updates
    """

    def __init__(self):
        self.notification_channels = {
            'email': self.send_email,
            'sms': self.send_sms,
            'api': self.send_api_notification,
            'websocket': self.send_websocket_update
        }

        self.templates = {
            'staff_alert': "URGENT: {message}. Action required: {actions}",
            'supply_alert': "SUPPLY ALERT: {message}. Procurement needed: {details}",
            'patient_advisory': "HEALTH ADVISORY: {message}. Precautions: {precautions}",
            'capacity_alert': "CAPACITY ALERT: {message}. Emergency protocols activated."
        }

    def send_notification(self, task):
        """Send notification through appropriate channel"""
        channel = task.get('channel', 'email')
        if channel in self.notification_channels:
            try:
                result = self.notification_channels[channel](task)
                self.log_notification(task, result)
                return result
            except Exception as e:
                return {'status': 'error', 'error': str(e)}
        else:
            return {'status': 'error', 'error': 'Unsupported channel'}

    def send_email(self, task):
        """Send email notification"""
        try:
            # Mock email sending - in production, use actual SMTP
            recipients = task.get('recipients', [])
            subject = task.get('subject', 'Hospital Alert')
            message = self.format_message(task)

            # Simulate email sending
            print(f"Sending email to {recipients}: {subject}")
            print(f"Message: {message}")

            return {
                'status': 'success',
                'channel': 'email',
                'recipients': recipients,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def send_sms(self, task):
        """Send SMS notification using Twilio-like service"""
        try:
            # Mock SMS sending
            recipients = task.get('recipients', [])
            message = self.format_message(task)

            print(f"Sending SMS to {recipients}: {message}")

            return {
                'status': 'success',
                'channel': 'sms',
                'recipients': recipients,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def send_api_notification(self, task):
        """Send notification via API/webhook"""
        try:
            webhook_url = task.get('webhook_url', 'http://mock-webhook.com/notify')
            payload = {
                'type': task.get('type'),
                'message': self.format_message(task),
                'timestamp': datetime.now().isoformat(),
                'priority': task.get('priority', 'medium')
            }

            # Mock API call
            print(f"Sending API notification to {webhook_url}: {payload}")

            return {
                'status': 'success',
                'channel': 'api',
                'webhook_url': webhook_url,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def send_websocket_update(self, task):
        """Send real-time update via WebSocket"""
        try:
            # Mock WebSocket update - in production, use socket.io or similar
            message = {
                'type': 'realtime_update',
                'data': task,
                'timestamp': datetime.now().isoformat()
            }

            print(f"Sending WebSocket update: {message}")

            return {
                'status': 'success',
                'channel': 'websocket',
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def format_message(self, task):
        """Format message using templates"""
        template_type = task.get('type', 'staff_alert')
        template = self.templates.get(template_type, "{message}")

        return template.format(
            message=task.get('message', ''),
            actions=', '.join(task.get('actions_required', [])),
            details=task.get('procurement_details', ''),
            precautions=task.get('precautions', '')
        )

    def create_patient_advisory(self, risk_data):
        """Create and send patient advisories"""
        advisories = []

        risks = risk_data.get('risks', [])
        environmental_data = risk_data.get('environmental_data', {})

        if 'pollution_high' in risks:
            advisory = {
                'type': 'patient_advisory',
                'title': 'Air Quality Alert',
                'message': f'Air quality is poor (AQI: {environmental_data.get("pollution", {}).get("aqi", 0)}). Respiratory patients should stay indoors.',
                'precautions': ['Wear N95 masks', 'Avoid outdoor activities', 'Keep windows closed', 'Use air purifiers'],
                'target_audience': ['respiratory_patients', 'elderly', 'children'],
                'channels': ['public_website', 'sms', 'email']
            }
            advisories.append(advisory)

        if 'festival_crowd' in risks:
            advisory = {
                'type': 'patient_advisory',
                'title': 'Festival Health Advisory',
                'message': 'Large crowds expected during upcoming festival. Take extra precautions.',
                'precautions': ['Avoid crowded areas', 'Maintain social distance', 'Carry medications', 'Stay hydrated'],
                'target_audience': ['general_public', 'chronic_patients'],
                'channels': ['public_website', 'social_media']
            }
            advisories.append(advisory)

        if 'epidemic_risk' in risks:
            advisory = {
                'type': 'patient_advisory',
                'title': 'Health Epidemic Alert',
                'message': f'Increased health risks detected. {environmental_data.get("epidemic", {}).get("active_cases", 0)} active cases reported.',
                'precautions': ['Practice hygiene', 'Get vaccinated', 'Wear masks in public', 'Avoid unnecessary travel'],
                'target_audience': ['general_public'],
                'channels': ['public_website', 'sms', 'tv_broadcast']
            }
            advisories.append(advisory)

        # Send advisories through multiple channels
        for advisory in advisories:
            for channel in advisory.get('channels', ['public_website']):
                task = {
                    'type': advisory['type'],
                    'channel': channel,
                    'subject': advisory['title'],
                    'message': advisory['message'],
                    'precautions': advisory['precautions'],
                    'target_audience': advisory['target_audience']
                }
                self.send_notification(task)

        return advisories

    def create_staff_notifications(self, staffing_plan):
        """Create and send staff notifications"""
        notifications = []

        for day_plan in staffing_plan:
            if day_plan['extra_doctors'] > 0 or day_plan['extra_nurses'] > 0:
                notification = {
                    'type': 'staff_alert',
                    'channel': 'email',
                    'subject': f'Staff Augmentation Required - {day_plan["date"]}',
                    'message': f'Additional staff needed: {day_plan["extra_doctors"]} doctors, {day_plan["extra_nurses"]} nurses',
                    'actions_required': ['report_for_duty', 'overtime_available' if day_plan.get('overtime_doctors') else None],
                    'recipients': ['doctors', 'nurses', 'hr_department'],
                    'priority': 'high' if day_plan['extra_doctors'] > 5 else 'medium'
                }

                self.send_notification(notification)
                notifications.append(notification)

        return notifications

    def create_supply_alerts(self, supply_plan):
        """Create and send supply procurement alerts"""
        alerts = []

        for day_plan in supply_plan:
            if day_plan['procurement']:
                alert = {
                    'type': 'supply_alert',
                    'channel': 'email',
                    'subject': f'Urgent Supply Procurement - {day_plan["date"]}',
                    'message': f'Critical supplies needed: {day_plan["procurement"]}',
                    'procurement_details': day_plan['procurement'],
                    'actions_required': ['contact_suppliers', 'arrange_delivery'],
                    'recipients': ['procurement_team', 'inventory_manager', 'hospital_admin'],
                    'priority': 'high' if 'oxygen_cylinders' in day_plan['procurement'] else 'medium'
                }

                self.send_notification(alert)
                alerts.append(alert)

        return alerts

    def broadcast_emergency_alert(self, emergency_data):
        """Broadcast emergency alerts through all channels"""
        alert = {
            'type': 'capacity_alert',
            'channel': 'all',  # Send through all channels
            'subject': 'EMERGENCY HOSPITAL CAPACITY ALERT',
            'message': f'Critical capacity situation: {emergency_data.get("message", "")}',
            'actions_required': emergency_data.get('actions', []),
            'recipients': ['all_staff', 'emergency_services', 'nearby_hospitals'],
            'priority': 'critical'
        }

        # Send through multiple channels
        channels = ['email', 'sms', 'api', 'websocket']
        results = []

        for channel in channels:
            alert_copy = alert.copy()
            alert_copy['channel'] = channel
            result = self.send_notification(alert_copy)
            results.append(result)

        return results

    def log_notification(self, task, result):
        """Log all notifications for audit trail"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'task': task,
            'result': result,
            'status': result.get('status', 'unknown')
        }

        # Mock logging - in production, use proper logging system
        with open('logs/communication_log.json', 'a') as f:
            json.dump(log_entry, f)
            f.write('\n')

    def get_notification_history(self, hours=24):
        """Retrieve notification history"""
        try:
            with open('logs/communication_log.json', 'r') as f:
                logs = [json.loads(line) for line in f.readlines()]

            # Filter by time
            cutoff_time = datetime.now().timestamp() - (hours * 3600)
            recent_logs = [log for log in logs if datetime.fromisoformat(log['timestamp']).timestamp() > cutoff_time]

            return recent_logs

        except FileNotFoundError:
            return []

    def get_delivery_stats(self):
        """Get notification delivery statistics"""
        history = self.get_notification_history(168)  # Last 7 days

        stats = {
            'total_sent': len(history),
            'successful': len([h for h in history if h['result'].get('status') == 'success']),
            'failed': len([h for h in history if h['result'].get('status') == 'error']),
            'by_channel': {}
        }

        for log in history:
            channel = log['task'].get('channel', 'unknown')
            if channel not in stats['by_channel']:
                stats['by_channel'][channel] = 0
            stats['by_channel'][channel] += 1

        return stats

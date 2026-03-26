"""
log_parser.py
الدور: تحليل سجلات Apache/Nginx (access.log)
المدخل: محتوى ملف السجل
المخرج: قائمة بالطلبات المحللة
"""

import re
from collections import defaultdict

class LogParser:
    """تحليل سجلات Apache/Nginx"""
    
    def __init__(self):
        # نمط Apache/Nginx log
        # مثال: 192.168.1.1 - - [25/Mar/2024:10:00:00] "GET /index.html HTTP/1.1" 200 1024
        self.log_pattern = r'(\d+\.\d+\.\d+\.\d+) - - \[(.*?)\] "(.*?)" (\d+) (\d+)'
    
    def parse_line(self, line):
        """
        تحليل سطر واحد من السجل
        المدخل: line - سطر من access.log
        المخرج: قاموس يحتوي على المعلومات أو None إذا لم يتطابق
        """
        match = re.search(self.log_pattern, line)
        
        if match:
            return {
                'ip': match.group(1),           # عنوان IP
                'time': match.group(2),         # الوقت
                'request': match.group(3),      # الطلب (GET /page.php?id=1)
                'status': int(match.group(4)),  # حالة الاستجابة (200, 404, 500)
                'size': int(match.group(5)),    # حجم الرد
                'raw': line                      # السطر الأصلي
            }
        return None
    
    def parse_file(self, content):
        """
        تحليل محتوى ملف السجل بالكامل
        المدخل: content - محتوى ملف access.log
        المخرج: قائمة من الطلبات المحللة
        """
        lines = content.strip().split('\n')
        parsed_requests = []
        
        for line in lines:
            if line.strip():
                parsed = self.parse_line(line)
                if parsed:
                    parsed_requests.append(parsed)
        
        return parsed_requests
    
    def group_by_ip(self, requests):
        """
        تجميع الطلبات حسب عنوان IP
        المدخل: requests - قائمة الطلبات المحللة
        المخرج: قاموس {ip: [قائمة الطلبات]}
        """
        grouped = defaultdict(list)
        for req in requests:
            grouped[req['ip']].append(req)
        return grouped
    
    def get_timeline(self, requests):
        """
        ترتيب الطلبات حسب الوقت (من الأقدم إلى الأحدث)
        المدخل: requests - قائمة الطلبات المحللة
        المخرج: قائمة مرتبة حسب الوقت
        """
        return sorted(requests, key=lambda x: x['time'])
    
    def get_error_requests(self, requests):
        """
        استخراج الطلبات التي أعطت أخطاء (status 4xx أو 5xx)
        """
        return [req for req in requests if req['status'] >= 400]
    
    def get_success_requests(self, requests):
        """
        استخراج الطلبات الناجحة (status 2xx)
        """
        return [req for req in requests if 200 <= req['status'] < 300]


# اختبار سريع
if __name__ == '__main__':
    parser = LogParser()
    
    # مثال لسجل
    sample = '192.168.1.1 - - [25/Mar/2024:10:00:00 +0000] "GET /index.html HTTP/1.1" 200 1024'
    
    result = parser.parse_line(sample)
    print(f"نتيجة التحليل:")
    print(f"  IP: {result['ip']}")
    print(f"  الوقت: {result['time']}")
    print(f"  الطلب: {result['request']}")
    print(f"  الحالة: {result['status']}")
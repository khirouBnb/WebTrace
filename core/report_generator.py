"""
report_generator.py
الدور: إنشاء تقارير الطب الشرعي
المدخل: معلومات القضية ونتائج التحليل
المخرج: تقرير منسق
"""

from datetime import datetime
import json
import os

class ReportGenerator:
    """إنشاء تقارير الطب الشرعي"""
    
    def __init__(self, reports_path='reports'):
        self.reports_path = reports_path
        
        # إنشاء مجلد التقارير إذا لم يكن موجوداً
        if not os.path.exists(reports_path):
            os.makedirs(reports_path)
    
    def generate_report(self, case_info, analysis_results):
        """
        إنشاء تقرير كامل
        المدخل:
            case_info: قاموس يحتوي على معلومات القضية
            analysis_results: قاموس يحتوي على نتائج التحليل
        المخرج: قاموس التقرير
        """
        # إنشاء معرف فريد للتقرير
        report_id = f"FOR-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # حساب مستوى الخطورة
        risk_level = self._calculate_risk_level(analysis_results)
        
        # حساب نسبة الهجمات
        total_requests = analysis_results.get('total_requests', 0)
        total_attacks = analysis_results.get('total_attacks', 0)
        attack_rate = (total_attacks / max(total_requests, 1)) * 100
        
        # بناء التقرير
        report = {
            'report_id': report_id,
            'generated_at': datetime.now().isoformat(),
            'results': analysis_results,  # حفظ النتائج كاملة لضمان عرضها في التقرير
            'case_info': case_info,
            'summary': {
                'total_requests': total_requests,
                'total_attacks': total_attacks,
                'attack_rate': attack_rate,
                'risk_level': risk_level,
                'main_attacker_ip': self._get_main_attacker(analysis_results),
                'unique_attackers': len(analysis_results.get('suspicious_ips', []))
            },
            'attacks': analysis_results.get('attacks', [])[:50],  # آخر 50 هجوم
            'suspicious_ips': analysis_results.get('suspicious_ips', [])[:10],  # أعلى 10 IPs
            'attack_types': self._get_attack_types_stats(analysis_results),
            'recommendations': self._get_recommendations(analysis_results)
        }
        
        # حفظ التقرير في ملف
        self._save_report(report)
        
        return report
    
    def _calculate_risk_level(self, results):
        """حساب مستوى الخطورة"""
        total_attacks = results.get('total_attacks', 0)
        
        if total_attacks > 100:
            return 'CRITICAL'
        elif total_attacks > 50:
            return 'HIGH'
        elif total_attacks > 10:
            return 'MEDIUM'
        elif total_attacks > 0:
            return 'LOW'
        return 'NONE'
    
    def _get_main_attacker(self, results):
        """استخراج IP المهاجم الرئيسي"""
        suspicious_ips = results.get('suspicious_ips', [])
        if suspicious_ips:
            return suspicious_ips[0].get('ip', 'غير معروف')
        return 'لا يوجد'
    
    def _get_attack_types_stats(self, results):
        """إحصائيات أنواع الهجمات"""
        attack_types = {}
        for attack in results.get('attacks', []):
            attack_type = attack.get('type', 'Unknown')
            attack_types[attack_type] = attack_types.get(attack_type, 0) + 1
        return attack_types
    
    def _get_recommendations(self, results):
        """توليد توصيات أمنية بناءً على نتائج التحليل"""
        recommendations = []
        
        # توصيات عامة
        if results.get('total_attacks', 0) > 0:
            recommendations.append({
                'title': 'تحديث النظام',
                'description': 'قم بتحديث جميع البرامج والخادوم إلى آخر إصدار',
                'priority': 'HIGH'
            })
            
            recommendations.append({
                'title': 'تثبيت WAF',
                'description': 'قم بتثبيت Web Application Firewall لمنع الهجمات المستقبلية',
                'priority': 'HIGH'
            })
        
        # توصيات حسب نوع الهجوم
        attack_types = self._get_attack_types_stats(results)
        
        if 'SQL Injection' in attack_types:
            recommendations.append({
                'title': 'حماية من SQL Injection',
                'description': 'استخدم Prepared Statements في جميع استعلامات SQL. قم بتحديث جميع استعلامات SQL في التطبيق.',
                'priority': 'CRITICAL'
            })
        
        if 'XSS' in attack_types:
            recommendations.append({
                'title': 'حماية من XSS',
                'description': 'قم بتطهير جميع المدخلات (Input Sanitization) واستخدم Content Security Policy (CSP).',
                'priority': 'HIGH'
            })
        
        if 'Local File Inclusion' in attack_types:
            recommendations.append({
                'title': 'حماية من LFI/RFI',
                'description': 'قم بتعطيل allow_url_include، وقم بتقييد الوصول إلى الملفات الحساسة.',
                'priority': 'CRITICAL'
            })
        
        if 'Brute Force Attack' in attack_types:
            recommendations.append({
                'title': 'حماية من Brute Force',
                'description': 'قم بتفعيل حماية تسجيل الدخول (Captcha، تحديد عدد المحاولات، تأخير بين المحاولات).',
                'priority': 'MEDIUM'
            })
        
        return recommendations
    
    def _save_report(self, report):
        """حفظ التقرير في ملف JSON"""
        report_file = os.path.join(self.reports_path, f"{report['report_id']}.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"✅ تم حفظ التقرير في: {report_file}")


# اختبار سريع
if __name__ == '__main__':
    reporter = ReportGenerator()
    
    case = {'case_name': 'اختبار', 'website': 'example.com'}
    results = {
        'total_requests': 1000,
        'total_attacks': 50,
        'attacks': [
            {'ip': '192.168.1.1', 'type': 'SQL Injection', 'request': 'GET /page.php?id=1\'--'},
            {'ip': '192.168.1.1', 'type': 'XSS', 'request': 'GET /search.php?q=<script>'}
        ],
        'suspicious_ips': [{'ip': '192.168.1.1', 'count': 25}]
    }
    
    report = reporter.generate_report(case, results)
    print(f"\nتقرير: {report['report_id']}")
    print(f"مستوى الخطورة: {report['summary']['risk_level']}")
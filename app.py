"""
app.py
الدور: الملف الرئيسي لتشغيل سيرفر Flask
يستخدم جميع الموديولات في مجلد core
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
import uuid
from datetime import datetime
from collections import defaultdict
import traceback

# استيراد الموديولات الخاصة بنا
try:
    from core.attack_detector import AttackDetector
    from core.log_parser import LogParser
    from core.report_generator import ReportGenerator
    from core.model_trainer import ModelTrainer
except ImportError as e:
    print(f"❌ Error importing modules: {e}")

# إنشاء تطبيق Flask
app = Flask(__name__)
app.secret_key = 'cybersight-ai-secret-2024'
# السماح بملفات أكبر (مثلاً 32 ميجابايت) لتجنب خطأ 413
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

# مخزن مؤقت لنتائج التحليل لتجنب خطأ 414 URI Too Long
analysis_storage = {}

# إنشاء المجلدات إذا لم تكن موجودة
os.makedirs('uploads', exist_ok=True)
os.makedirs('reports', exist_ok=True)
os.makedirs('models', exist_ok=True)

# تهيئة المكونات
print("=" * 50)
print("🚀 تشغيل CyberSight AI Server")
print("=" * 50)

# 1. تدريب النموذج (إذا لم يكن موجوداً)
trainer = ModelTrainer()
model = trainer.load_model()

if model is None:
    print("⚠️ لم يتم العثور على نموذج، جاري التدريب...")
    model = trainer.train_from_data()

# 2. تهيئة كاشف الهجمات
detector = AttackDetector()

# 3. تهيئة محلل السجلات
log_parser = LogParser()

# 4. تهيئة منشئ التقارير
report_generator = ReportGenerator()

print("✅ جميع المكونات جاهزة!")
print("📍 http://localhost:5000")
print("=" * 50)


# ==================== الصفحات ====================

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    return render_template('index.html')


@app.route('/analyze')
def analyze_page():
    """صفحة تحليل الملفات"""
    return render_template('analyze.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_log():
    """
    API لتحليل السجلات
    تستقبل ملفات access.log و error.log وترجع النتائج
    """
    try:
        # التحقق من وجود ملف access.log
        access_file = request.files.get('access_log_file') or request.files.get('log_file')
        
        if not access_file or access_file.filename == '':
            return jsonify({'error': 'يرجى رفع ملف access.log'}), 400

        # التحقق من محتوى الملف (لا يهم الامتداد)
        try:
            content = access_file.read().decode('utf-8', errors='ignore')
            if not content or len(content.strip()) == 0:
                return jsonify({'error': 'خطأ: الملف المرفوع فارغ'}), 400
        except Exception:
            return jsonify({'error': 'خطأ: تعذر قراءة الملف كملف نصي'}), 400

        # تحليل السجلات
        requests_list = log_parser.parse_file(content)
        
        if not requests_list:
            return jsonify({'error': 'خطأ: لم يتم العثور على سجلات صالحة. تأكد من أن الملف بتنسيق Apache/Nginx standard.'}), 400

        # كشف الهجمات
        attacks = []
        suspicious_ips = defaultdict(int)
        
        for req in requests_list:
            result = detector.detect(req['request'])
            
            if result['is_attack']:
                attacks.append({
                    'ip': req['ip'],
                    'time': req['time'],
                    'request': req['request'],
                    'type': result['attack_type'],
                    'confidence': result['confidence']
                })
                suspicious_ips[req['ip']] += 1
        
        # ترتيب الـ IPs المشبوهة
        suspicious_ips_list = [
            {'ip': ip, 'count': count}
            for ip, count in sorted(suspicious_ips.items(), key=lambda x: x[1], reverse=True)
        ]
        
        # تجميع النتائج
        results = {
            'total_requests': len(requests_list),
            'total_attacks': len(attacks),
            'attacks': attacks,
            'suspicious_ips': suspicious_ips_list
        }
        
        # معالجة ملف error.log إذا كان موجوداً
        error_log_info = "لم يتم رفعه"
        if 'error_log_file' in request.files and request.files['error_log_file'].filename != '':
            error_file = request.files['error_log_file']
            # يمكن إضافة تحليل إضافي هنا مستقبلاً
            error_name = os.path.splitext(error_file.filename)[0]
            error_log_info = f"تم رفع الملف ({error_name})"

        # إنشاء معلومات القضية للتقرير
        case_info = {
            'site_name': request.form.get('site_name') or request.form.get('case_name', 'موقع غير مسمى'),
            'incident_date': request.form.get('incident_date', 'تاريخ غير محدد'),
            'analyzed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'access_log_filename': os.path.splitext(access_file.filename)[0],
            'error_log_info': error_log_info
        }
        
        report = report_generator.generate_report(case_info, results)
        
        # حفظ النتائج في الذاكرة وإرجاع معرف فريد
        report_id = report['report_id']
        analysis_storage[report_id] = {
            'results': results,
            'report': report
        }
        
        return jsonify({
            'success': True,
            'report_id': report_id
        })
        
    except Exception as e:
        print(f"❌ Error during analysis:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/detect', methods=['POST'])
def detect_single():
    """
    API لتحليل طلب واحد
    تستقبل نص الطلب وترجع نتيجة التحليل
    """
    try:
        data = request.get_json()
        request_text = data.get('request', '')
        
        result = detector.detect(request_text)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/train', methods=['POST'])
def train_model_endpoint():
    """
    API لإعادة تدريب النموذج
    """
    try:
        trainer = ModelTrainer()
        model = trainer.train_from_data()
        
        return jsonify({
            'success': True,
            'message': 'Model training successful'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/results')
def results():
    """صفحة عرض النتائج"""
    report_id = request.args.get('id') or request.args.get('report_id')
    
    # 1. البحث في الذاكرة المؤقتة (للسرعة)
    if report_id in analysis_storage:
        data_dict = analysis_storage[report_id]
        return render_template('results.html', 
                             report=data_dict.get('report', {}),
                             results=data_dict.get('results', {}))
    
    # 2. البحث في الملفات المحفوظة (في حال إعادة تشغيل السيرفر)
    if report_id:
        file_path = os.path.join('reports', f"{report_id}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    stored_report = json.load(f)
                    return render_template('results.html', 
                                         report=stored_report,
                                         # Use the results embedded in the report if available
                                         results=stored_report.get('results', {}))
            except Exception as e:
                print(f"Error loading stored report: {e}")
    
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
"""
attack_detector.py
الدور: كشف الهجمات باستخدام النموذج المدرب
المدخل: طلب نصي
المخرج: نتيجة (هل هو هجوم؟ ونوعه وثقته)
"""

import numpy as np
import joblib
import os
from core.feature_extractor import FeatureExtractor

class AttackDetector:
    """كشف الهجمات باستخدام النموذج المدرب"""
    
    def __init__(self, models_path='models'):
        self.models_path = models_path
        self.extractor = FeatureExtractor()
        self.model = None
        
        # تحميل النموذج
        self.load_model()
    
    def load_model(self):
        """تحميل النموذج المدرب"""
        model_path = os.path.join(self.models_path, 'forensic_model.pkl')
        
        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
            print("✅ تم تحميل النموذج بنجاح")
            return True
        else:
            print("⚠️ النموذج غير موجود! قم بتدريب النموذج أولاً")
            return False
    
    def detect(self, request_text):
        """
        كشف إذا كان الطلب هجوماً
        المدخل: request_text - نص الطلب
        المخرج: قاموس يحتوي على:
            - is_attack: هل هو هجوم
            - confidence: نسبة الثقة
            - attack_type: نوع الهجوم (إذا كان هجوماً)
            - request: الطلب الأصلي
        """
        if self.model is None:
            return {
                'is_attack': False,
                'confidence': 0,
                'error': 'النموذج غير محمل',
                'request': request_text
            }
        
        # استخراج الميزات
        features = self.extractor.extract(request_text)
        
        # تحويل إلى مصفوفة
        X = np.array([features])
        
        # التنبؤ
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        confidence = max(probabilities)
        
        # تقدير نوع الهجوم (بناءً على الكلمات المفتاحية)
        attack_type = self._estimate_attack_type(request_text) if prediction == 1 else None
        
        return {
            'is_attack': bool(prediction),
            'confidence': float(confidence),
            'attack_type': attack_type,
            'request': request_text
        }
    
    def _estimate_attack_type(self, text):
        """
        تقدير نوع الهجوم بناءً على الكلمات المفتاحية
        المدخل: text - نص الطلب
        المخرج: نوع الهجوم
        """
        text_lower = text.lower()
        
        # SQL Injection
        sql_keywords = ['select', 'union', 'or ', 'and ', '--', "'", '"', 'drop', 'insert', 'update']
        if any(k in text_lower for k in sql_keywords):
            return 'SQL Injection'
        
        # XSS
        xss_keywords = ['<script', 'javascript:', 'onerror=', 'alert(', '<iframe', '<svg', 'onload=']
        if any(k in text_lower for k in xss_keywords):
            return 'XSS'
        
        # LFI / RFI
        lfi_keywords = ['../', '..\\', '/etc/passwd', 'php://', 'file://', 'proc/self']
        if any(k in text_lower for k in lfi_keywords):
            return 'Local File Inclusion'
        
        # Brute Force
        brute_keywords = ['login', 'admin', 'wp-login', 'password', 'bruteforce']
        if any(k in text_lower for k in brute_keywords):
            return 'Brute Force Attack'
        
        return 'Unknown Attack'
    
    def detect_batch(self, requests_list):
        """
        كشف الهجمات في قائمة من الطلبات
        المدخل: requests_list - قائمة الطلبات
        المخرج: قائمة بالنتائج
        """
        results = []
        for req in requests_list:
            results.append(self.detect(req))
        return results


# اختبار سريع
if __name__ == '__main__':
    detector = AttackDetector()
    
    # اختبار
    tests = [
        "GET /index.html",
        "GET /page.php?id=1' OR '1'='1--",
        "GET /search.php?q=<script>alert(1)</script>",
        "GET /page.php?file=../../../etc/passwd",
    ]
    
    for test in tests:
        result = detector.detect(test)
        print(f"\nطلب: {test}")
        if result['is_attack']:
            print(f"  ⚠️ هجوم - نوع: {result['attack_type']} - ثقة: {result['confidence']*100:.1f}%")
        else:
            print(f"  ✅ عادي - ثقة: {result['confidence']*100:.1f}%")
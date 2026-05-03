"""
feature_extractor.py
الدور: استخراج الميزات (features) من الطلبات النصية
المدخل: نص الطلب (مثل: GET /page.php?id=1'--)
المخرج: قائمة من الأرقام تمثل الميزات
"""

import re

class FeatureExtractor:
    """استخراج الميزات من الطلبات HTTP"""
    
    def __init__(self):
        # أسماء الميزات (20 ميزة)
        self.feature_names = [
            'length',              # 1. طول الطلب
            'num_digits',          # 2. عدد الأرقام
            'num_special_chars',   # 3. عدد الرموز الخاصة
            'num_quotes',          # 4. عدد علامات الاقتباس
            'has_dash',            # 5. وجود --
            'has_union',           # 6. وجود UNION
            'has_select',          # 7. وجود SELECT
            'has_or',              # 8. وجود OR
            'has_and',             # 9. وجود AND
            'has_script',          # 10. وجود <script
            'has_onerror',         # 11. وجود onerror=
            'has_javascript',      # 12. وجود javascript:
            'has_dotdot',          # 13. وجود ../
            'has_etc_passwd',      # 14. وجود /etc/passwd
            'num_params',          # 15. عدد المعاملات
            'has_equals',          # 16. وجود =
            'has_percent',         # 17. وجود %
            'has_ampersand',       # 18. وجود &
            'has_question',        # 19. وجود ?
            'has_space'            # 20. وجود مسافة
        ]
    
    def extract(self, text):
        """
        استخراج الميزات من النص
        المدخل: text - نص الطلب
        المخرج: list - قائمة من 20 رقم
        """
        features = []
        
        # 1. طول الطلب
        features.append(len(text))
        
        # 2. عدد الأرقام
        features.append(len(re.findall(r'\d', text)))
        
        # 3. عدد الرموز الخاصة
        special_chars = r'[!@#$%^&*()_+=\[\]{}|;:,.<>?`~]'
        features.append(len(re.findall(special_chars, text)))
        
        # 4. عدد علامات الاقتباس
        features.append(text.count("'") + text.count('"'))
        
        # 5. وجود --
        features.append(1 if '--' in text else 0)
        
        # 6. وجود UNION
        features.append(1 if 'union' in text.lower() else 0)
        
        # 7. وجود SELECT
        features.append(1 if 'select' in text.lower() else 0)
        
        # 8. وجود OR
        features.append(1 if ' or ' in text.lower() else 0)
        
        # 9. وجود AND
        features.append(1 if ' and ' in text.lower() else 0)
        
        # 10. وجود <script
        features.append(1 if '<script' in text.lower() else 0)
        
        # 11. وجود onerror=
        features.append(1 if 'onerror=' in text.lower() else 0)
        
        # 12. وجود javascript:
        features.append(1 if 'javascript:' in text.lower() else 0)
        
        # 13. وجود ../
        features.append(1 if '../' in text else 0)
        
        # 14. وجود /etc/passwd
        features.append(1 if '/etc/passwd' in text else 0)
        
        # 15. عدد المعاملات
        features.append(text.count('&') + text.count('?'))
        
        # 16. وجود =
        features.append(1 if '=' in text else 0)
        
        # 17. وجود %
        features.append(1 if '%' in text else 0)
        
        # 18. وجود &
        features.append(1 if '&' in text else 0)
        
        # 19. وجود ?
        features.append(1 if '?' in text else 0)
        
        # 20. وجود مسافة
        features.append(1 if ' ' in text else 0)
        
        return features
    
    def get_feature_names(self):
        """إرجاع أسماء الميزات"""
        return self.feature_names


# اختبار سريع (يمكن تشغيله مباشرة)
if __name__ == '__main__':
    extractor = FeatureExtractor()
    
    # اختبار طلب عادي
    normal = "GET /index.html"
    features = extractor.extract(normal)
    print(f"طلب عادي: {normal}")
    print(f"الميزات: {features[:5]}...\n")
    
    # اختبار طلب هجوم
    attack = "GET /page.php?id=1' OR '1'='1--"
    features = extractor.extract(attack)
    print(f"طلب هجوم: {attack}")
    print(f"الميزات: {features[:5]}...")
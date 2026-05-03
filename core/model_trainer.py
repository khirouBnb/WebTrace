"""
model_trainer.py
الدور: تدريب نموذج Random Forest للكشف عن الهجمات
المدخل: قائمة الطلبات وقائمة التصنيفات
المخرج: النموذج المدرب
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
from core.feature_extractor import FeatureExtractor
from core.data_loader import load_data

class ModelTrainer:
    """تدريب نموذج الكشف عن الهجمات"""
    
    def __init__(self, models_path='models'):
        self.models_path = models_path
        self.extractor = FeatureExtractor()
        
        # إنشاء مجلد النماذج إذا لم يكن موجوداً
        if not os.path.exists(models_path):
            os.makedirs(models_path)
    
    def prepare_features(self, requests):
        """
        تحويل الطلبات إلى ميزات
        المدخل: requests - قائمة الطلبات النصية
        المخرج: مصفوفة الميزات
        """
        X = []
        for req in requests:
            features = self.extractor.extract(req)
            X.append(features)
        return np.array(X)
    
    def train(self, X, y):
        """
        تدريب النموذج
        المدخل: X - الميزات, y - التصنيفات
        المخرج: النموذج المدرب
        """
        print("\n" + "=" * 50)
        print("🤖 بدء تدريب النموذج")
        print("=" * 50)
        
        # تقسيم البيانات
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"\n📊 تقسيم البيانات:")
        print(f"   - تدريب: {len(X_train)} عينة")
        print(f"   - اختبار: {len(X_test)} عينة")
        
        # تدريب النموذج
        print("\n🌲 تدريب Random Forest...")
        model = RandomForestClassifier(
            n_estimators=100,      # 100 شجرة
            max_depth=15,          # أقصى عمق
            random_state=42,       # للتكرار
            n_jobs=-1              # استخدام جميع المعالجات
        )
        
        model.fit(X_train, y_train)
        
        # تقييم
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n✅ دقة النموذج: {accuracy * 100:.2f}%")
        print("\nتقرير التصنيف:")
        print(classification_report(y_test, y_pred, target_names=['عادي', 'هجوم']))
        
        return model
    
    def save_model(self, model):
        """حفظ النموذج في ملف"""
        model_path = os.path.join(self.models_path, 'forensic_model.pkl')
        joblib.dump(model, model_path)
        
        # حفظ أسماء الميزات أيضاً
        features_path = os.path.join(self.models_path, 'feature_names.pkl')
        joblib.dump(self.extractor.get_feature_names(), features_path)
        
        print(f"\n✅ تم حفظ النموذج في: {model_path}")
        return model_path
    
    def load_model(self):
        """تحميل النموذج من الملف"""
        model_path = os.path.join(self.models_path, 'forensic_model.pkl')
        
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            print(f"✅ تم تحميل النموذج من: {model_path}")
            return model
        else:
            print(f"⚠️ النموذج غير موجود: {model_path}")
            return None
    
    def train_from_data(self):
        """تدريب النموذج من البيانات المحملة"""
        # تحميل البيانات
        requests, labels = load_data()
        
        # استخراج الميزات
        X = self.prepare_features(requests)
        y = np.array(labels)
        
        # تدريب النموذج
        model = self.train(X, y)
        
        # حفظ النموذج
        self.save_model(model)
        
        return model


# اختبار سريع
if __name__ == '__main__':
    trainer = ModelTrainer()
    model = trainer.train_from_data()
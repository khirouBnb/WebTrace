"""
data_loader.py
الدور: تحميل البيانات من ملفات Kaggle أو استخدام بيانات مدمجة
المدخل: مسار مجلد datasets
المخرج: قائمة الطلبات (requests) وقائمة التصنيفات (labels)
"""

import os
import pandas as pd

def load_kaggle_data(datasets_path='datasets'):
    """
    تحميل البيانات من ملفات Kaggle
    المدخل: datasets_path - مسار مجلد البيانات
    المخرج: (requests, labels) - قائمة الطلبات وقائمة التصنيفات
    """
    
    print("=" * 50)
    print("📊 جاري تحميل البيانات من Kaggle...")
    print("=" * 50)
    
    all_requests = []
    all_labels = []
    
    # 1. تحميل Web Attack Dataset (الرئيسي)
    file1 = os.path.join(datasets_path, 'web-attack-and-normal-requests-dataset', 'balanced_dataset.csv')
    if os.path.exists(file1):
        print(f"📁 تحميل: {file1}")
        try:
            df1 = pd.read_csv(file1)
            
            # محاولة تحديد الأعمدة المناسبة
            if 'Request' in df1.columns and 'Label' in df1.columns:
                for _, row in df1.iterrows():
                    all_requests.append(str(row['Request']))
                    label = 1 if 'attack' in str(row['Label']).lower() else 0
                    all_labels.append(label)
            elif 'Query' in df1.columns and 'Label' in df1.columns:
                for _, row in df1.iterrows():
                    all_requests.append(str(row['Query']))
                    label = 1 if 'attack' in str(row['Label']).lower() else 0
                    all_labels.append(label)
            
            print(f"   ✅ {len(df1)} عينة")
        except Exception as e:
            print(f"   ⚠️ خطأ في قراءة الملف: {e}")
    
    # 2. تحميل SQL Injection Dataset
    file2 = os.path.join(datasets_path, 'sql-injection-dataset', 'sql_injection_dataset.csv')
    if os.path.exists(file2):
        print(f"📁 تحميل: {file2}")
        try:
            df2 = pd.read_csv(file2)
            
            if 'Query' in df2.columns and 'Label' in df2.columns:
                for _, row in df2.iterrows():
                    all_requests.append(str(row['Query']))
                    label = 1 if 'sql' in str(row['Label']).lower() or row['Label'] == 1 else 0
                    all_labels.append(label)
            
            print(f"   ✅ {len(df2)} عينة")
        except Exception as e:
            print(f"   ⚠️ خطأ في قراءة الملف: {e}")
    
    # 3. تحميل HTTP CSIC Dataset
    file3 = os.path.join(datasets_path, 'http-dataset-csic-2010', 'http_dataset.csv')
    if os.path.exists(file3):
        print(f"📁 تحميل: {file3}")
        try:
            df3 = pd.read_csv(file3)
            
            if 'Request' in df3.columns and 'Label' in df3.columns:
                for _, row in df3.iterrows():
                    all_requests.append(str(row['Request']))
                    label = 1 if row['Label'] == 'attack' else 0
                    all_labels.append(label)
            
            print(f"   ✅ {len(df3)} عينة")
        except Exception as e:
            print(f"   ⚠️ خطأ في قراءة الملف: {e}")
    
    return all_requests, all_labels


def load_txt_data(file_path):
    """Load attack/normal requests from txt file"""
    requests = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            requests = [line.strip() for line in f if line.strip()]
        print(f"Loaded {len(requests)} samples from {file_path}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    return requests

def get_builtin_data(datasets_path='datasets'):
    """
    استخدام بيانات مدمجة (إذا لم توجد ملفات Kaggle)
    المخرج: (requests, labels) - قائمة الطلبات وقائمة التصنيفات
    """
    if not os.path.exists(datasets_path):
        os.makedirs(datasets_path, exist_ok=True)
    
    # Load from txt files
    normal = load_txt_data(os.path.join(datasets_path, 'normal_requests.txt'))
    sql = load_txt_data(os.path.join(datasets_path, 'sql_injection_samples.txt'))
    xss = load_txt_data(os.path.join(datasets_path, 'xss_samples.txt'))
    lfi = load_txt_data(os.path.join(datasets_path, 'lfi_samples.txt'))
    
    all_requests = normal + sql + xss + lfi
    all_labels = ([0] * len(normal) + 
                  [1] * (len(sql) + len(xss) + len(lfi)))
    
    return all_requests, all_labels


def load_data(datasets_path='datasets'):
    """
    تحميل البيانات (يحاول Kaggle أولاً، ثم البيانات المدمجة)
    المدخل: datasets_path - مسار مجلد البيانات
    المخرج: (requests, labels) - قائمة الطلبات وقائمة التصنيفات
    """
    
    # محاولة تحميل بيانات Kaggle
    requests, labels = load_kaggle_data(datasets_path)
    
    # إذا لم يتم تحميل أي بيانات، استخدم البيانات المدمجة
    if len(requests) == 0:
        print("⚠️ لم يتم العثور على ملفات Kaggle، جاري استخدام البيانات المدمجة...")
        requests, labels = get_builtin_data(datasets_path)
    
    print(f"\n📊 المجموع الكلي: {len(requests)} عينة")
    print(f"   - هجمات: {sum(labels)}")
    print(f"   - عادي: {len(labels) - sum(labels)}")
    
    return requests, labels


# اختبار سريع
if __name__ == '__main__':
    requests, labels = load_data()
    print(f"\nأول 3 طلبات:")
    for i in range(3):
        print(f"  {i+1}. {requests[i]} -> {'هجوم' if labels[i] else 'عادي'}")
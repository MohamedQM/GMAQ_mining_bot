
# منصة التعدين العربية 🚀

منصة ويب عربية متطورة لأتمتة عمليات التعدين عبر بوتات التليجرام

## 🌟 المميزات

- واجهة عربية سهلة الاستخدام
- دعم متعدد لعملات التعدين (COIN, BANAN, TRX, SHIB, BEAMX)
- نظام مراقبة وإحصائيات شامل
- حفظ تلقائي للبيانات
- إدارة متقدمة للروابط

## 🚀 النشر السريع على Zeabur

### الخطوة 1: رفع المشروع
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO
git push -u origin main
```

### الخطوة 2: النشر على Zeabur
1. اذهب إلى [dash.zeabur.com](https://dash.zeabur.com)
2. اربط حساب GitHub
3. اختر Repository المشروع
4. اضبط متغيرات البيئة:
   - `SESSION_SECRET`: مفتاح سري قوي
5. انقر Deploy

## ⚙️ متغيرات البيئة

```env
SESSION_SECRET=your-secret-key-here
PORT=5000
FLASK_ENV=production
```

## 📁 هيكل المشروع

```
├── app.py              # التطبيق الرئيسي
├── main.py             # نقطة دخول التطبيق  
├── mining_core.py      # نظام التعدين الأساسي
├── requirements.txt    # المكتبات المطلوبة
├── Procfile           # إعدادات النشر
├── zeabur.json        # إعدادات Zeabur
├── templates/         # ملفات HTML
├── static/           # ملفات CSS/JS
└── .env.example      # مثال متغيرات البيئة
```

## 🔧 التطوير المحلي

```bash
# تثبيت المتطلبات
pip install -r requirements.txt

# تشغيل التطبيق
python main.py
```

## 📊 الاستخدام

1. افتح الموقع في المتصفح
2. أدخل رابط التعدين في الحقل المناسب
3. انقر "بدء التعدين"
4. راقب الإحصائيات في الوقت الفعلي

## 🛠️ الدعم الفني

للمساعدة والدعم، يرجى إنشاء Issue في GitHub Repository

---
تم تطوير هذا المشروع بـ ❤️ للمجتمع العربي

# دليل النشر - Deployment Guide

## النشر على Zeabur

1. ارفع المشروع على GitHub
2. اذهب إلى [Zeabur](https://zeabur.com)
3. ربط الحساب بـ GitHub
4. اختر Repository المناسب
5. اضبط متغيرات البيئة:
   - `SESSION_SECRET`: أي نص عشوائي قوي
6. انقر Deploy

## النشر على Heroku

1. ارفع المشروع على GitHub
2. اذهب إلى [Heroku](https://heroku.com)
3. انشئ تطبيق جديد
4. ربط GitHub Repository
5. اضبط Config Vars:
   - `SESSION_SECRET`: أي نص عشوائي قوي
6. Enable Automatic Deploys

## النشر على Railway

1. اذهب إلى [Railway](https://railway.app)
2. ربط GitHub Repository
3. اضبط Environment Variables:
   - `SESSION_SECRET`: أي نص عشوائي قوي
4. Deploy

## النشر على Render

1. اذهب إلى [Render](https://render.com)
2. ربط GitHub Repository
3. اختر Web Service
4. اضبط Environment Variables:
   - `SESSION_SECRET`: أي نص عشوائي قوي
5. Deploy

## نصائح مهمة

- تأكد من وجود جميع الملفات المطلوبة
- اضبط SESSION_SECRET بنص قوي وعشوائي
- تجنب رفع users_data.json إلى GitHub (محمي بـ .gitignore)
- استخدم HTTPS في الإنتاج

## استكشاف الأخطاء

### خطأ 502 Bad Gateway
- تأكد من أن PORT متغير صحيح
- تأكد من أن gunicorn يشتغل على 0.0.0.0
- راجع logs الخدمة

### Application Error
- تأكد من requirements صحيحة
- تأكد من SESSION_SECRET مضبوط
- راجع application logs
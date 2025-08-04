
#!/bin/bash

echo "🔧 إعداد ملفات النشر..."

# التأكد من وجود الملفات المطلوبة
required_files=("main.py" "app.py" "mining_core.py" "requirements.txt" "Procfile")

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ الملف المطلوب غير موجود: $file"
        exit 1
    fi
done

echo "✅ جميع الملفات المطلوبة موجودة"

# تنظيف الملفات غير المطلوبة
echo "🧹 تنظيف الملفات غير المطلوبة..."
rm -f *.zip test_*.py

# إنشاء ملف .env إذا لم يكن موجود
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "📄 تم إنشاء ملف .env من المثال"
fi

echo "🎉 التطبيق جاهز للنشر على Zeabur!"
echo "📋 الخطوات التالية:"
echo "1. ارفع المشروع على GitHub"
echo "2. اذهب إلى dash.zeabur.com"
echo "3. اربط الـ Repository"
echo "4. اضبط متغير البيئة SESSION_SECRET"
echo "5. انقر Deploy"

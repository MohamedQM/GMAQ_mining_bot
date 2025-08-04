
#!/bin/bash

# تعيين متغيرات البيئة الافتراضية
export FLASK_ENV=${FLASK_ENV:-production}
export PORT=${PORT:-5000}

# بدء التطبيق
if [ "$FLASK_ENV" = "production" ]; then
    echo "🚀 تشغيل التطبيق في وضع الإنتاج..."
    gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --preload main:app
else
    echo "🔧 تشغيل التطبيق في وضع التطوير..."
    python main.py
fi

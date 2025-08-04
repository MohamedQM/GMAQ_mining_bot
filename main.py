
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from app import app

# إعداد نظام السجلات للإنتاج
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """تشغيل الموقع مع إعدادات محسنة للإنتاج"""
    logger.info("🚀 بدء تشغيل منصة التعدين العربية...")
    
    # الحصول على البورت من متغيرات البيئة
    port = int(os.environ.get("PORT", 5000))
    
    # إعدادات الإنتاج
    debug_mode = os.environ.get("FLASK_ENV") != "production"
    
    logger.info(f"📡 تشغيل الخادم على البورت: {port}")
    logger.info(f"🔧 وضع التطوير: {'مُفعل' if debug_mode else 'معطل'}")
    
    # تشغيل التطبيق
    app.run(
        host="0.0.0.0", 
        port=port, 
        debug=debug_mode,
        threaded=True,
        use_reloader=False
    )

if __name__ == "__main__":
    main()

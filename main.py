#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from app import app

# إعداد نظام السجلات
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """تشغيل الموقع فقط"""
    logger.info("🚀 بدء تشغيل الموقع...")

    # تشغيل الموقع
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()
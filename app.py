#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import threading
import requests
from mining_core import MiningCore

# إعداد نظام السجلات
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# تهيئة Flask
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your-secret-key-here")

# إعدادات الأدمن
ADMIN_ID = 962731079
forced_channels = []

# تهيئة نظام التعدين
mining_core = MiningCore()

# قاموس الروابط المخصصة
custom_links = {
    'coin': {
        'name': 'COIN',
        'bot_name': 'CryptoFreeMoney_bot',
        'url': 'https://t.me/CryptoFreeMoney_bot?start=962731079',
        'description': 'تعدين العملات المشفرة'
    },
    'banan': {
        'name': 'BANAN',
        'bot_name': 'InstaTasker_bot', 
        'url': 'https://t.me/InstaTasker_bot?start=962731079',
        'description': 'تعدين عملة البانان'
    },
    'trx': {
        'name': 'TRX',
        'bot_name': 'TRXVAULTMININGRoBot',
        'url': 'https://t.me/TRXVAULTMININGRoBot?start=962731079',
        'description': 'تعدين عملة TRX'
    },
    'shib': {
        'name': 'SHIB',
        'bot_name': 'SHIBAdsPaybot',
        'url': 'https://t.me/SHIBAdsPaybot?start=962731079',
        'description': 'تعدين عملة SHIB'
    },
    'beamx': {
        'name': 'BEAMX',
        'bot_name': 'BeamX_bot',
        'url': 'https://t.me/BeamX_bot?start=962731079',
        'description': 'تعدين عملة BEAMX'
    }
}

def get_user_ip():
    """الحصول على IP المستخدم الحقيقي"""
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']

def generate_user_fingerprint():
    """إنشاء بصمة فريدة للمستخدم بناءً على عدة عوامل"""
    import hashlib
    
    # جمع معلومات المستخدم
    user_ip = get_user_ip()
    user_agent = request.headers.get('User-Agent', '')
    accept_language = request.headers.get('Accept-Language', '')
    accept_encoding = request.headers.get('Accept-Encoding', '')
    
    # إنشاء نص فريد
    fingerprint_data = f"{user_ip}:{user_agent}:{accept_language}:{accept_encoding}"
    
    # تشفير البيانات لإنشاء معرف فريد
    fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
    
    return fingerprint

def get_user_location(ip):
    """الحصول على موقع المستخدم من IP"""
    try:
        # تنظيف IP من المنافذ والعناوين المتعددة
        clean_ip = ip.split(',')[0].strip() if ',' in ip else ip.strip()
        
        # تجربة APIs متعددة
        apis = [
            f'http://ip-api.com/json/{clean_ip}?fields=status,country,city,countryCode',
            f'https://ipapi.co/{clean_ip}/json/',
            f'http://www.geoplugin.net/json.gp?ip={clean_ip}'
        ]
        
        for api_url in apis:
            try:
                response = requests.get(api_url, timeout=5)
                data = response.json()
                
                # ip-api.com format
                if 'status' in data and data['status'] == 'success':
                    return {
                        'country': data.get('country', 'غير معروف'),
                        'city': data.get('city', 'غير معروف'),
                        'flag': data.get('countryCode', 'XX').lower()
                    }
                
                # ipapi.co format
                elif 'country_name' in data:
                    return {
                        'country': data.get('country_name', 'غير معروف'),
                        'city': data.get('city', 'غير معروف'),
                        'flag': data.get('country', 'XX').lower()
                    }
                
                # geoplugin format
                elif 'geoplugin_countryName' in data:
                    return {
                        'country': data.get('geoplugin_countryName', 'غير معروف'),
                        'city': data.get('geoplugin_city', 'غير معروف'),
                        'flag': data.get('geoplugin_countryCode', 'XX').lower()
                    }
                    
            except Exception as api_error:
                logger.warning(f"فشل API {api_url}: {api_error}")
                continue
                
    except Exception as e:
        logger.error(f"خطأ في الحصول على الموقع: {e}")
    
    return {'country': 'غير معروف', 'city': 'غير معروف', 'flag': 'xx'}

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    user_ip = get_user_ip()
    user_location = get_user_location(user_ip)
    user_agent = request.headers.get('User-Agent', '')
    
    # إعداد session للمستخدم مع بصمة فريدة
    if 'user_id' not in session:
        user_fingerprint = generate_user_fingerprint()
        session['user_id'] = user_fingerprint
        session['user_ip'] = user_ip
        session['user_agent'] = user_agent
        session['created_at'] = datetime.now().isoformat()
    
    user_id = session['user_id']
    
    # حفظ معلومات المستخدم في نظام التعدين
    if user_id not in mining_core.user_sessions:
        mining_core.user_sessions[user_id] = {
            'user_ip': user_ip,
            'user_agent': user_agent,
            'user_location': user_location,
            'created_at': session.get('created_at'),
            'mining_types': {},
            'total_tasks': 0,
            'start_date': datetime.now().isoformat(),
            'is_running': {},
            'saved_urls': {},
            'url_history': [],
            'custom_user_agent': '',
            'use_custom_ua': False,
            'operation_logs': []
        }
        mining_core.save_user_data()
    
    # التحقق من كون المستخدم أدمن
    is_admin = str(user_id) == str(ADMIN_ID) or user_ip == '127.0.0.1'
    
    # إحصائيات المستخدم
    user_stats = mining_core.get_user_stats(user_id)
    
    return render_template('index.html', 
                         user_ip=user_ip,
                         user_location=user_location,
                         user_agent=user_agent,
                         is_admin=is_admin,
                         user_stats=user_stats,
                         custom_links=custom_links,
                         mining_status=mining_core.get_mining_status(user_id))

@app.route('/donations')
def donations():
    """صفحة التبرعات"""
    return render_template('donations.html')

@app.route('/api/start_mining', methods=['POST'])
def start_mining():
    """بدء التعدين"""
    try:
        data = request.get_json()
        mining_type = data.get('mining_type')
        init_data = data.get('init_data')
        use_custom_ua = data.get('use_custom_ua', False)
        user_id = session.get('user_id')
        
        # التحقق من البيانات الأساسية
        if not mining_type or not init_data:
            return jsonify({'success': False, 'message': 'بيانات غير صحيحة'})
        
        # إنشاء user_id إذا لم يكن موجود
        if not user_id:
            user_fingerprint = generate_user_fingerprint()
            session['user_id'] = user_fingerprint
            session['user_ip'] = get_user_ip()
            session['user_agent'] = request.headers.get('User-Agent', '')
            session['created_at'] = datetime.now().isoformat()
            user_id = user_fingerprint
        
        # استخراج البيانات من الرابط
        extracted_data = mining_core.extract_data(init_data)
        if not extracted_data:
            return jsonify({'success': False, 'message': 'رابط غير صحيح. يجب أن يحتوي على tgWebAppData'})
        
        # حفظ User-Agent إذا طلب المستخدم ذلك
        custom_user_agent = None
        if use_custom_ua:
            custom_user_agent = request.headers.get('User-Agent', '')
        
        result = mining_core.start_mining(user_id, mining_type, extracted_data, custom_user_agent)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"خطأ في بدء التعدين: {e}")
        return jsonify({'success': False, 'message': 'حدث خطأ في بدء التعدين'})

@app.route('/api/stop_mining', methods=['POST'])
def stop_mining():
    """إيقاف التعدين"""
    try:
        data = request.get_json()
        mining_type = data.get('mining_type')
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': 'غير مسموح'})
        
        result = mining_core.stop_mining(user_id, mining_type)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"خطأ في إيقاف التعدين: {e}")
        return jsonify({'success': False, 'message': 'حدث خطأ في إيقاف التعدين'})

@app.route('/api/stop_all_mining', methods=['POST'])
def stop_all_mining():
    """إيقاف جميع أنواع التعدين"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'success': False, 'message': 'غير مسموح'})
        
        result = mining_core.stop_all_mining(user_id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"خطأ في إيقاف جميع التعدين: {e}")
        return jsonify({'success': False, 'message': 'حدث خطأ في إيقاف التعدين'})

@app.route('/api/mining_status')
def get_mining_status():
    """الحصول على حالة التعدين"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'غير مسموح'})
        
        status = mining_core.get_mining_status(user_id)
        stats = mining_core.get_user_stats(user_id)
        
        return jsonify({
            'success': True, 
            'status': status,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"خطأ في الحصول على حالة التعدين: {e}")
        return jsonify({'success': False, 'message': 'حدث خطأ'})

@app.route('/api/admin/users')
def admin_get_users():
    """الحصول على قائمة المستخدمين - للأدمن فقط"""
    try:
        user_id = session.get('user_id')
        user_ip = get_user_ip()
        
        # التحقق من صلاحيات الأدمن
        if str(user_id) != str(ADMIN_ID) and user_ip != '127.0.0.1':
            return jsonify({'success': False, 'message': 'غير مسموح'})
        
        users = mining_core.get_all_users()
        return jsonify({'success': True, 'users': users})
        
    except Exception as e:
        logger.error(f"خطأ في الحصول على المستخدمين: {e}")
        return jsonify({'success': False, 'message': 'حدث خطأ'})

@app.route('/api/admin/stop_user_mining', methods=['POST'])
def admin_stop_user_mining():
    """إيقاف تعدين مستخدم معين - للأدمن فقط"""
    try:
        admin_id = session.get('user_id')
        admin_ip = get_user_ip()
        
        # التحقق من صلاحيات الأدمن
        if str(admin_id) != str(ADMIN_ID) and admin_ip != '127.0.0.1':
            return jsonify({'success': False, 'message': 'غير مسموح'})
        
        data = request.get_json()
        target_user_id = data.get('user_id')
        mining_type = data.get('mining_type')
        
        if mining_type == 'all':
            result = mining_core.stop_all_mining(target_user_id)
        else:
            result = mining_core.stop_mining(target_user_id, mining_type)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"خطأ في إيقاف تعدين المستخدم: {e}")
        return jsonify({'success': False, 'message': 'حدث خطأ'})

@app.route('/api/url_history')
def get_url_history():
    """الحصول على سجل الروابط"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'غير مسموح'})
        
        history = mining_core.get_url_history(user_id)
        return jsonify({'success': True, 'history': history})
        
    except Exception as e:
        logger.error(f"خطأ في الحصول على سجل الروابط: {e}")
        return jsonify({'success': False, 'message': 'حدث خطأ'})

@app.route('/api/clear_url_history', methods=['POST'])
def clear_url_history():
    """مسح سجل الروابط"""





    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'غير مسموح'})
        
        result = mining_core.clear_url_history(user_id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"خطأ في مسح سجل الروابط: {e}")
        return jsonify({'success': False, 'message': 'حدث خطأ'})

@app.route('/api/operation_logs')
def get_operation_logs():
    """الحصول على سجل العمليات"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'غير مسموح'})
        
        logs = mining_core.get_operation_logs(user_id)
        return jsonify({'success': True, 'logs': logs})
        
    except Exception as e:
        logger.error(f"خطأ في الحصول على سجل العمليات: {e}")
        return jsonify({'success': False, 'message': 'حدث خطأ'})

@app.route('/api/clear_operation_logs', methods=['POST'])
def clear_operation_logs():
    """مسح سجل العمليات"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'غير مسموح'})
        
        result = mining_core.clear_operation_logs(user_id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"خطأ في مسح سجل العمليات: {e}")
        return jsonify({'success': False, 'message': 'حدث خطأ'})

@app.route('/api/daily_ads_status')
def get_daily_ads_status():
    """الحصول على حالة الإعلانات اليومية"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'غير مسموح'})
        
        # الحد الأقصى للإعلانات لكل نوع
        max_daily_ads = {
            'COIN': 30,
            'BANAN': 20,
            'TRX': 20,
            'SHIB': 20,
            'BEAMX': 20
        }
        
        status = {}
        
        # جلب الحالة الحالية من السيرفر لكل نوع تعدين
        for mining_type in max_daily_ads.keys():
            if user_id in mining_core.user_sessions:
                saved_urls = mining_core.user_sessions[user_id].get('saved_urls', {})
                if mining_type in saved_urls:
                    try:
                        # إنشاء session مؤقت للفحص
                        temp_session = requests.Session()
                        init_data = saved_urls[mining_type]
                        
                        # جلب العدد الحالي حسب نوع التعدين
                        current_count = 0
                        if mining_type == 'COIN':
                            current_count, _ = mining_core.coin_get_hourly_tasks(temp_session, init_data)
                        elif mining_type == 'BANAN':
                            current_count, _ = mining_core.banan_get_hourly_tasks(temp_session, init_data)
                        elif mining_type == 'TRX':
                            current_count, _ = mining_core.trx_get_hourly_tasks(temp_session, init_data)
                        elif mining_type == 'SHIB':
                            current_count, _ = mining_core.shib_get_hourly_tasks(temp_session, init_data)
                        elif mining_type == 'BEAMX':
                            current_count, _ = mining_core.beamx_get_hourly_tasks(temp_session, init_data)
                        
                        if current_count is not None:
                            max_count = max_daily_ads[mining_type]
                            remaining = max_count - current_count
                            status[mining_type] = {
                                'completed': current_count,
                                'max_daily': max_count,
                                'remaining': remaining,
                                'percentage': round((current_count / max_count) * 100, 1),
                                'is_maxed': current_count >= max_count
                            }
                        else:
                            status[mining_type] = {
                                'completed': 0,
                                'max_daily': max_daily_ads[mining_type],
                                'remaining': max_daily_ads[mining_type],
                                'percentage': 0,
                                'is_maxed': False,
                                'error': 'لا يمكن جلب البيانات'
                            }
                    except Exception as e:
                        status[mining_type] = {
                            'completed': 0,
                            'max_daily': max_daily_ads[mining_type],
                            'remaining': max_daily_ads[mining_type],
                            'percentage': 0,
                            'is_maxed': False,
                            'error': f'خطأ: {str(e)}'
                        }
                else:
                    status[mining_type] = {
                        'completed': 0,
                        'max_daily': max_daily_ads[mining_type],
                        'remaining': max_daily_ads[mining_type],
                        'percentage': 0,
                        'is_maxed': False,
                        'error': 'لم يتم إعداد الرابط بعد'
                    }
        
        return jsonify({'success': True, 'status': status})
        
    except Exception as e:
        logger.error(f"خطأ في جلب حالة الإعلانات اليومية: {e}")
        return jsonify({'success': False, 'message': 'حدث خطأ'})

if __name__ == '__main__':
    # تحميل البيانات المحفوظة وإعادة تشغيل التعدين
    mining_core.load_user_data()
    mining_core.restart_mining_from_saved_data()
    
    app.run(host='0.0.0.0', port=5000, debug=True)

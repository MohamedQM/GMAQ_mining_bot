#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import re
import requests
import time
import threading
import logging
from datetime import datetime

# إعداد نظام السجلات
logger = logging.getLogger(__name__)

class MiningCore:
    def __init__(self):
        self.user_sessions = {}
        self.user_threads = {}
        self.user_data_file = "users_data.json"
        self.forced_channels = []
        self.custom_links = {}

    def save_user_data(self):
        """حفظ بيانات المستخدمين"""
        try:
            data_to_save = {
                'users': {},
                'forced_channels': self.forced_channels,
                'custom_links': self.custom_links
            }
            for user_id, session in self.user_sessions.items():
                data_to_save['users'][str(user_id)] = {
                    'username': session.get('username', ''),
                    'user_ip': session.get('user_ip', ''),
                    'user_agent': session.get('user_agent', ''),
                    'user_location': session.get('user_location', {}),
                    'created_at': session.get('created_at', ''),
                    'mining_types': session.get('mining_types', {}),
                    'total_tasks': session.get('total_tasks', 0),
                    'start_date': session.get('start_date', ''),
                    'last_activity': datetime.now().isoformat(),
                    'is_running': session.get('is_running', {}),
                    'saved_urls': session.get('saved_urls', {}),
                    'url_history': session.get('url_history', []),
                    'custom_user_agent': session.get('custom_user_agent', ''),
                    'use_custom_ua': session.get('use_custom_ua', False),
                    'operation_logs': session.get('operation_logs', [])
                }

            with open(self.user_data_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"خطأ في حفظ بيانات المستخدمين: {e}")

    def load_user_data(self):
        """تحميل بيانات المستخدمين"""
        try:
            if os.path.exists(self.user_data_file):
                with open(self.user_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'users' in data:
                        for user_id, user_info in data['users'].items():
                            # استخدام user_id كما هو (string) بدلاً من تحويله لـ int
                            self.user_sessions[user_id] = user_info
                            # إضافة الحقول المفقودة
                            required_fields = {
                                'saved_urls': {},
                                'url_history': [],
                                'custom_user_agent': '',
                                'use_custom_ua': False,
                                'operation_logs': [],
                                'user_ip': '',
                                'user_agent': '',
                                'user_location': {},
                                'created_at': '',
                                'last_activity': ''
                            }

                            for field, default_value in required_fields.items():
                                if field not in self.user_sessions[user_id]:
                                    self.user_sessions[user_id][field] = default_value

                    if 'forced_channels' in data:
                        self.forced_channels = data['forced_channels']

                    if 'custom_links' in data:
                        self.custom_links.update(data['custom_links'])
        except Exception as e:
            logger.error(f"خطأ في تحميل بيانات المستخدمين: {e}")

    def restart_mining_from_saved_data(self):
        """إعادة تشغيل التعدين التلقائي عند بدء الخادم"""
        try:
            for user_id, session in self.user_sessions.items():
                is_running = session.get('is_running', {})
                saved_urls = session.get('saved_urls', {})

                for mining_type in ['BANAN', 'TRX', 'SHIB', 'COIN', 'BEAMX']:
                    if is_running.get(mining_type, False) and mining_type in saved_urls:
                        init_data = saved_urls[mining_type]

                        thread_key = f"{user_id}_{mining_type}"
                        if thread_key not in self.user_threads or not self.user_threads[thread_key].is_alive():
                            thread = threading.Thread(
                                target=self.mining_worker,
                                args=(user_id, mining_type, init_data),
                                daemon=True
                            )
                            thread.start()
                            self.user_threads[thread_key] = thread

                            logger.info(f"تم إعادة تشغيل التعدين للمستخدم {user_id} - نوع التعدين: {mining_type}")
        except Exception as e:
            logger.error(f"خطأ في إعادة تشغيل التعدين التلقائي: {e}")

    def extract_data(self, url):
        """استخراج البيانات من الرابط - نفس الطريقة المستخدمة في السكريپتات الأصلية"""
        try:
            # استخراج الجزء المشفر بعد tgWebAppData= (نفس النمط من السكريپت الأصلي)
            match = re.search(r'tgWebAppData=([^&]+)', url)
            if match:
                return match.group(1)

            # إذا كان الرابط مجرد بيانات مشفرة فقط
            if url.startswith('user%3D'):
                return url

            logger.warning(f"لا يمكن استخراج البيانات من الرابط: {url[:100]}")
            return None

        except Exception as e:
            logger.error(f"خطأ في استخراج البيانات: {e}")
            return None

    # دوال سكريبت BANAN
    def banan_get_hourly_tasks(self, session, init_data):
        url = f"https://botsmother.com/api/command/OTMx/NzY0Ng==?initData={init_data}"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": url
        }
        # إذا لم يكن هناك User-Agent مخصص، استخدم الافتراضي
        if 'User-Agent' not in session.headers:
            headers["User-Agent"] = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1"
        resp = session.get(url, headers=headers)
        match = re.search(r'id="hourly-tasks">(\d+)<', resp.text)
        if match:
            return int(match.group(1)), url
        return None, url

    def banan_get_task_id(self, session, init_data, referer):
        url = f"https://botsmother.com/api/command/OTMx/NzY1MA==?initData={init_data}"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
            "Accept": "*/*",
            "Referer": referer,
            "Content-Type": "application/json"
        }
        resp = session.get(url, headers=headers)
        try:
            data = resp.json()
            return data.get("task_id")
        except Exception:
            return None

    def banan_complete_task(self, session, init_data, task_id, referer):
        url = f"https://botsmother.com/api/command/OTMx/NzY1MQ==?initData={init_data}&task_id={task_id}"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
            "Accept": "*/*",
            "Referer": referer,
            "Content-Type": "application/json"
        }
        resp = session.get(url, headers=headers)
        try:
            return resp.json()
        except Exception:
            return resp.text

    # دوال سكريبت TRX
    def trx_get_hourly_tasks(self, session, init_data):
        url = f"https://botsmother.com/api/command/OTg3/ODA0MA==?initData={init_data}"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": url
        }
        resp = session.get(url, headers=headers)
        match = re.search(r'id="hourly-tasks">(\d+)<', resp.text)
        if match:
            return int(match.group(1)), url
        return None, url

    def trx_get_task_id(self, session, init_data, referer):
        url = f"https://botsmother.com/api/command/OTg3/ODA0NA==?initData={init_data}"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
            "Accept": "*/*",
            "Referer": referer,
            "Content-Type": "application/json"
        }
        resp = session.get(url, headers=headers)
        try:
            data = resp.json()
            return data.get("task_id")
        except Exception:
            return None

    def trx_complete_task(self, session, init_data, task_id, referer):
        url = f"https://botsmother.com/api/command/OTg3/ODA0NQ==?initData={init_data}&task_id={task_id}"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
            "Accept": "*/*",
            "Referer": referer,
            "Content-Type": "application/json"
        }
        resp = session.get(url, headers=headers)
        try:
            return resp.json()
        except Exception:
            return resp.text

    # دوال سكريبت SHIB
    def shib_get_hourly_tasks(self, session, init_data):
        url = f"https://botsmother.com/api/command/OTU4/NzgzMw==?initData={init_data}"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": url
        }
        resp = session.get(url, headers=headers)
        match = re.search(r'id="hourly-tasks">(\d+)<', resp.text)
        if match:
            return int(match.group(1)), url
        return None, url

    def shib_get_task_id(self, session, init_data, referer):
        url = f"https://botsmother.com/api/command/OTU4/NzgzNw==?initData={init_data}"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
            "Accept": "*/*",
            "Referer": referer,
            "Content-Type": "application/json"
        }
        resp = session.get(url, headers=headers)
        try:
            data = resp.json()
            return data.get("task_id")
        except Exception:
            return None

    def shib_complete_task(self, session, init_data, task_id, referer):
        url = f"https://botsmother.com/api/command/OTU4/NzgzOA==?initData={init_data}&task_id={task_id}"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
            "Accept": "*/*",
            "Referer": referer,
            "Content-Type": "application/json"
        }
        resp = session.get(url, headers=headers)
        try:
            return resp.json()
        except Exception:
            return resp.text

    # دوال سكريبت COIN
    def coin_get_hourly_tasks(self, session, init_data):
        url = f"https://botsmother.com/api/command/OTkz/ODA1OQ==?initData={init_data}"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": url
        }
        resp = session.get(url, headers=headers)
        match = re.search(r'id="hourly-tasks">(\d+)<', resp.text)
        if match:
            return int(match.group(1)), url
        return None, url

    def coin_get_task_id(self, session, init_data, referer):
        url = f"https://botsmother.com/api/command/OTkz/ODA2Mw==?initData={init_data}"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
            "Accept": "*/*",
            "Referer": referer,
            "Content-Type": "application/json"
        }
        resp = session.get(url, headers=headers)
        try:
            data = resp.json()
            return data.get("task_id")
        except Exception:
            return None

    def coin_complete_task(self, session, init_data, task_id, referer):
        url = f"https://botsmother.com/api/command/OTkz/ODA2NA==?initData={init_data}&task_id={task_id}"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
            "Accept": "*/*",
            "Referer": referer,
            "Content-Type": "application/json"
        }
        resp = session.get(url, headers=headers)
        try:
            return resp.json()
        except Exception:
            return resp.text

    # BEAMX script functions - Updated with correct URLs
    def beamx_get_page_info(self, session, init_data):
        """جلب معلومات الصفحة الرئيسية للـ BEAMX"""
        url = f"https://botsmother.com/api/command/MTAyOQ==/ODQ1Mg==?initData={init_data}"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": url
        }
        resp = session.get(url, headers=headers)

        page_info = {
            'balance': None,
            'daily_tasks_completed': None,
            'daily_tasks_total': None,
            'hourly_tasks_completed': None,
            'hourly_tasks_total': None,
            'daily_progress': 0,
            'hourly_progress': 0,
            'can_mine': False
        }

        try:
            # استخراج الرصيد - من الـ JavaScript variables أولاً
            balance_patterns = [
                r'balance["\']?\s*:\s*([0-9.]+)',  # JavaScript variable
                r'user-balance["\']?>([0-9.]+)<',  # HTML element
                r'Balance[:\s]*([0-9.]+)',  # Plain text
                r'id="balance"[^>]*>([^<]+)'  # HTML id
            ]
            for pattern in balance_patterns:
                balance_match = re.search(pattern, resp.text, re.IGNORECASE)
                if balance_match:
                    page_info['balance'] = balance_match.group(1).strip()
                    break

            # استخراج إعلانات الساعة - من الـ JavaScript variables أولاً
            hourly_patterns = [
                r'hourlyTasks["\']?\s*:\s*(\d+)',  # JavaScript variable
                r'hourly-tasks["\']?>(\d+)<',  # HTML element
                r'id="hourly-tasks">(\d+)<',  # HTML id
                r'Hourly.*?(\d+)/(\d+)',  # Text pattern
            ]
            for pattern in hourly_patterns:
                hourly_match = re.search(pattern, resp.text, re.IGNORECASE)
                if hourly_match:
                    page_info['hourly_tasks_completed'] = int(hourly_match.group(1))
                    page_info['hourly_tasks_total'] = 15  # الافتراضي الصحيح للـ BEAMX
                    page_info['hourly_progress'] = (page_info['hourly_tasks_completed'] / 15) * 100
                    break
            else:
                page_info['hourly_tasks_completed'] = 0
                page_info['hourly_tasks_total'] = 15
                page_info['hourly_progress'] = 0

            # استخراج إعلانات اليوم - من الـ JavaScript variables أولاً
            daily_patterns = [
                r'todayTasks["\']?\s*:\s*(\d+)',  # JavaScript variable
                r'today-tasks["\']?>(\d+)<',  # HTML element
                r'id="daily-tasks">(\d+)<',  # HTML id
                r'Daily.*?(\d+)/(\d+)',  # Text pattern
            ]
            for pattern in daily_patterns:
                daily_match = re.search(pattern, resp.text, re.IGNORECASE)
                if daily_match:
                    page_info['daily_tasks_completed'] = int(daily_match.group(1))
                    page_info['daily_tasks_total'] = 30  # الافتراضي الصحيح للـ BEAMX
                    page_info['daily_progress'] = (page_info['daily_tasks_completed'] / 30) * 100
                    break
            else:
                page_info['daily_tasks_completed'] = 0
                page_info['daily_tasks_total'] = 30
                page_info['daily_progress'] = 0

            # تحديد إمكانية التعدين
            if page_info['daily_progress'] < 100 and page_info['hourly_progress'] < 100:
                page_info['can_mine'] = True

            logger.info(f"معلومات BEAMX: الرصيد={page_info['balance']}, اليوم={page_info['daily_tasks_completed']}/100, الساعة={page_info['hourly_tasks_completed']}/20")

        except Exception as e:
            logger.error(f"خطأ في تحليل صفحة BEAMX: {e}")

        return page_info, url

    def beamx_get_task_id(self, session, init_data, referer):
        url = f"https://botsmother.com/api/command/MTAyOQ==/ODQ1Ng==?initData={init_data}"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
            "Accept": "*/*",
            "Referer": referer,
            "Content-Type": "application/json"
        }
        resp = session.get(url, headers=headers)
        try:
            data = resp.json()
            # التحقق من وجود status وأنه True
            if data.get("status") == True and "task_id" in data:
                return data.get("task_id")
            return None
        except Exception as e:
            logger.error(f"خطأ في جلب task_id للـ BEAMX: {e}")
            return None

    def beamx_complete_task(self, session, init_data, task_id, referer):
        url = f"https://botsmother.com/api/command/MTAyOQ==/ODQ1Nw==?initData={init_data}&task_id={task_id}"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
            "Accept": "*/*",
            "Referer": referer,
            "Content-Type": "application/json"
        }
        resp = session.get(url, headers=headers)
        try:
            return resp.json()
        except Exception:
            return resp.text

    def mining_worker(self, user_id, mining_type, init_data):
        """عامل التعدين"""
        session = requests.Session()

        # الحد الأقصى للإعلانات لكل نوع تعدين
        max_daily_tasks = {
            'COIN': 30,
            'BANAN': 20,
            'TRX': 20,
            'SHIB': 20,
            'BEAMX': 20
        }

        # تهيئة session المستخدم
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'user_ip': '',
                'user_agent': '',
                'user_location': {},
                'created_at': datetime.now().isoformat(),
                'mining_types': {},
                'total_tasks': 0,
                'start_date': datetime.now().isoformat(),
                'is_running': {},
                'saved_urls': {},
                'url_history': [],
                'custom_user_agent': '',
                'use_custom_ua': False,
                'operation_logs': [],
                'last_activity': datetime.now().isoformat()
            }

        # استخدام User-Agent المخصص إذا كان متاحًا
        if self.user_sessions[user_id].get('use_custom_ua', False):
            custom_ua = self.user_sessions[user_id].get('custom_user_agent', '')
            if custom_ua:
                session.headers.update({'User-Agent': custom_ua})

        # حفظ الرابط وتحديث الحالة
        self.user_sessions[user_id]['saved_urls'][mining_type] = init_data
        self.user_sessions[user_id]['is_running'][mining_type] = True

        if mining_type not in self.user_sessions[user_id]['mining_types']:
            self.user_sessions[user_id]['mining_types'][mining_type] = 0

        self.save_user_data()

        logger.info(f"بدأ التعدين للمستخدم {user_id} - نوع التعدين: {mining_type}")

        while self.user_sessions[user_id].get('is_running', {}).get(mining_type, False):
            try:
                # اختيار دالة التعدين المناسبة
                # تسجيل تفاصيل العملية
                operation_log = {
                    'timestamp': datetime.now().isoformat(),
                    'mining_type': mining_type,
                    'user_id': user_id,
                    'step': '',
                    'status': '',
                    'details': '',
                    'error': None
                }

                if mining_type == 'BANAN':
                    operation_log['step'] = 'جلب المهام'
                    tasks, referer = self.banan_get_hourly_tasks(session, init_data)
                    if tasks:
                        operation_log['status'] = 'نجح'
                        operation_log['details'] = f'تم العثور على {tasks} مهمة'
                        self.add_operation_log(user_id, operation_log.copy())

                        operation_log['step'] = 'جلب Task ID'
                        task_id = self.banan_get_task_id(session, init_data, referer)
                        if task_id:
                            operation_log['status'] = 'نجح'
                            operation_log['details'] = f'Task ID: {task_id}'
                            self.add_operation_log(user_id, operation_log.copy())

                            # انتظار 10 ثواني للتأكد من مشاهدة الإعلان
                            operation_log['step'] = 'انتظار'
                            operation_log['status'] = 'جاري'
                            operation_log['details'] = 'انتظار 10 ثواني لمشاهدة الإعلان'
                            self.add_operation_log(user_id, operation_log.copy())
                            logger.info(f"انتظار 10 ثواني قبل إكمال المهمة - {mining_type} - المستخدم {user_id}")
                            time.sleep(10)

                            operation_log['step'] = 'إكمال المهمة'
                            result = self.banan_complete_task(session, init_data, task_id, referer)
                            if result:
                                operation_log['status'] = 'نجح'
                                operation_log['details'] = f'تم إكمال المهمة بنجاح: {result}'
                                self.user_sessions[user_id]['mining_types'][mining_type] += 1
                                self.user_sessions[user_id]['total_tasks'] += 1
                            else:
                                operation_log['status'] = 'فشل'
                                operation_log['details'] = 'فشل في إكمال المهمة'
                        else:
                            operation_log['status'] = 'فشل'
                            operation_log['details'] = 'فشل في الحصول على Task ID'
                    else:
                        operation_log['status'] = 'فشل'
                        operation_log['details'] = 'فشل في جلب المهام'
                    self.add_operation_log(user_id, operation_log.copy())

                elif mining_type == 'TRX':
                    operation_log['step'] = 'جلب المهام'
                    tasks, referer = self.trx_get_hourly_tasks(session, init_data)
                    if tasks:
                        operation_log['status'] = 'نجح'
                        operation_log['details'] = f'تم العثور على {tasks} مهمة'
                        self.add_operation_log(user_id, operation_log.copy())

                        operation_log['step'] = 'جلب Task ID'
                        task_id = self.trx_get_task_id(session, init_data, referer)
                        if task_id:
                            operation_log['status'] = 'نجح'
                            operation_log['details'] = f'Task ID: {task_id}'
                            self.add_operation_log(user_id, operation_log.copy())

                            # انتظار 10 ثواني
                            operation_log['step'] = 'انتظار'
                            operation_log['status'] = 'جاري'
                            operation_log['details'] = 'انتظار 10 ثواني لمشاهدة الإعلان'
                            self.add_operation_log(user_id, operation_log.copy())
                            logger.info(f"انتظار 10 ثواني قبل إكمال المهمة - {mining_type} - المستخدم {user_id}")
                            time.sleep(10)

                            operation_log['step'] = 'إكمال المهمة'
                            result = self.trx_complete_task(session, init_data, task_id, referer)
                            if result:
                                operation_log['status'] = 'نجح'
                                operation_log['details'] = f'تم إكمال المهمة بنجاح: {result}'
                                self.user_sessions[user_id]['mining_types'][mining_type] += 1
                                self.user_sessions[user_id]['total_tasks'] += 1
                            else:
                                operation_log['status'] = 'فشل'
                                operation_log['details'] = 'فشل في إكمال المهمة'
                        else:
                            operation_log['status'] = 'فشل'
                            operation_log['details'] = 'فشل في الحصول على Task ID'
                    else:
                        operation_log['status'] = 'فشل'
                        operation_log['details'] = 'فشل في جلب المهام'
                    self.add_operation_log(user_id, operation_log.copy())

                elif mining_type == 'SHIB':
                    operation_log['step'] = 'جلب المهام'
                    tasks, referer = self.shib_get_hourly_tasks(session, init_data)
                    if tasks:
                        operation_log['status'] = 'نجح'
                        operation_log['details'] = f'تم العثور على {tasks} مهمة'
                        self.add_operation_log(user_id, operation_log.copy())

                        operation_log['step'] = 'جلب Task ID'
                        task_id = self.shib_get_task_id(session, init_data, referer)
                        if task_id:
                            operation_log['status'] = 'نجح'
                            operation_log['details'] = f'Task ID: {task_id}'
                            self.add_operation_log(user_id, operation_log.copy())

                            # انتظار 10 ثواني
                            operation_log['step'] = 'انتظار'
                            operation_log['status'] = 'جاري'
                            operation_log['details'] = 'انتظار 10 ثواني لمشاهدة الإعلان'
                            self.add_operation_log(user_id, operation_log.copy())
                            logger.info(f"انتظار 10 ثواني قبل إكمال المهمة - {mining_type} - المستخدم {user_id}")
                            time.sleep(10)

                            operation_log['step'] = 'إكمال المهمة'
                            result = self.shib_complete_task(session, init_data, task_id, referer)
                            if result:
                                operation_log['status'] = 'نجح'
                                operation_log['details'] = f'تم إكمال المهمة بنجاح: {result}'
                                self.user_sessions[user_id]['mining_types'][mining_type] += 1
                                self.user_sessions[user_id]['total_tasks'] += 1
                            else:
                                operation_log['status'] = 'فشل'
                                operation_log['details'] = 'فشل في إكمال المهمة'
                        else:
                            operation_log['status'] = 'فشل'
                            operation_log['details'] = 'فشل في الحصول على Task ID'
                    else:
                        operation_log['status'] = 'فشل'
                        operation_log['details'] = 'فشل في جلب المهام'
                    self.add_operation_log(user_id, operation_log.copy())

                elif mining_type == 'COIN':
                    operation_log['step'] = 'فحص المهام المكتملة'
                    tasks_completed, referer = self.coin_get_hourly_tasks(session, init_data)
                    max_tasks = max_daily_tasks.get(mining_type, 20)

                    if tasks_completed is not None:
                        remaining_tasks = max_tasks - tasks_completed
                        operation_log['status'] = 'نجح'
                        operation_log['details'] = f'المهام المكتملة: {tasks_completed}/{max_tasks} - المتبقي: {remaining_tasks}'
                        self.add_operation_log(user_id, operation_log.copy())

                        # التحقق من الوصول للحد الأقصى
                        if tasks_completed >= max_tasks:
                            operation_log['step'] = 'تم الوصول للحد الأقصى'
                            operation_log['status'] = 'مكتمل'
                            operation_log['details'] = f'تم إكمال جميع المهام اليومية ({max_tasks}/{max_tasks}). سيتم إعادة المحاولة بعد ساعة'
                            self.add_operation_log(user_id, operation_log.copy())
                            logger.info(f"تم الوصول للحد الأقصى للمهام - {mining_type} - المستخدم {user_id}")
                            time.sleep(3600)  # انتظار ساعة كاملة
                            continue

                        operation_log['step'] = 'جلب Task ID'
                        task_id = self.coin_get_task_id(session, init_data, referer)
                        if task_id:
                            operation_log['status'] = 'نجح'
                            operation_log['details'] = f'Task ID: {task_id}'
                            self.add_operation_log(user_id, operation_log.copy())

                            # انتظار 10 ثواني
                            operation_log['step'] = 'انتظار'
                            operation_log['status'] = 'جاري'
                            operation_log['details'] = 'انتظار 10 ثواني لمشاهدة الإعلان'
                            self.add_operation_log(user_id, operation_log.copy())
                            logger.info(f"انتظار 10 ثواني قبل إكمال المهمة - {mining_type} - المستخدم {user_id}")
                            time.sleep(10)

                            operation_log['step'] = 'إكمال المهمة'
                            result = self.coin_complete_task(session, init_data, task_id, referer)
                            if result:
                                operation_log['status'] = 'نجح'
                                operation_log['details'] = f'تم إكمال المهمة بنجاح: {result}'
                                self.user_sessions[user_id]['mining_types'][mining_type] += 1
                                self.user_sessions[user_id]['total_tasks'] += 1
                            else:
                                operation_log['status'] = 'فشل'
                                operation_log['details'] = 'فشل في إكمال المهمة'
                        else:
                            operation_log['status'] = 'فشل'
                            operation_log['details'] = 'فشل في الحصول على Task ID'
                    else:
                        operation_log['status'] = 'فشل'
                        operation_log['details'] = 'فشل في جلب المهام'
                    self.add_operation_log(user_id, operation_log.copy())

                elif mining_type == 'BEAMX':
                    operation_log['step'] = 'فحص الصفحة الرئيسية'
                    page_info, referer = self.beamx_get_page_info(session, init_data)

                    # تحديث معلومات المستخدم
                    operation_log['status'] = 'نجح'
                    operation_log['details'] = f"الرصيد: {page_info['balance']}, يومي: {page_info['daily_tasks_completed']}/100, ساعة: {page_info['hourly_tasks_completed']}/20"
                    self.add_operation_log(user_id, operation_log.copy())

                    # فحص إذا كانت المهام اليومية مكتملة
                    if page_info['daily_progress'] >= 100:
                        operation_log['step'] = 'مهام يومية مكتملة'
                        operation_log['status'] = 'توقف'
                        operation_log['details'] = 'تم إنجاز جميع المهام اليومية - سيتم إعادة التشغيل بعد UTC+3'
                        self.add_operation_log(user_id, operation_log.copy())
                        logger.info(f"مهام BEAMX اليومية مكتملة للمستخدم {user_id} - توقف حتى اليوم التالي")
                        time.sleep(600)  # انتظار 10 دقائق ثم إعادة فحص
                        continue

                    # فحص إذا كانت مهام الساعة مكتملة
                    if page_info['hourly_progress'] >= 100:
                        operation_log['step'] = 'مهام ساعة مكتملة'
                        operation_log['status'] = 'انتظار'
                        operation_log['details'] = 'تم إنجاز جميع مهام الساعة - انتظار 10 دقائق'
                        self.add_operation_log(user_id, operation_log.copy())
                        logger.info(f"مهام BEAMX الساعة مكتملة للمستخدم {user_id} - انتظار 10 دقائق")
                        time.sleep(600)  # انتظار 10 دقائق
                        continue

                    # إذا كان التعدين متاح
                    if page_info['can_mine']:
                        operation_log['step'] = 'جلب Task ID'
                        task_id = self.beamx_get_task_id(session, init_data, referer)
                        if task_id:
                            operation_log['status'] = 'نجح'
                            operation_log['details'] = f'Task ID: {task_id}'
                            self.add_operation_log(user_id, operation_log.copy())

                            # انتظار 11 ثانية
                            operation_log['step'] = 'انتظار'
                            operation_log['status'] = 'جاري'
                            operation_log['details'] = 'انتظار 11 ثانية لمشاهدة الإعلان'
                            self.add_operation_log(user_id, operation_log.copy())
                            logger.info(f"انتظار 11 ثانية قبل إكمال المهمة - {mining_type} - المستخدم {user_id}")
                            time.sleep(11)

                            operation_log['step'] = 'إكمال المهمة'
                            result = self.beamx_complete_task(session, init_data, task_id, referer)
                            if result and isinstance(result, dict) and result.get('status') == True:
                                operation_log['status'] = 'نجح'
                                balance = result.get('balance', 'غير محدد')
                                hourly_tasks = result.get('hourlyTasks', 'غير محدد')
                                operation_log['details'] = f'تم إكمال المهمة بنجاح! الرصيد: {balance}, المهام: {hourly_tasks}'
                                self.user_sessions[user_id]['mining_types'][mining_type] += 1
                                self.user_sessions[user_id]['total_tasks'] += 1
                            else:
                                operation_log['status'] = 'فشل'
                                operation_log['details'] = f'فشل في إكمال المهمة: {result}'
                            self.add_operation_log(user_id, operation_log.copy())
                        else:
                            operation_log['status'] = 'فشل'
                            operation_log['details'] = 'فشل في الحصول على Task ID'
                            self.add_operation_log(user_id, operation_log.copy())
                    else:
                        operation_log['status'] = 'متوقف'
                        operation_log['details'] = 'التعدين غير متاح حالياً'
                        self.add_operation_log(user_id, operation_log.copy())

                # حفظ البيانات
                self.save_user_data()

                # انتظار 5 ثواني قبل المحاولة التالية
                operation_log['step'] = 'انتظار المحاولة التالية'
                operation_log['status'] = 'جاري'
                operation_log['details'] = 'انتظار 5 ثواني قبل البحث عن مهام جديدة'
                self.add_operation_log(user_id, operation_log.copy())

                logger.info(f"انتظار 5 ثواني قبل المحاولة التالية - {mining_type} - المستخدم {user_id}")
                time.sleep(5)

            except Exception as e:
                logger.error(f"خطأ في التعدين للمستخدم {user_id} - {mining_type}: {e}")
                time.sleep(5)  # انتظار 5 ثواني عند حدوث خطأ

        logger.info(f"توقف التعدين للمستخدم {user_id} - نوع التعدين: {mining_type}")

    def extract_init_data_from_url(self, url):
        """استخراج initData من الرابط الكامل للبوت"""
        # استخراج الجزء المشفر بعد tgWebAppData=
        match = re.search(r'tgWebAppData=([^&]+)', url)
        if match:
            return match.group(1)
        # إذا كان الرابط يحتوي على initData مباشرة (الشكل القديم)
        return url

    def start_mining(self, user_id, mining_type, init_data, custom_user_agent=None):
        """بدء التعدين"""
        try:
            # التحقق من أن التعدين غير نشط بالفعل
            thread_key = f"{user_id}_{mining_type}"
            if thread_key in self.user_threads and self.user_threads[thread_key].is_alive():
                return {'success': False, 'message': f'التعدين {mining_type} يعمل بالفعل'}

            # تهيئة session المستخدم
            if user_id not in self.user_sessions:
                self.user_sessions[user_id] = {
                    'user_ip': '',
                    'user_agent': '',
                    'user_location': {},
                    'created_at': datetime.now().isoformat(),
                    'mining_types': {},
                    'total_tasks': 0,
                    'start_date': datetime.now().isoformat(),
                    'is_running': {},
                    'saved_urls': {},
                    'url_history': [],
                    'custom_user_agent': '',
                    'use_custom_ua': False,
                    'operation_logs': [],
                    'last_activity': datetime.now().isoformat()
                }

            # حفظ User-Agent المخصص
            if custom_user_agent:
                self.user_sessions[user_id]['custom_user_agent'] = custom_user_agent
                self.user_sessions[user_id]['use_custom_ua'] = True

            # استخراج initData من الرابط إذا كان رابط كامل
            extracted_init_data = self.extract_init_data_from_url(init_data)

            # حفظ الرابط الأصلي في السجل
            url_entry = {
                'url': init_data,  # الرابط الأصلي الكامل
                'mining_type': mining_type,
                'timestamp': datetime.now().isoformat(),
                'status': 'started'
            }
            self.user_sessions[user_id]['url_history'].append(url_entry)

            # بدء خيط التعدين
            thread = threading.Thread(
                target=self.mining_worker,
                args=(user_id, mining_type, extracted_init_data),
                daemon=True
            )
            thread.start()
            self.user_threads[thread_key] = thread

            return {'success': True, 'message': f'تم بدء التعدين {mining_type} بنجاح'}

        except Exception as e:
            logger.error(f"خطأ في بدء التعدين: {e}")
            return {'success': False, 'message': 'حدث خطأ في بدء التعدين'}

    def stop_mining(self, user_id, mining_type):
        """إيقاف التعدين"""
        try:
            if user_id in self.user_sessions:
                self.user_sessions[user_id].setdefault('is_running', {})[mining_type] = False
                self.save_user_data()
                return {'success': True, 'message': f'تم إيقاف التعدين {mining_type}'}

            return {'success': False, 'message': 'المستخدم غير موجود'}

        except Exception as e:
            logger.error(f"خطأ في إيقاف التعدين: {e}")
            return {'success': False, 'message': 'حدث خطأ في إيقاف التعدين'}

    def stop_all_mining(self, user_id):
        """إيقاف جميع أنواع التعدين"""
        try:
            if user_id in self.user_sessions:
                for mining_type in ['BANAN', 'TRX', 'SHIB', 'COIN', 'BEAMX']:
                    self.user_sessions[user_id].setdefault('is_running', {})[mining_type] = False
                self.save_user_data()
                return {'success': True, 'message': 'تم إيقاف جميع أنواع التعدين'}

            return {'success': False, 'message': 'المستخدم غير موجود'}

        except Exception as e:
            logger.error(f"خطأ في إيقاف جميع التعدين: {e}")
            return {'success': False, 'message': 'حدث خطأ في إيقاف التعدين'}

    def get_mining_status(self, user_id):
        """الحصول على حالة التعدين"""
        if user_id in self.user_sessions:
            return self.user_sessions[user_id].get('is_running', {})
        return {}

    def get_user_stats(self, user_id):
        """الحصول على إحصائيات المستخدم"""
        if user_id in self.user_sessions:
            session = self.user_sessions[user_id]
            return {
                'mining_types': session.get('mining_types', {}),
                'total_tasks': session.get('total_tasks', 0),
                'start_date': session.get('start_date', ''),
                'last_activity': session.get('last_activity', '')
            }
        return {'mining_types': {}, 'total_tasks': 0, 'start_date': '', 'last_activity': ''}

    def get_all_users(self):
        """الحصول على جميع المستخدمين - للأدمن"""
        users = []
        for user_id, session in self.user_sessions.items():
            users.append({
                'user_id': user_id,
                'username': session.get('username', 'غير معروف'),
                'total_tasks': session.get('total_tasks', 0),
                'mining_types': session.get('mining_types', {}),
                'is_running': session.get('is_running', {}),
                'start_date': session.get('start_date', ''),
                'last_activity': session.get('last_activity', '')
            })
        return users

    def get_url_history(self, user_id):
        """الحصول على سجل الروابط للمستخدم"""
        if user_id not in self.user_sessions:
            return []

        # جمع الروابط من url_history و saved_urls
        history = []

        # إضافة الروابط من url_history (الروابط القديمة)
        url_history = self.user_sessions[user_id].get('url_history', [])
        for entry in url_history:
            history.append({
                'mining_type': entry.get('mining_type', 'غير محدد'),
                'url': entry.get('url', ''),
                'timestamp': entry.get('timestamp', ''),
                'status': entry.get('status', 'غير محدد')
            })

        # إضافة الروابط من saved_urls (الروابط المحفوظة حالياً)
        saved_urls = self.user_sessions[user_id].get('saved_urls', {})
        for mining_type, url_data in saved_urls.items():
            if isinstance(url_data, list):
                # إذا كانت قائمة من الروابط
                for url_entry in url_data:
                    history.append({
                        'mining_type': mining_type,
                        'url': url_entry.get('url', ''),
                        'timestamp': url_entry.get('added_at', ''),
                        'status': 'محفوظ'
                    })
            elif isinstance(url_data, str):
                # إذا كان رابط واحد (النظام القديم)
                history.append({
                    'mining_type': mining_type,
                    'url': url_data,
                    'timestamp': self.user_sessions[user_id].get('created_at', ''),
                    'status': 'محفوظ'
                })

        # ترتيب التاريخ من الأحدث للأقدم
        history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        return history

    def clear_url_history(self, user_id):
        """مسح سجل الروابط للمستخدم"""
        try:
            if user_id in self.user_sessions:
                self.user_sessions[user_id]['url_history'] = []
                self.save_user_data()
                return {'success': True, 'message': 'تم مسح سجل الروابط بنجاح'}

            return {'success': False, 'message': 'المستخدم غير موجود'}

        except Exception as e:
            logger.error(f"خطأ في مسح سجل الروابط: {e}")
            return {'success': False, 'message': 'حدث خطأ في مسح السجل'}

    def add_operation_log(self, user_id, log_entry):
        """إضافة سجل عملية جديد"""
        try:
            if user_id not in self.user_sessions:
                return

            if 'operation_logs' not in self.user_sessions[user_id]:
                self.user_sessions[user_id]['operation_logs'] = []

            # الاحتفاظ بآخر 50 سجل فقط
            if len(self.user_sessions[user_id]['operation_logs']) >= 50:
                self.user_sessions[user_id]['operation_logs'].pop(0)

            self.user_sessions[user_id]['operation_logs'].append(log_entry)

        except Exception as e:
            logger.error(f"خطأ في إضافة سجل العملية: {e}")

    def get_operation_logs(self, user_id):
        """الحصول على سجلات العمليات للمستخدم"""
        if user_id in self.user_sessions:
            return self.user_sessions[user_id].get('operation_logs', [])
        return []

    def clear_operation_logs(self, user_id):
        """مسح سجلات العمليات للمستخدم"""
        try:
            if user_id in self.user_sessions:
                self.user_sessions[user_id]['operation_logs'] = []
                self.save_user_data()
                return {'success': True, 'message': 'تم مسح سجل العمليات بنجاح'}

            return {'success': False, 'message': 'المستخدم غير موجود'}

        except Exception as e:
            logger.error(f"خطأ في مسح سجل العمليات: {e}")
            return {'success': False, 'message': 'حدث خطأ في مسح السجل'}
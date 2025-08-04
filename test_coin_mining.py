
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import requests
import time
import json

def extract_data(url):
    """استخراج البيانات من الرابط"""
    print(f"الرابط الأصلي: {url[:100]}...")
    
    # استخراج الجزء المشفر بعد tgWebAppData=
    match = re.search(r'tgWebAppData=([^&]+)', url)
    if match:
        extracted = match.group(1)
        print(f"تم استخراج البيانات: {extracted[:50]}...")
        return extracted
    
    # إذا كان الرابط مجرد بيانات مشفرة فقط
    if url.startswith('user%3D'):
        print(f"الرابط عبارة عن بيانات مشفرة: {url[:50]}...")
        return url
    
    print("❌ لم يتم العثور على بيانات مشفرة في الرابط")
    return None

def coin_get_hourly_tasks(session, init_data):
    """الحصول على عدد المهام لـ COIN"""
    url = f"https://botsmother.com/api/command/OTkz/ODA1OQ==?initData={init_data}"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": url
    }
    
    print(f"جاري الطلب إلى: {url[:80]}...")
    
    try:
        resp = session.get(url, headers=headers, timeout=30)
        print(f"كود الاستجابة: {resp.status_code}")
        print(f"حجم الاستجابة: {len(resp.text)} حرف")
        
        # البحث عن عدد المهام
        match = re.search(r'id="hourly-tasks">(\d+)<', resp.text)
        if match:
            tasks_count = int(match.group(1))
            print(f"✅ عدد المهام المنجزة: {tasks_count}")
            return tasks_count, url
        else:
            print("❌ لم يتم العثور على عدد المهام في الاستجابة")
            # طباعة جزء من الاستجابة للفحص
            print(f"عينة من الاستجابة: {resp.text[:500]}...")
            return None, url
            
    except requests.exceptions.Timeout:
        print("❌ انتهت مهلة الطلب")
        return None, url
    except requests.exceptions.RequestException as e:
        print(f"❌ خطأ في الطلب: {e}")
        return None, url
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
        return None, url

def coin_get_task_id(session, init_data, referer):
    """الحصول على task_id لـ COIN"""
    url = f"https://botsmother.com/api/command/OTkz/ODA2Mw==?initData={init_data}"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
        "Accept": "*/*",
        "Referer": referer,
        "Content-Type": "application/json"
    }
    
    print(f"جاري الحصول على task_id...")
    
    try:
        resp = session.get(url, headers=headers, timeout=30)
        print(f"كود الاستجابة: {resp.status_code}")
        
        try:
            data = resp.json()
            task_id = data.get("task_id")
            if task_id:
                print(f"✅ تم الحصول على task_id: {task_id}")
            else:
                print(f"❌ لا يوجد task_id في الاستجابة: {data}")
            return task_id
        except json.JSONDecodeError:
            print(f"❌ الاستجابة ليست JSON صحيح: {resp.text[:200]}")
            return None
            
    except Exception as e:
        print(f"❌ خطأ في الحصول على task_id: {e}")
        return None

def coin_complete_task(session, init_data, task_id, referer):
    """إكمال المهمة لـ COIN"""
    url = f"https://botsmother.com/api/command/OTkz/ODA2NA==?initData={init_data}&task_id={task_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
        "Accept": "*/*",
        "Referer": referer,
        "Content-Type": "application/json"
    }
    
    print(f"جاري إكمال المهمة...")
    
    try:
        resp = session.get(url, headers=headers, timeout=30)
        print(f"كود الاستجابة: {resp.status_code}")
        
        try:
            result = resp.json()
            print(f"✅ نتيجة إكمال المهمة: {result}")
            return result
        except json.JSONDecodeError:
            print(f"الاستجابة النصية: {resp.text}")
            return resp.text
            
    except Exception as e:
        print(f"❌ خطأ في إكمال المهمة: {e}")
        return None

def test_coin_mining():
    """اختبار تعدين COIN"""
    # الرابط المقدم
    test_url = "https://botsmother.com/api/command/OTkz/ODA1OQ==?tgWebAppStartParam=962731079#tgWebAppData=user%3D%257B%2522id%2522%253A7948727427%252C%2522first_name%2522%253A%2522Ana%2522%252C%2522last_name%2522%253A%2522Baba%2522%252C%2522language_code%2522%253A%2522ar%2522%252C%2522allows_write_to_pm%2522%253Atrue%252C%2522photo_url%2522%253A%2522https%253A%255C%252F%255C%252Ft.me%255C%252Fi%255C%252Fuserpic%255C%252F320%255C%252FTUZOu3ms_T7-g1QACIbQ5O3XG_3XUC9ND-XqIofA274XEh2w5y8ZKWCX6ljrb5dW.svg%2522%257D%26chat_instance%3D-5575783396380320458%26chat_type%3Dsender%26start_param%3D962731079%26auth_date%3D1754278904%26signature%3DfEZvJZrIVkagEK1OLKOKRLJlDojDC9sxjtHzjvf0vFHPpx9Un0x81u0Qjp-f02SqbMfQvrqamJ1LsfInUjwADA%26hash%3D9339617ac03ced18efeaf92185428d2316765d7f8d2be4bbe098facb4a997626&tgWebAppVersion=9.0&tgWebAppPlatform=android&tgWebAppFullscreen=1&tgWebAppThemeParams=%7B%22bg_color%22%3A%22%23212d3b%22%2C%22section_bg_color%22%3A%22%231d2733%22%2C%22secondary_bg_color%22%3A%22%23151e27%22%2C%22text_color%22%3A%22%23ffffff%22%2C%22hint_color%22%3A%22%237d8b99%22%2C%22link_color%22%3A%22%235eabe1%22%2C%22button_color%22%3A%22%2350a8eb%22%2C%22button_text_color%22%3A%22%23ffffff%22%2C%22header_bg_color%22%3A%22%23242d39%22%2C%22accent_text_color%22%3A%22%2364b5ef%22%2C%22section_header_text_color%22%3A%22%2379c4fc%22%2C%22subtitle_text_color%22%3A%22%237b8790%22%2C%22destructive_text_color%22%3A%22%23ee686f%22%2C%22section_separator_color%22%3A%22%230d1218%22%2C%22bottom_bar_bg_color%22%3A%22%23151e27%22%7D"
    
    print("=" * 50)
    print("🧪 اختبار تعدين COIN")
    print("=" * 50)
    
    # استخراج البيانات
    init_data = extract_data(test_url)
    if not init_data:
        print("❌ فشل في استخراج البيانات من الرابط")
        return
    
    # إنشاء session
    session = requests.Session()
    
    print("\n" + "=" * 30)
    print("📊 الخطوة 1: جلب عدد المهام")
    print("=" * 30)
    
    # جلب عدد المهام
    tasks_count, referer = coin_get_hourly_tasks(session, init_data)
    
    if tasks_count is None:
        print("❌ فشل في جلب عدد المهام")
        return
    
    if tasks_count >= 20:
        print(f"⚠️ تم الوصول للحد الأقصى: {tasks_count}/20")
        print("يجب الانتظار حتى إعادة تعيين المهام")
        return
    
    print("\n" + "=" * 30)
    print("🆔 الخطوة 2: جلب task_id")
    print("=" * 30)
    
    # جلب task_id
    task_id = coin_get_task_id(session, init_data, referer)
    
    if not task_id:
        print("❌ فشل في جلب task_id")
        return
    
    print(f"⏳ انتظار 11 ثانية قبل إكمال المهمة...")
    time.sleep(11)
    
    print("\n" + "=" * 30)
    print("✅ الخطوة 3: إكمال المهمة")
    print("=" * 30)
    
    # إكمال المهمة
    result = coin_complete_task(session, init_data, task_id, referer)
    
    if result:
        print("🎉 تم إكمال الاختبار بنجاح!")
        print(f"النتيجة النهائية: {result}")
    else:
        print("❌ فشل في إكمال المهمة")
    
    print("\n" + "=" * 50)
    print("🔍 ملخص الاختبار")
    print("=" * 50)
    print(f"• عدد المهام قبل الاختبار: {tasks_count}")
    print(f"• task_id: {task_id}")
    print(f"• حالة إكمال المهمة: {'نجح' if result else 'فشل'}")
    
    # اختبار إضافي: جلب عدد المهام مرة أخرى للتأكد من الزيادة
    print("\n🔄 جاري التحقق من عدد المهام بعد الإكمال...")
    new_tasks_count, _ = coin_get_hourly_tasks(session, init_data)
    if new_tasks_count is not None:
        print(f"• عدد المهام بعد الاختبار: {new_tasks_count}")
        if new_tasks_count > tasks_count:
            print("✅ تم زيادة عدد المهام بنجاح!")
        else:
            print("⚠️ لم تتم زيادة عدد المهام")

if __name__ == "__main__":
    test_coin_mining()

# Realistic app UI strings — the kind of text that shows up in mobile
# apps, web dashboards, email clients, and Slack/Notion-style products.
#
# These are the "boring" strings that, if mishandled, ship broken UI:
# button labels, error messages, menu items, toast notifications.
# All are constructed for testing; not copied from any specific app.

# Mobile app common strings — buttons, dialogs, navigation.
mobile_buttons = {
    "تسجيل_الدخول": "تسجيل الدخول",
    "إنشاء_حساب": "إنشاء حساب",
    "نسيت_كلمة_المرور": "نسيت كلمة المرور؟",
    "إلغاء": "إلغاء",
    "موافق": "موافق",
    "حفظ": "حفظ",
    "مشاركة": "مشاركة",
    "حذف": "حذف",
    "تعديل": "تعديل",
    "إعدادات": "الإعدادات",
}

# Form validation messages — these are short and user-facing.
form_errors = {
    "required": "هذا الحقل مطلوب",
    "invalid_email": "يرجى إدخال بريد إلكتروني صحيح",
    "password_short": "كلمة المرور يجب أن تكون 8 أحرف على الأقل",
    "password_mismatch": "كلمتا المرور غير متطابقتين",
    "phone_invalid": "يرجى إدخال رقم هاتف صحيح",
}

# Toast / snackbar notifications — single-line status updates.
toasts = {
    "saved": "تم الحفظ بنجاح",
    "sent": "تم الإرسال",
    "deleted": "تم الحذف",
    "copied": "تم النسخ إلى الحافظة",
    "loading": "جارٍ التحميل...",
    "no_internet": "لا يوجد اتصال بالإنترنت",
    "session_expired": "انتهت صلاحية الجلسة، يرجى تسجيل الدخول مرة أخرى",
}

# Email subject lines — must render correctly in inbox lists.
email_subjects = {
    "welcome": "مرحباً بك في خدمة البريد الإلكتروني",
    "receipt": "إيصال الدفع - رقم الطلب #12345",
    "verification": "تأكيد عنوان البريد الإلكتروني",
    "password_reset": "إعادة تعيين كلمة المرور",
    "meeting": "دعوة لاجتماع: مراجعة الربع الرابع",
}

# Slack/Notion-style messages — mixed Arabic + @mentions + #channels.
slack_messages = {
    "mention": "<@mahmoud> راجع المهمة <#arabic-fix|arabic-fix> قبل الاجتماع",
    "code_block": "```python\nfrom arabic_fix import fix\nprint(fix('مرحبا'))\n```",
    "reaction": ":tada: مبروك على الإطلاق! :rocket:",
}

# GitHub-issue-style content — code blocks, references, mixed script.
github_issue = {
    "title": "خطأ في عرض النص العربي على واجهة المستخدم",
    "body": """### وصف المشكلة

عند عرض النص التالي:
```
User 42 logged in from الرياض at 09:30
```
تظهر الأرقام الإنجليزية `42` و `09:30` في الجهة الخطأ من السطر.

### خطوات إعادة الإنتاج
1. سجّل الدخول بحساب يحتوي على اسم عربي
2. افتح لوحة التحكم
3. تحقق من رسالة الترحيب
""",
}

# Dashboard widget labels — short, mixed scripts.
dashboard = {
    "users_online": "المستخدمون النشطون الآن: 1,247",
    "revenue_today": "إيرادات اليوم: ٤٥٬٧٨٢ ر.س",
    "new_signups": "الاشتراكات الجديدة (آخر 24 ساعة): 89",
    "pending_tasks": "المهام المعلقة: 12",
}

# Currency-formatted strings — Arabic currency symbol SAR/EGP/USD etc.
currency_strings = {
    "sar": "١٬٢٣٤٫٥٦ ر.س",
    "egp": "٢٬٥٠٠٫٠٠ ج.م",
    "usd": "$ 1,234.56",
    "mixed": "السعر: ١٥٠٫٠٠ ر.س (≈ $39.99)",
}
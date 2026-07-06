# Edge cases — text inputs that historically caused bugs in BiDi/reshape
# libraries. Every entry here was either a real bug report or a "found
# in the wild" production incident.

# Single-letter Arabic — should not be reshaped to presentation forms
# in a way that breaks recognizability.
single_letters = ["ا", "ب", "ت", "ث", "ج", "ح", "خ", "د", "ذ", "ر", "ز", "س"]

# All four Arabic ligatures the reshaper knows about.
ligatures = [
    ("لا", "ل+ا ligature"),  # laam-alef
    ("ﷲ", "Allah (U+FDF2)"),  # Allah ligature
    ("ﷺ", "sallallahu alayhi wasallam"),  # ﷺ
    ("ﷻ", "jal-lajalouhou"),  # ﷻ
]

# RTL marks / format characters — must survive without being reshaped.
format_chars = {
    "rle": "\u202Bمتن عربي\u202C",
    "rlo": "\u202Eنص من اليمين لليسار\u202C",
    "lre": "\u202Aleft-to-right override\u202C",
    "lro": "\u202D12345\u202C",
    "isolate_ltr": "\u2066ABC\u2069",
    "isolate_rtl": "\u2067عربي\u2069",
}

# Combining marks that the bidi algorithm cares about.
combining = {
    "fatha": "\u064E",        # َ
    "kasra": "\u0650",        # ِ
    "damma": "\u064F",        # ُ
    "sukun": "\u0652",        # ْ
    "shadda": "\u0651",       # ّ
    "tanween_fath": "\u064B", # ً
    "tanween_kasr": "\u064D", # ٍ
    "tanween_damm": "\u064C", # ٌ
}

# Whitespace-only edge cases.
whitespace = [
    "",                  # empty
    " ",                 # single ASCII space
    "\u00A0",            # non-breaking space
    "\u200B",            # zero-width space (Arabic web bug source)
    "\u200C",            # zero-width non-joiner (ZWNJ)
    "\u200D",            # zero-width joiner (ZWJ)
    "\u200E",            # LTR mark
    "\u200F",            # RTL mark
    "\uFEFF",            # BOM / zero-width no-break space
    "   ",               # multiple ASCII spaces
    "\t\n\r ",           # mixed control whitespace
]

# Pure-Latin strings — must pass through unchanged.
pure_latin = [
    "Hello, World!",
    "user@example.com",
    "https://example.com/path?q=1",
    "User 42",
    "12345",
    "abc XYZ",
    "Lorem ipsum dolor sit amet",
    "café résumé naïve",  # Latin with diacritics — must NOT be reshaped
]

# Numbers — different scripts / formats.
numbers = {
    "western": "1234567890",
    "arabic_indic": "١٢٣٤٥٦٧٨٩٠",       # U+0660..U+0669
    "extended_arabic": "۰۱۲۳۴۵۶۷۸۹",     # Persian/Urdu digits U+06F0..U+06F9
    "decimal_western": "3.14159",
    "decimal_arabic": "٣٫١٤١٥٩",
    "thousand_sep_western": "1,234,567",
    "thousand_sep_arabic": "١٬٢٣٤٬٥٦٧",   # U+066C Arabic thousands separator
}

# Text containing emojis — must not break reshape.
with_emoji = [
    "مرحبا 👋",
    "🇸🇦 العلم السعودي",  # flag emoji + Arabic
    "القهوة ☕ صباحاً",
    "✅ تم بنجاح ✓",
]

# Bidi-isolated runs (real bug source).
bidi_isolated = [
    "Contact: user@example.com — مرحبا",
    "Version 1.0.0 من arabic-fix",
    "في 2024-01-15 الساعة 09:30",
    "قرأ الكتاب (123 صفحة) في يومين",
    "نص عربي + English text + 123 + نص",
]

# Path strings — forward/back slash ambiguity in mixed-script.
paths = {
    "unix_arabic_filename": "/Users/mahmoud/ملفات/document.txt",
    "windows_arabic": "C:\\Users\\mahmoud\\مستندات\\file.docx",
    "url_with_arabic": "https://example.com/مقالات/المقدمة",
}

# Very long line — stress test for reshape performance.
long_arabic = " ".join(["السلام عليكم"] * 100)  # 100x repetition

# Empty multiline content.
multiline = {
    "single_newline": "السطر الأول\nالسطر الثاني",
    "blank_lines": "السطر الأول\n\n\nالسطر الثاني",
    "windows_line_endings": "السطر الأول\r\nالسطر الثاني\r\n",
    "mixed_endings": "السطر الأول\r\nالسطر الثاني\nالسطر الثالث\r",
}

# Control characters — must not crash.
control_chars = "Hello\x00World\x07\x08\tمرحبا"
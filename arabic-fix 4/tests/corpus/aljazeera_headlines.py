# Al Jazeera-style Arabic news headlines — realistic mixed-script content.
#
# These are constructed in the style of real Al Jazeera headlines to
# exercise the library on:
#   - mixed Arabic + Latin (organization names, English transliteration)
#   - dates / numbers (Eastern Arabic-Indic vs Western digits)
#   - punctuation (Arabic comma ، question mark ؟)
#   - proper nouns with diacritics
#
# Sources of style: aljazeera.net headlines (Arabic section). The text
# below is constructed for testing; it is not copied from any specific
# article.

# Mixed Arabic + English organization names — typical breaking-news headline.
breaking_news = "عاجل: قمة G20 تنعقد في الرياض الأسبوع المقبل"

# Political headline — person name + city + date.
summit = "الرئيس يلتقي نظيره الفرنسي في باريس يوم 15 نوفمبر"

# Numbers in Eastern Arabic-Indic digits.
election = "أكثر من ٧٫٥ مليون ناخب شاركوا في الانتخابات التشريعية"

# Mixed Latin/digit embed inside Arabic sentence — common for sports news.
sports = "حقق المنتخب الوطني فوزاً تاريخياً 3-1 أمام نظيره البرازيلي"

# Economic headline — currency symbols + percent.
economy = "ارتفع سعر صرف الدولار بنسبة 2.5% أمام الجنيه المصري"

# A longer lede paragraph — multiple sentences.
lede = "أعلنت وزارة الصحة اليوم الأحد عن تسجيل 1423 حالة إصابة جديدة بفيروس كورونا خلال الأربع وعشرين ساعة الماضية. ودعت الوزارة المواطنين إلى الالتزام بالإجراءات الاحترازية وارتداء الكمامات في الأماكن العامة."

# Question-form headline.
question = "هل ستُعقد المحادثات النووية الأسبوع المقبل في فيينا؟"

# Date with Arabic numerals and Latin month abbreviation (Western style).
date_mixed = "موعد المباراة: 25/12/2024 الساعة 8:30 مساءً بتوقيت مكة المكرمة"

# Short breaking-news banner (like the rotating headline bar).
banner = "عاجل | ارتفاع عدد ضحايا الزلزال إلى 1200 قتيل وأكثر من 3000 مصاب"
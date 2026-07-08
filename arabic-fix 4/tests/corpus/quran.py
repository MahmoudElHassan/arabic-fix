# Quran samples — public-domain Arabic verses used to stress-test
# tashkeel preservation and shaping on religious text.
#
# Sources:
#   - Al-Fatiha (The Opening), Surah 1, all 7 verses
#   - Ayat al-Kursi (The Throne), Surah 2 verse 255
#   - Al-Ikhlas (Sincerity), Surah 112, all 4 verses
#
# All verses carry full tashkeel (harakat). The library must preserve
# every diacritic — the eval cases / docs/before-after.md both
# reference these.
#
# These are religious texts in the public domain (Quran has no
# copyright per Islamic scholarly consensus). Included as test
# fixtures, not as user-facing documentation.

# Al-Fatiha — Surah 1, opening chapter of the Quran. The single most
# recited text in Arabic.
الفاتحة = """بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ
الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ
الرَّحْمَٰنِ الرَّحِيمِ
مَالِكِ يَوْمِ الدِّينِ
إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ
اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ
صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ"""

# Ayat al-Kursi — Surah 2:255. Famous long verse with full tashkeel,
# includes the word ﷲ (Allah ligature).
آية_الكرسي = "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ ۚ لَا تَأْخُذُهُ سِنَةٌ وَلَا نَوْمٌ ۚ لَّهُ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ ۗ مَن ذَا الَّذِي يَشْفَعُ عِندَهُ إِلَّا بِإِذْنِهِ ۚ يَعْلَمُ مَا بَيْنَ أَيْدِيهِمْ وَمَا خَلْفَهُمْ ۖ وَلَا يُحِيطُونَ بِشَيْءٍ مِّنْ عِلْمِهِ إِلَّا بِمَا شَاءَ ۚ وَسِعَ كُرْسِيُّهُ السَّمَاوَاتِ وَالْأَرْضَ ۖ وَلَا يَئُودُهُ حِفْظُهُمَا ۚ وَهُوَ الْعَلِيُّ الْعَظِيمُ"

# Al-Ikhlas — Surah 112. Short surah with full tashkeel.
الإخلاص = """قُلْ هُوَ اللَّهُ أَحَدٌ
اللَّهُ الصَّمَدُ
لَمْ يَلِدْ وَلَمْ يُولَدْ
وَلَمْ يَكُن لَّهُ كُفُوًا أَحَدٌ"""
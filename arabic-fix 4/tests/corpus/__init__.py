# Real Arabic corpus fixtures.
#
# Modules (one per topic, sibling of this file):
#   - quran: Quran samples (Al-Fatiha, Ayat al-Kursi, Al-Ikhlas).
#   - aljazeera_headlines: Al Jazeera-style news headlines.
#   - app_ui: Mobile / web / Slack / GitHub UI strings.
#   - edge_cases: RTL marks, format chars, emoji, paths, control chars.
#
# Usage in tests:
#   from corpus.quran import آية_الكرسي
#   from corpus.aljazeera_headlines import breaking_news
#
# All text is constructed for testing and falls under fair use; Quran
# verses are public domain (no copyright per scholarly consensus).
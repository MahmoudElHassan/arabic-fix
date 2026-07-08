# Font stack for Arabic UI

> Pick fonts from this list in this order. All listed fonts have full
> Arabic + Latin + tashkeel coverage. Avoid system defaults — most
> operating systems pick a poor fallback (or none at all) for Arabic.

## Web (free + OFL-licensed)

| Font | Weight | Best for | URL |
|---|---|---|---|
| **Tajawal** | 200–900 | Display + body, modern SaaS | fonts.google.com/specimen/Tajawal |
| **Noto Naskh Arabic** | 400–700 | Body, long-form reading | fonts.google.com/noto/specimen/Noto+Naskh+Arabic |
| **Amiri** | 400–700 | Editorial, classical | fonts.google.com/specimen/Amiri |
| **Cairo** | 200–900 | UI / dashboards | fonts.google.com/specimen/Cairo |
| **Vazirmatn** | 100–900 | UI, monospace pairing | github.com/rastikerdar/vazirmatn |
| **IBM Plex Sans Arabic** | 100–700 | Enterprise / corporate | github.com/IBM/plex |

## Editorial / print

| Font | Best for |
|---|---|
| **Scheherazade New** | Long-form Arabic text, classical books |
| **Reem Kufi** | Kufi-style headlines, branding |
| **Aref Ruqaa** | Calligraphic accents |

## Monospace (for code)

| Font | Notes |
|---|---|
| **Fira Code Arabic** | Programming ligatures + Arabic glyphs |
| **Vazirmatn Mono** | Lightweight mono with full Arabic |

## Rules of thumb

1. Always declare BOTH Arabic and Latin families in one stack. Browsers
   fallback per-character so a single `font-family` is correct.

   ```css
   font-family: "Tajawal", "Inter", system-ui, sans-serif;
   /* Tajawal handles Arabic glyphs; Inter handles Latin; the rest
      catches platforms where neither is installed. */
   ```

2. Variable fonts win. Load one `.woff2` with a weight axis, not 6 files.

3. Don't load Arabic fonts via `@font-face` for a *small* Arabic
   fragment inside an English page. Use the system font — it's already
   tuned for that OS.

4. Test with a *real* Arabic paragraph, not "Hello World"-equivalent
   `مرحبا`. Cursive connections and ligatures only show up in
   multi-letter words like `مكتبة` and `العربية`.

5. Test with diacritics ON: `مَرْحَبَا بِالْعَالَمِ`. Most font bugs
   emerge with combining marks.

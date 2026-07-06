# RTL layout rules for designers

> Twelve rules. Memorize the ones that bite you most (3, 4, 8, 11), refer
> back to the rest.

## 1. Use logical CSS properties

```css
/* BAD */
padding-left: 16px;
margin-right: 8px;
border-left: 1px solid #ccc;
text-align: left;

/* GOOD */
padding-inline-start: 16px;
margin-inline-end: 8px;
border-inline-start: 1px solid #ccc;
text-align: start;
```

`inline-start` and `inline-end` resolve automatically with `direction`.
If you find yourself typing `left` or `right` for a property that has a
logical alternative, change it.

## 2. Set direction at the root, not per component

```html
<html dir="rtl" lang="ar">    <!-- whole doc is RTL -->
  <body>
    <div dir="ltr">           <!-- explicit LTR island for the price column -->
      <span class="price">$4.99</span>
    </div>
  </body>
</html>
```

Nested overrides should be rare and explicit.

## 3. Mirror direction-implying icons

Anything that "goes somewhere" needs mirroring:

| Icon | Mirror? |
|---|---|
| → chevron, arrow, back, next, forward | YES |
| ⏵ play | YES |
| ⏸ pause | NO |
| ↑ upload (cloud up) | NO |
| ⬇ download | NO |
| 🔍 search | NO |
| 🎚 progress bar thumb | YES |
| ↪ share-internal | YES |
| 🪞 brand logo that has directionality | YES (sometimes — review case by case) |

## 4. Numbers and dates stay LTR — usually

Arabic users understand Latin digits `0-9` perfectly. Switching to
`٠-٩` is a *content* decision per product, not a layout rule.

```html
<p>لديك <bdi>3</bdi> رسائل جديدة</p>
```

`<bdi>` isolates the digit so BiDi doesn't smear it into the Arabic run.

## 5. Punctuation in Arabic

| Symbol | Position | Notes |
|---|---|---|
| ؟ `?` | RTL — appears on the left visually | Use Arabic question mark `؟` inside Arabic runs |
| ، `,` | RTL — appears on the left visually | Use Arabic comma `،` inside Arabic runs |
| ; ، | RTL | Use Arabic semicolon |
| « » | RTL | Use Arabic-style quotes `«...»` |

## 6. Mix LTR runs with `<bdi>` not naked HTML

```html
<!-- BAD -->
<p dir="rtl">مرحبا user@example.com</p>
<!-- rendering depends on browser heuristics -->

<!-- GOOD -->
<p dir="rtl">
  مرحبا <bdi>user@example.com</bdi>
</p>
```

`<bdi>` = "BiDirectional Isolate" — keeps the run from being
re-ordered.

## 7. Forms

- Placeholder text alignment auto-handles by `direction`, but verify
  with a real Arabic placeholder, not the English default.
- Required-field asterisks: `*` stays at the *visual* right end of an
  Arabic label, not after the text.
- Truncation indicator `…` is direction-neutral.

## 8. Letter-spacing is forbidden in Arabic runs

```css
.ar { letter-spacing: 0.05em; }   /* breaks baseline */
.ar { word-spacing: 0.05em; }      /* correct alternative */
```

## 9. Cursors

- `cursor: text` — neutral
- `cursor: pointer` — neutral
- Never set custom cursors that point a direction unless you also mirror.

## 10. Hover / focus / press states

Ripples expand from the *reading edge*. In RTL, that's the right.
Material UI and Apple HIG both expect this.

## 11. Animations reverse with direction

```css
.slide-in { animation: slide-from-start 200ms ease; }
@keyframes slide-from-start {
  from { transform: translateX(-100%); }   /* RTL = from the right = negative */
  to   { transform: translateX(0); }
}
```

Or use `translateX` with a logical property equivalent that auto-reverses.

## 12. Test with these 4 sentences

If your layout survives these, it'll survive most of the real world:

1. Pure Arabic, no diacritics:
   `مرحبا بالعالم`
2. Pure Arabic, with full tashkeel:
   `مَرْحَبًا بِالْعَالَمِ`
3. Mixed BiDi: digits + Arabic + Latin:
   `User 42 logged in from الرياض at 09:30 today`
4. LTR island inside RTL:
   `مرحبا (user@example.com) كيف حالك؟`

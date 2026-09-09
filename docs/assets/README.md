# Assets

Statyczne assety dla README i dokumentacji.

## Pliki

1. `logo.svg` logo projektu. Package box z sygnałem live tracking. Kolory zgodne z paletą (`#38E0C8` mint cyan, `#4FCE85` good green, `#0A0F1C` deep midnight).
2. `hero.png` (do dodania). Screenshot hero z artifact wizualnego. Rozmiar 880 px szerokości, 2x DPI dla retina.

## Jak wygenerować hero.png

1. Otwórz artifact: https://claude.ai/code/artifact/ee29def7-0999-4098-9571-49c9e68f6f1c
2. W przeglądarce (Chrome DevTools): Device Toolbar → 1760 px width (2x 880).
3. Screenshot obszaru hero (od góry do końca metrics band). Zapisz jako `hero.png`.
4. Kompresja: TinyPNG albo `pngquant --quality=80-95 hero.png -o hero.png`.
5. Cel: poniżej 300 KB, ładne w README na wszystkich urządzeniach.

## Social preview

GitHub Settings → Social preview wymaga obrazu 1280x640 px. Wygeneruj oddzielnie z artifact, tylko sam hero plus nazwa projektu, mniej detali dla czytelności w kaflu LinkedIn.

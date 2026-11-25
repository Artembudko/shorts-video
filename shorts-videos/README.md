# Shorts-відео (стиль @RicksClips3000), російською, з озвучкою

Вертикальні 1080x1920 відео, 30 fps: векторна анімація (SVG -> rsvg-convert -> PIL), субтитри, музика, SFX.

## Структура
- `engine/art.py`, `art3.py`, `scenery.py` — спрайти, фони
- `engine/make2.py` — движок + відео про эму (`python3 make2.py preview|render`)
- `engine/make3.py` — відео про кобр (`python3 make3.py preview|render`)
- `examples/*_script_ru.txt` — тексти для озвучки
- `CLAUDE.md` — інструкції для Claude

Запускати з папки, де лежить `durs.json` (час сцен), результат: `tmp.mp4`, звук: `a.wav`.
Потрібні: python3, numpy, pillow, opencv-python, ffmpeg, librsvg (rsvg-convert), шрифт Inter-Black.

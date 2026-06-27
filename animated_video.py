from PIL import Image

# ✅ FIX ANTIALIAS ERROR
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips
)
from PIL import ImageDraw, ImageFont
import numpy as np
import asyncio
import edge_tts
import os
import re

from utils.llm_answer import client

# ── Canvas dimensions ──────────────────────────────────────────
SLIDE_W, SLIDE_H = 1280, 720

# ── Colours ────────────────────────────────────────────────────
BG_TOP         = (13,  17,  26)
BG_BOT         = (10,  14,  22)
TITLE_COLOR    = (0,   200, 255)   # cyan
BULLET_COLOR   = (226, 232, 245)   # near-white
BULLET_DIM     = (148, 163, 184)   # softer for 4th/5th bullets
ACCENT_COLOR   = (168,  85, 247)   # purple bar
DIVIDER_COLOR  = (30,   50,  80)
NUMBER_COLOR   = (60,   85, 120)

# ── Safe zone ──────────────────────────────────────────────────
PAD_L   = 90      # left padding (after accent bar)
PAD_R   = 90      # right padding
PAD_T   = 55      # top of title
PAD_B   = 50      # bottom safe zone height

USABLE_W = SLIDE_W - PAD_L - PAD_R    # 1100 px
USABLE_H = SLIDE_H - PAD_T - PAD_B    # 615 px


# ── Font loader ────────────────────────────────────────────────
def load_fonts():
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return (
                    ImageFont.truetype(path, 68),   # title
                    ImageFont.truetype(path, 44),   # body
                    ImageFont.truetype(path, 28),   # counter
                )
            except Exception:
                continue
    fb = ImageFont.load_default()
    return fb, fb, fb


# ── Text helpers ───────────────────────────────────────────────
def text_w(draw, txt, font):
    try:
        bb = draw.textbbox((0, 0), txt, font=font)
        return bb[2] - bb[0]
    except Exception:
        return len(txt) * 22

def text_h(draw, txt, font):
    try:
        bb = draw.textbbox((0, 0), txt, font=font)
        return bb[3] - bb[1]
    except Exception:
        return 36

def wrap_px(draw, text, font, max_px):
    """Word-wrap to fit within max_px width."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if text_w(draw, test, font) <= max_px:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [text]


# ── Background gradient ────────────────────────────────────────
def draw_background(draw):
    """Simple top-to-bottom vertical gradient."""
    for y in range(SLIDE_H):
        t   = y / SLIDE_H
        r   = int(BG_TOP[0] + (BG_BOT[0]-BG_TOP[0]) * t)
        g   = int(BG_TOP[1] + (BG_BOT[1]-BG_TOP[1]) * t)
        b   = int(BG_TOP[2] + (BG_BOT[2]-BG_TOP[2]) * t)
        draw.line([(0, y), (SLIDE_W, y)], fill=(r, g, b))


# ── LLM slide script ───────────────────────────────────────────
def generate_slide_content(text):
    prompt = f"""Convert the text below into a teaching slide.

Output format (exactly):
Line 1: Title (5-8 words, no trailing punctuation)
Lines 2-6: Bullet points (one per line, 6-12 words each, no bullet symbols)

Rules:
- Do NOT add •, -, *, #, numbers or any prefix
- Each bullet must be a complete, informative idea
- Cover the key concepts fully
- Minimum 4 bullets, maximum 6 bullets

Text:
{text}
"""
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return response.choices[0].message.content.strip()


# ── Voice ──────────────────────────────────────────────────────
async def generate_voice(text):
    communicate = edge_tts.Communicate(
        text,
        voice="en-US-GuyNeural",
        rate="+5%",
        pitch="+0Hz"
    )
    await communicate.save("audio.mp3")


# ── Draw one slide ─────────────────────────────────────────────
def draw_slide(title, bullets, slide_num, total,
               title_font, body_font, num_font):

    img  = Image.new("RGB", (SLIDE_W, SLIDE_H), BG_TOP)
    draw = ImageDraw.Draw(img)

    # gradient bg
    draw_background(draw)

    # subtle top glow strip
    for i in range(6):
        alpha = max(0, 30 - i*5)
        draw.rectangle([(0, i), (SLIDE_W, i+1)], fill=(0, 200, 255))

    # left accent bar
    draw.rectangle([(50, PAD_T), (60, SLIDE_H - PAD_B)], fill=ACCENT_COLOR)

    # ── Title ────────────────────────────────────────────────
    clean_title = re.sub(r'^[\s•\-*#\d.]+', '', title).strip()
    title_lines = wrap_px(draw, clean_title, title_font, USABLE_W)

    y = PAD_T
    title_line_h = text_h(draw, "Ag", title_font)
    for ln in title_lines[:2]:
        draw.text((PAD_L, y), ln, font=title_font, fill=TITLE_COLOR)
        y += title_line_h + 8

    # divider
    y += 12
    draw.rectangle([(PAD_L, y), (PAD_L + USABLE_W, y + 2)], fill=DIVIDER_COLOR)
    y += 22

    # ── Bullets ───────────────────────────────────────────────
    # Figure out how much vertical space is left and distribute evenly
    space_left   = (SLIDE_H - PAD_B) - y
    body_line_h  = text_h(draw, "Ag", body_font)
    dot_r        = 9       # bullet dot radius
    dot_gap      = 20      # gap from dot to text
    text_x       = PAD_L + dot_r * 2 + dot_gap
    text_w_max   = SLIDE_W - PAD_R - text_x

    # Estimate total lines needed
    all_wrapped = []
    for b in bullets:
        clean = re.sub(r'^[\s•\-*·\d.]+', '', b).strip()
        if clean:
            all_wrapped.append(wrap_px(draw, clean, body_font, text_w_max))

    if not all_wrapped:
        return img

    total_lines = sum(len(w) for w in all_wrapped)
    # Gap between bullets: distribute remaining space
    min_gap      = 16
    extra_space  = max(0, space_left - total_lines * (body_line_h + 6) - len(all_wrapped) * min_gap)
    between_gap  = min_gap + int(extra_space / max(len(all_wrapped), 1))
    between_gap  = min(between_gap, 70)   # cap so it doesn't look weird

    for idx, wrapped_lines in enumerate(all_wrapped):
        if y + body_line_h > SLIDE_H - PAD_B:
            break

        # dot colour cycles through accent palette
        dot_colors = [ACCENT_COLOR, (0,200,255), (255,107,157), (34,197,94)]
        dot_color  = dot_colors[idx % len(dot_colors)]

        # vertical centre of first line
        dot_cy = y + body_line_h // 2
        draw.ellipse(
            [(PAD_L, dot_cy - dot_r),
             (PAD_L + dot_r*2, dot_cy + dot_r)],
            fill=dot_color
        )

        # choose colour: first 3 full brightness, rest dimmer
        line_color = BULLET_COLOR if idx < 3 else BULLET_DIM

        for li, ln in enumerate(wrapped_lines):
            if y + body_line_h > SLIDE_H - PAD_B:
                break
            draw.text((text_x, y), ln, font=body_font, fill=line_color)
            y += body_line_h + 6

        y += between_gap

    # ── Slide counter ─────────────────────────────────────────
    counter = f"{slide_num} / {total}"
    cw = text_w(draw, counter, num_font)
    draw.text(
        (SLIDE_W - PAD_R - cw, SLIDE_H - PAD_B + 14),
        counter,
        font=num_font,
        fill=NUMBER_COLOR
    )

    # bottom accent line
    draw.rectangle(
        [(PAD_L, SLIDE_H - 12), (SLIDE_W - PAD_R, SLIDE_H - 8)],
        fill=(0, 200, 255)
    )

    return img


# ── Main entry ─────────────────────────────────────────────────
def create_animated_video(text):
    if os.path.exists("audio.mp3"):
        os.remove("audio.mp3")

    asyncio.run(generate_voice(text))

    audio          = AudioFileClip("audio.mp3")
    audio_duration = audio.duration

    parts = [p.strip() for p in text.split(".") if p.strip()]
    if not parts:
        parts = [text]

    title_font, body_font, num_font = load_fonts()

    total_words = sum(len(p.split()) for p in parts) or 1
    clips       = []
    total_parts = len(parts)

    for slide_num, part in enumerate(parts, start=1):
        clean = re.sub(r'[^a-zA-Z0-9,.\s!?]', '', part)[:250].strip()
        if not clean:
            continue

        slide_raw = generate_slide_content(clean)
        lines     = [l for l in slide_raw.split("\n") if l.strip()]

        title   = lines[0] if lines else "Key Concept"
        bullets = lines[1:7] if len(lines) > 1 else ["Key information from document"]

        img       = draw_slide(title, bullets, slide_num, total_parts,
                               title_font, body_font, num_font)
        img_array = np.array(img)

        words_count = len(clean.split())
        duration    = max(2.5, (words_count / total_words) * audio_duration)

        clip = (
            ImageClip(img_array)
            .set_duration(duration)
            .fadein(0.35)
            .fadeout(0.35)
        )
        clips.append(clip)

    if not clips:
        return None

    final = concatenate_videoclips(clips, method="compose")
    final = final.set_audio(audio)
    final = final.set_duration(audio_duration)

    final.write_videofile(
        "animated.mp4",
        fps=30,
        codec="libx264",
        bitrate="5000k",
        audio_codec="aac",
        logger=None
    )

    return "animated.mp4"
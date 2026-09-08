import os
import sys
import math
import subprocess
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

# ---------------------------------------------------------
# Easing & Math Utilities
# ---------------------------------------------------------
def clamp(val, low=0.0, high=1.0):
    return max(low, min(high, float(val)))

def ease_out_cubic(t):
    t = clamp(t)
    return 1.0 - (1.0 - t) ** 3

def ease_in_cubic(t):
    t = clamp(t)
    return t ** 3

def ease_out_back(t, s=1.35):
    t = clamp(t)
    t = t - 1.0
    return 1.0 + (s + 1.0) * (t ** 3) + s * (t ** 2)

def lerp(a, b, t):
    return a + (b - a) * t

# ---------------------------------------------------------
# Graphics Utilities
# ---------------------------------------------------------
def create_studio_background(w, h):
    """Generates an ultra-premium luxury studio lighting background."""
    arr = np.zeros((h, w, 3), dtype=np.float32)
    for y in range(h):
        ratio = y / float(h)
        arr[y, :, 0] = 255 - ratio * 12
        arr[y, :, 1] = 255 - ratio * 10
        arr[y, :, 2] = 255 - ratio * 6
        
    cx, cy = w / 2.0, h * 0.44
    max_dist = math.hypot(w / 2.0, h / 2.0)
    y_coords, x_coords = np.ogrid[:h, :w]
    dist = np.hypot(x_coords - cx, y_coords - cy)
    glow = np.clip(1.0 - (dist / max_dist), 0, 1) ** 1.8 * 22
    
    arr[:, :, 0] = np.clip(arr[:, :, 0] + glow, 0, 255)
    arr[:, :, 1] = np.clip(arr[:, :, 1] + glow, 0, 255)
    arr[:, :, 2] = np.clip(arr[:, :, 2] + glow, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))

def add_drop_shadow(img, blur_radius=22, offset=(8, 14), shadow_alpha=0.28):
    """Adds a soft Gaussian drop shadow to an RGBA image."""
    w, h = img.size
    pad_x = blur_radius * 2 + abs(offset[0])
    pad_y = blur_radius * 2 + abs(offset[1])
    shadow = Image.new('RGBA', (w + pad_x, h + pad_y), (0, 0, 0, 0))
    alpha = img.split()[-1]
    
    black = Image.new('RGBA', img.size, (0, 0, 0, 0))
    alpha_arr = (np.array(alpha).astype(float) * shadow_alpha).astype(np.uint8)
    black.putalpha(Image.fromarray(alpha_arr))
    
    paste_x = blur_radius + max(0, offset[0])
    paste_y = blur_radius + max(0, offset[1])
    shadow.paste(black, (paste_x, paste_y), black)
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))
    
    img_x = blur_radius - min(0, offset[0])
    img_y = blur_radius - min(0, offset[1])
    shadow.paste(img, (img_x, img_y), img)
    return shadow

def load_and_trim(path):
    im = Image.open(path).convert('RGBA')
    bbox = im.getbbox()
    if bbox:
        return im.crop(bbox)
    return im

def scale_asset(img, target_w=None, target_h=None):
    if img is None:
        return None
    w, h = img.size
    if target_w is not None and target_h is None:
        target_h = int(h * (target_w / float(w)))
    elif target_h is not None and target_w is None:
        target_w = int(w * (target_h / float(h)))
    elif target_w is None and target_h is None:
        return img
    if w == int(target_w) and h == int(target_h):
        return img
    return img.resize((max(1, int(target_w)), max(1, int(target_h))), Image.BILINEAR)

def draw_element(base_img, img, cx, cy, target_w=None, target_h=None, rot=0.0, alpha=1.0):
    if alpha <= 0.001:
        return
    w, h = img.size
    if target_w is not None and target_h is None:
        target_h = int(h * (target_w / float(w)))
    elif target_h is not None and target_w is None:
        target_w = int(w * (target_h / float(h)))
    elif target_w is None and target_h is None:
        target_w, target_h = w, h
        
    if w != int(target_w) or h != int(target_h):
        scaled = img.resize((max(1, int(target_w)), max(1, int(target_h))), Image.BILINEAR)
    else:
        scaled = img
        
    if abs(rot) > 0.01:
        rotated = scaled.rotate(rot, resample=Image.BILINEAR, expand=True)
    else:
        rotated = scaled
        
    if alpha < 0.999:
        r, g, b, a = rotated.split()
        a = a.point(lambda p: int(p * alpha))
        rotated = Image.merge('RGBA', (r, g, b, a))
        
    px = int(cx - rotated.width / 2.0)
    py = int(cy - rotated.height / 2.0)
    base_img.paste(rotated, (px, py), rotated)

# ---------------------------------------------------------
# Master Render Function
# ---------------------------------------------------------
def render_video(output_filename, width, height, is_vertical_9x16=False):
    print(f"\n=======================================================")
    print(f"Rendering: {output_filename} ({width}x{height})")
    print(f"=======================================================")
    
    fps = 30
    total_frames = 420  # exactly 14.0 seconds @ 30fps
    
    # 1. Load and trim all assets
    print("Loading trimmed assets...")
    logo = load_and_trim('assets/mod_sole_logo.png')
    htitle = load_and_trim('assets/header_title.png')
    urdu = load_and_trim('assets/urdu_tagline.png')
    eng = load_and_trim('assets/english_tagline.png')
    seal = load_and_trim('assets/heritage_seal.png')
    seal_shadow = add_drop_shadow(seal, blur_radius=18, offset=(0, 10), shadow_alpha=0.22)
    cta = load_and_trim('assets/outro_cta.png')
    contacts = load_and_trim('assets/contact_badges.png')
    contacts_shadow = add_drop_shadow(contacts, blur_radius=20, offset=(0, 10), shadow_alpha=0.25)
    
    cards = {
        "Lug":     add_drop_shadow(load_and_trim('assets/card_lug.png')),
        "Formal":  add_drop_shadow(load_and_trim('assets/card_formal.png')),
        "Sneaker": add_drop_shadow(load_and_trim('assets/card_sneaker.png')),
        "Comfort": add_drop_shadow(load_and_trim('assets/card_comfort.png')),
        "Heel":    add_drop_shadow(load_and_trim('assets/card_heel.png')),
    }
    
    bg_template = create_studio_background(width, height)
    
    # Coordinates configuration
    if not is_vertical_9x16:
        # 1080 x 1350 (4:5)
        # Scene 1 & 2
        header_logo_y = 80
        header_logo_w = 260
        header_title_y = 230
        header_title_w = 620
        
        cards_cfg = {
            "Sneaker": {"x": 285, "y": 560, "w": 440, "rot": -7.0, "start_f": 125},
            "Comfort": {"x": 795, "y": 570, "w": 440, "rot": 7.0,  "start_f": 160},
            "Heel":    {"x": 255, "y": 1040, "w": 440, "rot": -5.0, "start_f": 195},
            "Formal":  {"x": 825, "y": 1050, "w": 440, "rot": 5.0,  "start_f": 95},
            "Lug":     {"x": 540, "y": 800,  "w": 540, "rot": -12.0, "start_f": 55}, # Hero Center
        }
        
        # Scene 3 (Heritage)
        seal_y = 420
        seal_w = 380
        urdu_s3_y = 750
        urdu_s3_w = 780
        eng_s3_y = 900
        eng_s3_w = 760
        
        # Scene 4 (Outro)
        outro_logo_y = 350
        outro_logo_w = 560
        outro_urdu_y = 530
        outro_urdu_w = 620
        outro_cta_y = 710
        outro_cta_w = 780
        outro_contacts_y = 980
        outro_contacts_w = 940
    else:
        # 1080 x 1920 (9:16)
        header_logo_y = 150
        header_logo_w = 320
        header_title_y = 340
        header_title_w = 720
        
        cards_cfg = {
            "Sneaker": {"x": 285, "y": 780,  "w": 490, "rot": -7.0, "start_f": 125},
            "Comfort": {"x": 795, "y": 790,  "w": 490, "rot": 7.0,  "start_f": 160},
            "Heel":    {"x": 255, "y": 1390, "w": 490, "rot": -5.0, "start_f": 195},
            "Formal":  {"x": 825, "y": 1400, "w": 490, "rot": 5.0,  "start_f": 95},
            "Lug":     {"x": 540, "y": 1090, "w": 610, "rot": -12.0, "start_f": 55},
        }
        
        seal_y = 560
        seal_w = 460
        urdu_s3_y = 980
        urdu_s3_w = 880
        eng_s3_y = 1170
        eng_s3_w = 860
        
        outro_logo_y = 470
        outro_logo_w = 660
        outro_urdu_y = 690
        outro_urdu_w = 720
        outro_cta_y = 910
        outro_cta_w = 880
        outro_contacts_y = 1270
        outro_contacts_w = 980

    # Pre-scale static elements once to eliminate thousands of resizes inside loop
    for cname, cfg in cards_cfg.items():
        cards[cname] = scale_asset(cards[cname], target_w=cfg["w"])
    htitle = scale_asset(htitle, target_w=header_title_w)
    urdu_s3 = scale_asset(urdu, target_w=urdu_s3_w)
    eng_s3 = scale_asset(eng, target_w=eng_s3_w)
    outro_urdu = scale_asset(urdu, target_w=outro_urdu_w)
    outro_cta = scale_asset(cta, target_w=outro_cta_w)

    # Start ffmpeg
    cmd = [
        'ffmpeg',
        '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-pix_fmt', 'rgb24',
        '-s', f'{width}x{height}',
        '-r', str(fps),
        '-i', '-',
        '-i', 'bgm.aac',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'ultrafast',
        '-tune', 'zerolatency',
        '-threads', '0',
        '-crf', '20',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-shortest',
        output_filename
    ]
    
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    print("Encoding video stream...")
    
    # -----------------------------------------------------
    # Render Loop
    # -----------------------------------------------------
    for f in range(total_frames):
        frame_img = bg_template.copy()
        
        # =================================================
        # SCENE 1 & 2: INTRO & SHOWCASE (Frames 0 - 250)
        # 0.0s to 8.33s
        # =================================================
        if f <= 255:
            s_alpha = 1.0
            if f >= 238:
                # Fade out scene 2
                s_alpha = 1.0 - ease_in_cubic((f - 238) / 17.0)
                
            # 1. Header Logo
            t_logo = ease_out_cubic((f - 5) / 28.0)
            cur_logo_y = lerp(-100, header_logo_y, t_logo)
            draw_element(frame_img, logo, width / 2.0, cur_logo_y, target_w=header_logo_w, alpha=t_logo * s_alpha)
            
            # 2. Header Title "SOLES FOR YOUR REQUIREMENTS"
            t_title = ease_out_cubic((f - 18) / 28.0)
            cur_title_y = lerp(-120, header_title_y, t_title)
            draw_element(frame_img, htitle, width / 2.0, cur_title_y, target_w=header_title_w, alpha=t_title * s_alpha)
            
            # Floating micro-motion for collage
            float_y = math.sin(f * 0.08) * 3.5 if f > 215 else 0.0
            
            # Draw Cards in controlled depth order:
            # 1. Sneaker (Top Left)
            cfg_s = cards_cfg["Sneaker"]
            if f >= cfg_s["start_f"]:
                tc = ease_out_back((f - cfg_s["start_f"]) / 30.0, s=1.2)
                cx = lerp(-250, cfg_s["x"], tc)
                cy = lerp(cfg_s["y"] - 300, cfg_s["y"] + float_y, tc)
                draw_element(frame_img, cards["Sneaker"], cx, cy, target_w=cfg_s["w"], rot=cfg_s["rot"] * tc, alpha=s_alpha)
                
            # 2. Comfort (Top Right)
            cfg_c = cards_cfg["Comfort"]
            if f >= cfg_c["start_f"]:
                tc = ease_out_back((f - cfg_c["start_f"]) / 30.0, s=1.2)
                cx = lerp(width + 250, cfg_c["x"], tc)
                cy = lerp(cfg_c["y"] - 300, cfg_c["y"] - float_y, tc)
                draw_element(frame_img, cards["Comfort"], cx, cy, target_w=cfg_c["w"], rot=cfg_c["rot"] * tc, alpha=s_alpha)
                
            # 3. Heel (Bottom Left)
            cfg_h = cards_cfg["Heel"]
            if f >= cfg_h["start_f"]:
                tc = ease_out_back((f - cfg_h["start_f"]) / 30.0, s=1.2)
                cx = lerp(-250, cfg_h["x"], tc)
                cy = lerp(height + 250, cfg_h["y"] + float_y, tc)
                draw_element(frame_img, cards["Heel"], cx, cy, target_w=cfg_h["w"], rot=cfg_h["rot"] * tc, alpha=s_alpha)
                
            # 4. Formal (Bottom Right)
            cfg_f = cards_cfg["Formal"]
            if f >= cfg_f["start_f"]:
                tc = ease_out_back((f - cfg_f["start_f"]) / 30.0, s=1.2)
                cx = lerp(width + 250, cfg_f["x"], tc)
                cy = lerp(height + 250, cfg_f["y"] - float_y, tc)
                draw_element(frame_img, cards["Formal"], cx, cy, target_w=cfg_f["w"], rot=cfg_f["rot"] * tc, alpha=s_alpha)
                
            # 5. Lug Hero (Center) - Drawn ON TOP of all other cards!
            cfg_l = cards_cfg["Lug"]
            if f >= cfg_l["start_f"]:
                tc = ease_out_back((f - cfg_l["start_f"]) / 32.0, s=1.25)
                cx = cfg_l["x"]
                cy = lerp(height + 350, cfg_l["y"] + float_y * 1.4, tc)
                draw_element(frame_img, cards["Lug"], cx, cy, target_w=cfg_l["w"], rot=cfg_l["rot"] * tc, alpha=s_alpha)

        # =================================================
        # SCENE 3: HERITAGE & BILINGUAL TAGLINES (Frames 250 - 338)
        # 8.33s to 11.26s
        # =================================================
        if 250 <= f <= 340:
            s_alpha = 1.0
            if f < 268:
                s_alpha = ease_out_cubic((f - 250) / 18.0)
            elif f >= 324:
                s_alpha = 1.0 - ease_in_cubic((f - 324) / 16.0)
                
            # Heritage Seal with spring scale
            t_seal = ease_out_back((f - 254) / 26.0, s=1.3)
            cur_w = lerp(seal_w * 0.4, seal_w, t_seal)
            draw_element(frame_img, seal_shadow, width / 2.0, seal_y, target_w=cur_w, alpha=s_alpha)
            
            # Urdu Calligraphy
            if f >= 268:
                tu = ease_out_cubic((f - 268) / 22.0)
                cur_y = lerp(urdu_s3_y + 30, urdu_s3_y, tu)
                draw_element(frame_img, urdu, width / 2.0, cur_y, target_w=urdu_s3_w, alpha=tu * s_alpha)
                
            # English Tagline
            if f >= 280:
                te = ease_out_cubic((f - 280) / 20.0)
                cur_y = lerp(eng_s3_y + 25, eng_s3_y, te)
                draw_element(frame_img, eng, width / 2.0, cur_y, target_w=eng_s3_w, alpha=te * s_alpha)
                
            # Gleam sweep effect across seal
            if 280 <= f <= 315:
                gleam_t = (f - 280) / 35.0
                gleam_x = lerp(width/2.0 - 240, width/2.0 + 240, gleam_t)
                draw = ImageDraw.Draw(frame_img, 'RGBA')
                draw.ellipse([gleam_x - 30, seal_y - 120, gleam_x + 30, seal_y + 120], 
                             fill=(255, 255, 255, int(65 * math.sin(gleam_t * math.pi))))

        # =================================================
        # SCENE 4: GRAND OUTRO & CONTACTS (Frames 336 - 420)
        # 11.2s to 14.0s
        # =================================================
        if f >= 336:
            s_alpha = ease_out_cubic((f - 336) / 16.0)
            
            # 1. Hero Brand Logo
            t_logo = ease_out_back((f - 338) / 24.0, s=1.2)
            cur_w = lerp(outro_logo_w * 0.4, outro_logo_w, t_logo)
            draw_element(frame_img, logo, width / 2.0, outro_logo_y, target_w=cur_w, alpha=s_alpha)
            
            # 2. Urdu Tagline under logo
            if f >= 348:
                tu = ease_out_cubic((f - 348) / 20.0)
                cur_y = lerp(outro_urdu_y + 25, outro_urdu_y, tu)
                draw_element(frame_img, urdu, width / 2.0, cur_y, target_w=outro_urdu_w, alpha=tu * s_alpha)
                
            # 3. Outro CTA text
            if f >= 358:
                tcta = ease_out_cubic((f - 358) / 18.0)
                cur_y = lerp(outro_cta_y + 20, outro_cta_y, tcta)
                draw_element(frame_img, cta, width / 2.0, cur_y, target_w=outro_cta_w, alpha=tcta * s_alpha)
                
            # 4. WhatsApp Contact Badges
            if f >= 368:
                tcnt = ease_out_back((f - 368) / 22.0, s=1.2)
                cur_y = lerp(height + 150, outro_contacts_y, tcnt)
                pulse = 1.0 + math.sin(f * 0.3) * 0.02 if f > 390 else 1.0
                draw_element(frame_img, contacts_shadow, width / 2.0, cur_y, target_w=outro_contacts_w * pulse, alpha=s_alpha)

        # Write frame to ffmpeg
        proc.stdin.write(frame_img.tobytes())
        
        if (f + 1) % 60 == 0 or f == total_frames - 1:
            pct = int((f + 1) / total_frames * 100)
            print(f"Render progress: {pct}% ({f+1}/{total_frames} frames)")

    proc.stdin.close()
    stderr_output = proc.stderr.read().decode('utf-8')
    proc.wait()
    
    if proc.returncode != 0:
        print("FFmpeg Error:", stderr_output)
    else:
        print(f"Successfully rendered: {output_filename}")

# ---------------------------------------------------------
# Main Execution
# ---------------------------------------------------------
if __name__ == '__main__':
    # 1. Master 4:5 Commercial (1080x1350)
    render_video("MOD_SOLE_Commercial_4x5.mp4", 1080, 1350, is_vertical_9x16=False)
    
    # 2. Vertical 9:16 Commercial (1080x1920)
    render_video("MOD_SOLE_Commercial_9x16.mp4", 1080, 1920, is_vertical_9x16=True)
    
    print("\nAll videos rendered and mastered successfully!")


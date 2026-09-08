import os
import sys
import json
import base64
import subprocess
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import render_commercial

PORT = 8765

# -------------------------------------------------------------------
# Card Generation Function
# -------------------------------------------------------------------
def generate_product_card(img_input, title, tag, tag_color_rgb, output_path):
    card_size = 680
    card = Image.new('RGBA', (card_size, card_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    
    # Outer rounded rect
    draw.rounded_rectangle([16, 16, card_size - 16, card_size - 16], radius=28, 
                           fill=(254, 254, 254, 255), outline=(225, 228, 236, 230), width=3)
    
    # Fonts
    font_bold_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'fonts', 'Arial Bold.ttf')
    font_sub_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'fonts', 'Arial.ttf')
    if os.path.exists(font_bold_path):
        font_bold = ImageFont.truetype(font_bold_path, 32)
    elif os.path.exists('/System/Library/Fonts/HelveticaNeue.ttc'):
        font_bold = ImageFont.truetype('/System/Library/Fonts/HelveticaNeue.ttc', 32, index=0)
    else:
        font_bold = ImageFont.load_default()

    if os.path.exists(font_sub_path):
        font_sub = ImageFont.truetype(font_sub_path, 17)
    elif os.path.exists('/System/Library/Fonts/HelveticaNeue.ttc'):
        font_sub = ImageFont.truetype('/System/Library/Fonts/HelveticaNeue.ttc', 17, index=0)
    else:
        font_sub = ImageFont.load_default()
    
    # Title
    t_bbox = draw.textbbox((0, 0), title.upper(), font=font_bold)
    tw = t_bbox[2] - t_bbox[0]
    draw.text(((card_size - tw)/2, 34), title.upper(), fill=(20, 24, 40, 255), font=font_bold)
    
    # Subtitle: S O L E S
    s_text = "S  O  L  E  S"
    s_bbox = draw.textbbox((0, 0), s_text, font=font_sub)
    sw = s_bbox[2] - s_bbox[0]
    draw.text(((card_size - sw)/2, 74), s_text, fill=(110, 120, 140, 255), font=font_sub)
    
    # Gold divider line
    draw.line([card_size/2 - 90, 105, card_size/2 + 90, 105], fill=(212, 160, 23, 180), width=2)
    
    # Product Image
    if isinstance(img_input, str):
        prod = Image.open(img_input).convert('RGBA')
    else:
        prod = img_input.convert('RGBA')
        
    target_w, target_h = card_size - 80, card_size - 200
    # Scale keeping aspect ratio inside target box
    scale = min(target_w / float(prod.width), target_h / float(prod.height))
    nw, nh = int(prod.width * scale), int(prod.height * scale)
    prod_scaled = prod.resize((nw, nh), Image.LANCZOS)
    
    px = int(40 + (target_w - nw)/2)
    py = int(120 + (target_h - nh)/2)
    card.paste(prod_scaled, (px, py), prod_scaled)
    
    # Category tag pill at bottom
    tag_str = tag.upper()
    tag_bbox = draw.textbbox((0, 0), tag_str, font=font_sub)
    tag_w = tag_bbox[2] - tag_bbox[0]
    pill_w = tag_w + 36
    pill_x = (card_size - pill_w)/2
    draw.rounded_rectangle([pill_x, card_size - 60, pill_x + pill_w, card_size - 25], 
                           radius=16, fill=tag_color_rgb)
    draw.text((pill_x + 18, card_size - 55), tag_str, fill=(255, 255, 255, 255), font=font_sub)
    
    card.save(output_path)

# -------------------------------------------------------------------
# HTML Template Studio Front-End
# -------------------------------------------------------------------
HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MOD SOLE - Commercial Video Template Studio</title>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Noto+Nastaliq+Urdu:wght@700&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #0d111a;
  --card-bg: #151b28;
  --panel-bg: #1b2334;
  --accent: #d4a017;
  --accent-blue: #3b82f6;
  --text-main: #f3f4f6;
  --text-muted: #9ca3af;
  --border: #2d3748;
}
* { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Outfit', sans-serif; }
body { background: var(--bg); color: var(--text-main); min-height: 100vh; padding: 30px 20px; }
.container { max-width: 1200px; margin: 0 auto; }
header { text-align: center; margin-bottom: 35px; }
.brand-badge { display: inline-block; background: var(--accent); color: #000; font-weight: 800; font-size: 13px; padding: 5px 16px; border-radius: 20px; letter-spacing: 2px; margin-bottom: 12px; }
h1 { font-size: 38px; font-weight: 800; letter-spacing: 1px; color: #fff; margin-bottom: 6px; }
.urdu-tagline { font-family: 'Noto Nastaliq Urdu', serif; font-size: 26px; color: var(--accent); margin: 6px 0 15px; }
p.subtitle { color: var(--text-muted); font-size: 16px; }

.main-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 30px; }
@media(max-width: 900px) { .main-grid { grid-template-columns: 1fr; } }

.slots-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 30px; }
.slot-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 18px; padding: 18px; position: relative; transition: transform 0.2s, border-color 0.2s; }
.slot-card:hover { border-color: var(--accent); transform: translateY(-2px); }
.slot-badge { position: absolute; top: 12px; left: 14px; background: rgba(0,0,0,0.6); color: var(--accent); font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 12px; }
.hero-badge { background: var(--accent); color: #000; }

.img-preview-box { width: 100%; height: 180px; background: #0b0e14; border-radius: 12px; margin: 25px 0 15px; display: flex; align-items: center; justify-content: center; overflow: hidden; border: 2px dashed #2d3748; cursor: pointer; position: relative; }
.img-preview-box img { max-width: 90%; max-height: 90%; object-fit: contain; }
.img-preview-box:hover { border-color: var(--accent); }
.change-photo-btn { position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.75); color: #fff; font-size: 12px; padding: 5px 10px; border-radius: 8px; pointer-events: none; }

.input-group { margin-bottom: 12px; }
.input-group label { display: block; font-size: 12px; color: var(--text-muted); font-weight: 600; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 1px; }
.input-group input { width: 100%; background: #0c1017; border: 1px solid var(--border); border-radius: 8px; padding: 9px 12px; color: #fff; font-size: 14px; font-weight: 600; }
.input-group input:focus { outline: none; border-color: var(--accent); }

.control-panel { background: var(--card-bg); border: 1px solid var(--border); border-radius: 20px; padding: 25px; height: fit-content; }
.panel-title { font-size: 20px; font-weight: 700; margin-bottom: 18px; border-bottom: 1px solid var(--border); padding-bottom: 12px; }

.format-select { display: flex; gap: 12px; margin-bottom: 22px; }
.format-btn { flex: 1; padding: 14px; background: #0c1017; border: 2px solid var(--border); border-radius: 12px; color: #fff; cursor: pointer; text-align: center; transition: 0.2s; font-weight: 700; }
.format-btn.active { border-color: var(--accent); background: rgba(212,160,23,0.1); color: var(--accent); }
.format-btn small { display: block; font-size: 11px; font-weight: 400; color: var(--text-muted); margin-top: 3px; }

.generate-btn { width: 100%; background: linear-gradient(135deg, #d4a017, #f59e0b); color: #000; font-size: 18px; font-weight: 800; border: none; padding: 18px; border-radius: 14px; cursor: pointer; letter-spacing: 1px; transition: transform 0.2s, box-shadow 0.2s; display: flex; align-items: center; justify-content: center; gap: 10px; }
.generate-btn:hover { transform: translateY(-2px); box-shadow: 0 10px 25px rgba(212,160,23,0.3); }
.generate-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.status-box { margin-top: 20px; padding: 14px; border-radius: 10px; font-size: 14px; display: none; text-align: center; }
.status-loading { background: rgba(59,130,246,0.15); border: 1px solid var(--accent-blue); color: #60a5fa; display: block; }
.status-success { background: rgba(16,185,129,0.15); border: 1px solid #10b981; color: #34d399; display: block; }

.video-preview-wrapper { margin-top: 25px; display: none; }
.video-preview-wrapper video { width: 100%; border-radius: 12px; border: 1px solid var(--border); }
.download-btn { display: block; width: 100%; text-align: center; background: #10b981; color: #fff; font-weight: 700; padding: 14px; border-radius: 10px; text-decoration: none; margin-top: 10px; }
</style>
</head>
<body>
<div class="container">
  <header>
    <div class="brand-badge">MOD SOLE • SINCE 1980</div>
    <h1>Video Template Studio</h1>
    <div class="urdu-tagline">ہمارا معیار ہی ہماری پہچان ہے۔</div>
    <p class="subtitle">Select any picture to replace it and edit article titles. Click 'Generate Video' to create a fresh commercial.</p>
  </header>

  <div class="main-grid">
    <div>
      <div class="slots-grid">
        <!-- Slot 1 (Center Hero) -->
        <div class="slot-card">
          <span class="slot-badge hero-badge">HERO CENTER</span>
          <div class="img-preview-box" onclick="triggerUpload(1)">
            <img id="prev-1" src="/assets/premium_lug_sole_1788806240334.jpg">
            <span class="change-photo-btn">📷 Change Photo</span>
          </div>
          <input type="file" id="file-1" accept="image/*" style="display:none" onchange="handleFile(1, event)">
          <div class="input-group">
            <label>Card Title</label>
            <input type="text" id="title-1" value="QUALITY YOU CAN TRUST">
          </div>
          <div class="input-group">
            <label>Category Label</label>
            <input type="text" id="tag-1" value="HEAVY DUTY & WORK BOOTS">
          </div>
        </div>

        <!-- Slot 2 (Formal) -->
        <div class="slot-card">
          <span class="slot-badge">BOTTOM RIGHT</span>
          <div class="img-preview-box" onclick="triggerUpload(2)">
            <img id="prev-2" src="/assets/premium_formal_sole_1788806303413.jpg">
            <span class="change-photo-btn">📷 Change Photo</span>
          </div>
          <input type="file" id="file-2" accept="image/*" style="display:none" onchange="handleFile(2, event)">
          <div class="input-group">
            <label>Card Title</label>
            <input type="text" id="title-2" value="CRAFTED TO LAST">
          </div>
          <div class="input-group">
            <label>Category Label</label>
            <input type="text" id="tag-2" value="FORMAL & EXECUTIVE LEATHER">
          </div>
        </div>

        <!-- Slot 3 (Sneaker) -->
        <div class="slot-card">
          <span class="slot-badge">TOP LEFT</span>
          <div class="img-preview-box" onclick="triggerUpload(3)">
            <img id="prev-3" src="/assets/premium_sneaker_sole_1788806273036.jpg">
            <span class="change-photo-btn">📷 Change Photo</span>
          </div>
          <input type="file" id="file-3" accept="image/*" style="display:none" onchange="handleFile(3, event)">
          <div class="input-group">
            <label>Card Title</label>
            <input type="text" id="title-3" value="MAXIMUM COMFORT">
          </div>
          <div class="input-group">
            <label>Category Label</label>
            <input type="text" id="tag-3" value="ATHLETIC & SNEAKERS">
          </div>
        </div>

        <!-- Slot 4 (Casual Comfort) -->
        <div class="slot-card">
          <span class="slot-badge">TOP RIGHT</span>
          <div class="img-preview-box" onclick="triggerUpload(4)">
            <img id="prev-4" src="/assets/premium_comfort_sole_1788806341817.jpg">
            <span class="change-photo-btn">📷 Change Photo</span>
          </div>
          <input type="file" id="file-4" accept="image/*" style="display:none" onchange="handleFile(4, event)">
          <div class="input-group">
            <label>Card Title</label>
            <input type="text" id="title-4" value="SOFT & DURABLE">
          </div>
          <div class="input-group">
            <label>Category Label</label>
            <input type="text" id="tag-4" value="ERGONOMIC DAILY CASUAL">
          </div>
        </div>

        <!-- Slot 5 (Heel) -->
        <div class="slot-card">
          <span class="slot-badge">BOTTOM LEFT</span>
          <div class="img-preview-box" onclick="triggerUpload(5)">
            <img id="prev-5" src="/assets/premium_heel_sole_1788806376134.jpg">
            <span class="change-photo-btn">📷 Change Photo</span>
          </div>
          <input type="file" id="file-5" accept="image/*" style="display:none" onchange="handleFile(5, event)">
          <div class="input-group">
            <label>Card Title</label>
            <input type="text" id="title-5" value="FEMININE & ELEGANT">
          </div>
          <div class="input-group">
            <label>Category Label</label>
            <input type="text" id="tag-5" value="LADIES FASHION HEELS">
          </div>
        </div>
      </div>
    </div>

    <!-- Control Panel -->
    <div class="control-panel">
      <div class="panel-title">Video Settings</div>

      <div class="input-group">
        <label>Aspect Ratio</label>
        <div class="format-select">
          <div class="format-btn active" id="btn-916" onclick="setRatio('9x16')">
            9:16
            <small>Reel / TikTok / Status</small>
          </div>
          <div class="format-btn" id="btn-45" onclick="setRatio('4x5')">
            4:5
            <small>In-Feed Post</small>
          </div>
        </div>
      </div>

      <div class="input-group">
        <label>WhatsApp Number 1</label>
        <input type="text" id="phone-1" value="0331-4344110">
      </div>
      <div class="input-group" style="margin-bottom: 25px;">
        <label>WhatsApp Number 2</label>
        <input type="text" id="phone-2" value="0322-4343680">
      </div>

      <button class="generate-btn" id="gen-btn" onclick="generateVideo()">
        <span>🎬 Generate Commercial</span>
      </button>

      <div id="status-box" class="status-box"></div>

      <div id="video-wrapper" class="video-preview-wrapper">
        <video id="result-video" controls autoplay loop playsinline></video>
        <a id="download-link" class="download-btn" href="#" download>⬇️ Download Video (MP4)</a>
      </div>
    </div>
  </div>
</div>

<script>
let currentRatio = '9x16';
const uploadedImages = {};

function setRatio(ratio) {
  currentRatio = ratio;
  document.getElementById('btn-916').classList.toggle('active', ratio === '9x16');
  document.getElementById('btn-45').classList.toggle('active', ratio === '4x5');
}

function triggerUpload(slot) {
  document.getElementById('file-' + slot).click();
}

function handleFile(slot, event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function(e) {
    const img = new Image();
    img.onload = function() {
      // Auto-downscale high-res phone camera photos (e.g. 48MP) to 720px max dimension
      // This prevents cloud server 512MB RAM overflow and speeds up upload by 98%
      const maxDim = 720;
      let w = img.width, h = img.height;
      if (w > maxDim || h > maxDim) {
        if (w > h) { h = Math.round(h * (maxDim / w)); w = maxDim; }
        else { w = Math.round(w * (maxDim / h)); h = maxDim; }
      }
      const canvas = document.createElement('canvas');
      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0, w, h);
      const optimizedDataUrl = canvas.toDataURL('image/jpeg', 0.88);
      document.getElementById('prev-' + slot).src = optimizedDataUrl;
      uploadedImages[slot] = optimizedDataUrl;
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

async function generateVideo() {
  const btn = document.getElementById('gen-btn');
  const status = document.getElementById('status-box');
  const videoWrapper = document.getElementById('video-wrapper');
  
  btn.disabled = true;
  status.className = 'status-box status-loading';
  status.innerText = '⏳ Rendering new commercial ad (generating cards & compositing 420 frames)...';
  videoWrapper.style.display = 'none';

  const payload = {
    ratio: currentRatio,
    slots: {
      1: { title: document.getElementById('title-1').value, tag: document.getElementById('tag-1').value, image: uploadedImages[1] || null },
      2: { title: document.getElementById('title-2').value, tag: document.getElementById('tag-2').value, image: uploadedImages[2] || null },
      3: { title: document.getElementById('title-3').value, tag: document.getElementById('tag-3').value, image: uploadedImages[3] || null },
      4: { title: document.getElementById('title-4').value, tag: document.getElementById('tag-4').value, image: uploadedImages[4] || null },
      5: { title: document.getElementById('title-5').value, tag: document.getElementById('tag-5').value, image: uploadedImages[5] || null }
    }
  };

  try {
    const res = await fetch('/api/render', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.status === 'success') {
      status.className = 'status-box status-success';
      status.innerText = '✅ Commercial Video Rendered Successfully!';
      
      const v = document.getElementById('result-video');
      v.src = data.video_url + '?t=' + Date.now();
      const dlBtn = document.getElementById('download-link');
      dlBtn.onclick = function(e) {
        e.preventDefault();
        downloadVideoFile(data.video_url, data.filename);
      };
      videoWrapper.style.display = 'block';
    } else {
      status.innerText = '❌ Error: ' + data.error;
    }
  } catch (err) {
    status.innerText = '❌ Render failed: ' + err.message;
  } finally {
    btn.disabled = false;
  }
}

async function downloadVideoFile(url, defaultName) {
  const btn = document.getElementById('download-link');
  const oldText = btn.innerText;
  btn.innerText = '⏳ Downloading video...';
  try {
    const res = await fetch(url + '?t=' + Date.now());
    const blob = await res.blob();
    const mp4Blob = new Blob([blob], { type: 'video/mp4' });
    const blobUrl = window.URL.createObjectURL(mp4Blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = blobUrl;
    a.download = defaultName || 'MOD_SOLE_Commercial.mp4';
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
      window.URL.revokeObjectURL(blobUrl);
      a.remove();
      btn.innerText = oldText;
    }, 1500);
  } catch (err) {
    // Fallback direct navigation
    window.location.href = url;
    btn.innerText = oldText;
  }
}
</script>
</body>
</html>
"""

# -------------------------------------------------------------------
# HTTP Request Handler
# -------------------------------------------------------------------
class StudioHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        clean_path = self.path.split('?')[0].lstrip('/')
        if self.path == '/' or self.path == '/index.html' or clean_path == '':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
        elif clean_path.endswith('.mp4'):
            if os.path.exists(clean_path):
                self.send_response(200)
                self.send_header('Content-Type', 'video/mp4')
                self.send_header('Content-Disposition', f'attachment; filename="{clean_path}"')
                self.send_header('Content-Length', str(os.path.getsize(clean_path)))
                self.end_headers()
                with open(clean_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "Video file not found")
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/render':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            ratio = data.get('ratio', '9x16')
            slots = data.get('slots', {})
            
            # Map slot configurations
            slot_colors = {
                1: (180, 130, 40, 255),  # Lug
                2: (130, 60, 30, 255),   # Formal
                3: (30, 110, 180, 255),  # Sneaker
                4: (170, 90, 70, 255),   # Comfort
                5: (40, 40, 60, 255)     # Heel
            }
            default_imgs = {
                1: "assets/premium_lug_sole_1788806240334.jpg",
                2: "assets/premium_formal_sole_1788806303413.jpg",
                3: "assets/premium_sneaker_sole_1788806273036.jpg",
                4: "assets/premium_comfort_sole_1788806341817.jpg",
                5: "assets/premium_heel_sole_1788806376134.jpg"
            }
            slot_out_files = {
                1: "assets/card_lug.png",
                2: "assets/card_formal.png",
                3: "assets/card_sneaker.png",
                4: "assets/card_comfort.png",
                5: "assets/card_heel.png"
            }
            
            # 1. Update product cards
            for slot_num in range(1, 6):
                s_info = slots.get(str(slot_num), {})
                title = s_info.get('title', f"SLOT {slot_num}")
                tag = s_info.get('tag', "FOOTWEAR SOLE")
                b64_img = s_info.get('image')
                
                if b64_img and ',' in b64_img:
                    raw_data = base64.b64decode(b64_img.split(',')[1])
                    img_path = f"assets/upload_slot_{slot_num}.png"
                    with open(img_path, 'wb') as f:
                        f.write(raw_data)
                else:
                    img_path = default_imgs[slot_num]
                    
                generate_product_card(img_path, title, tag, slot_colors[slot_num], slot_out_files[slot_num])
            
            import gc
            gc.collect()
                
            # 2. Render target commercial video
            is_9x16 = (ratio == '9x16')
            out_name = "MOD_SOLE_Commercial_9x16.mp4" if is_9x16 else "MOD_SOLE_Commercial_4x5.mp4"
            w = 1080
            h = 1920 if is_9x16 else 1350
            
            print(f"\n[Template Studio] Rendering {out_name}...")
            render_commercial.render_video(out_name, w, h, is_vertical_9x16=is_9x16)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            resp = {
                "status": "success",
                "video_url": f"/{out_name}",
                "filename": out_name
            }
            self.wfile.write(json.dumps(resp).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    port = int(os.environ.get('PORT', PORT))
    server = HTTPServer(('0.0.0.0', port), StudioHandler)
    url = f"http://0.0.0.0:{port}"
    print(f"\n=======================================================")
    print(f"🎬 MOD SOLE - Template Studio Running!")
    print(f"👉 Listening on port {port} (0.0.0.0:{port})")
    print(f"=======================================================\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStudio server stopped.")

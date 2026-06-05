from flask import Flask, render_template_string, request, jsonify, send_file
import yt_dlp
import os, uuid, threading, tempfile, json
from urllib.parse import quote
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
import io

load_dotenv()

app = Flask(__name__)
MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://sam:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority')

try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    mongo_client.admin.command('ping')
    db = mongo_client['samhouston']
except Exception as e:
    print(f"MongoDB Connection Error: {e}")
    db = None

downloads = {}

HTML = r'''<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sam Houston Downloader | دانلود ویدیو آنلاین</title>
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {
  --g: rgba(255,255,255,0.06); --gb: rgba(255,255,255,0.12);
  --gh: rgba(255,255,255,0.1); --a: #38bdf8; --a2: #818cf8; --a3: #f472b6;
  --t: #f1f5f9; --tm: #94a3b8; --bg: #020617; --err: #f87171; --ok: #34d399;
}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Vazirmatn',sans-serif;background:var(--bg);color:var(--t);min-height:100vh;overflow-x:hidden}
.orbs{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.orb{position:absolute;border-radius:50%;filter:blur(90px);opacity:.18;animation:fl 14s ease-in-out infinite}
.o1{width:600px;height:600px;background:radial-gradient(circle,#6366f1,transparent);top:-150px;right:-150px}
.o2{width:500px;height:500px;background:radial-gradient(circle,#0ea5e9,transparent);bottom:-150px;left:-150px;animation-delay:-5s}
.o3{width:350px;height:350px;background:radial-gradient(circle,#ec4899,transparent);top:50%;left:45%;animation-delay:-10s}
@keyframes fl{0%,100%{transform:translate(0,0)}40%{transform:translate(20px,-20px)}70%{transform:translate(-15px,15px)}}
body::before{content:'';position:fixed;inset:0;z-index:0;background-image:linear-gradient(rgba(255,255,255,.02) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.02) 1px,transparent 1px);background-size:55px 55px;pointer-events:none}
.page{position:relative;z-index:1;min-height:100vh;display:flex;flex-direction:column;align-items:center;padding:36px 18px}

header{text-align:center;margin-bottom:40px;animation:fdown .7s ease both}
.pill{display:inline-flex;align-items:center;gap:9px;background:var(--g);border:1px solid var(--gb);backdrop-filter:blur(18px);border-radius:100px;padding:9px 22px;margin-bottom:20px}
.pdot{width:7px;height:7px;border-radius:50%;background:var(--a);box-shadow:0 0 10px var(--a)}
.pname{font-size:.8rem;font-weight:600;color:var(--tm);letter-spacing:.12em;text-transform:uppercase}
h1{font-size:clamp(1.9rem,5vw,3.2rem);font-weight:700;line-height:1.1;margin-bottom:10px;background:linear-gradient(135deg,#fff 0%,var(--a) 55%,var(--a2) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.sub{color:var(--tm);font-size:.92rem}

.card{width:100%;max-width:700px;background:var(--g);border:1px solid var(--gb);backdrop-filter:blur(18px);border-radius:22px;padding:28px;margin-bottom:16px;box-shadow:0 25px 60px rgba(0,0,0,.4),inset 0 1px 0 rgba(255,255,255,.07);animation:fup .7s ease .1s both}

.ui{width:100%;background:rgba(0,0,0,.35);border:1px solid var(--gb);border-radius:13px;padding:14px 17px;color:var(--t);font-family:'Vazirmatn',sans-serif;font-size:.92rem;direction:ltr;transition:all .2s;outline:none;margin-bottom:14px}
.ui::placeholder{color:#3a4a60}
.ui:focus{border-color:var(--a);background:rgba(56,189,248,.04);box-shadow:0 0 0 3px rgba(56,189,248,.1)}

.row{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px}
.lbl{font-size:.75rem;color:var(--tm);margin-bottom:7px;font-weight:500}
.sel{width:100%;background:rgba(0,0,0,.35);border:1px solid var(--gb);border-radius:10px;padding:10px 13px;color:var(--t);font-family:'Vazirmatn',sans-serif;font-size:.85rem;outline:none;cursor:pointer;transition:border .2s}
.sel:focus{border-color:var(--a)}
.sel option{background:#0f172a}

.bmain{width:100%;position:relative;overflow:hidden;background:linear-gradient(135deg,rgba(14,165,233,.22),rgba(99,102,241,.22));border:1px solid rgba(56,189,248,.38);backdrop-filter:blur(10px);border-radius:13px;padding:15px;color:#fff;font-family:'Vazirmatn',sans-serif;font-size:1rem;font-weight:600;cursor:pointer;transition:all .3s}
.bmain::before{content:'';position:absolute;top:-50%;left:-60%;width:35%;height:200%;background:linear-gradient(105deg,transparent,rgba(255,255,255,.22),transparent);transform:skewX(-20deg);transition:left .55s ease}
.bmain:hover::before{left:130%}
.bmain:hover{background:linear-gradient(135deg,rgba(14,165,233,.38),rgba(99,102,241,.38));border-color:rgba(56,189,248,.65);box-shadow:0 0 25px rgba(56,189,248,.28);transform:translateY(-1px)}
.bmain:disabled{opacity:.4;cursor:not-allowed;transform:none}

.pcard{display:none;width:100%;max-width:700px;background:var(--g);border:1px solid var(--gb);backdrop-filter:blur(18px);border-radius:22px;padding:28px;margin-bottom:16px;text-align:center}
.pbar-bg{background:rgba(255,255,255,.06);border-radius:100px;height:6px;margin:14px 0;overflow:hidden}
.pbar{height:100%;background:linear-gradient(90deg,var(--a),var(--a2));border-radius:100px;width:0%;transition:width .4s}
.ptxt{color:var(--tm);font-size:.88rem}

.ecard{display:none;width:100%;max-width:700px;background:rgba(248,113,113,.07);border:1px solid rgba(248,113,113,.22);backdrop-filter:blur(18px);border-radius:14px;padding:14px 18px;margin-bottom:16px;color:var(--err);font-size:.88rem;text-align:center}

.rcard{display:none;width:100%;max-width:700px;background:var(--g);border:1px solid var(--gb);backdrop-filter:blur(18px);border-radius:22px;padding:24px;margin-bottom:16px;animation:fup .4s ease both}
.vhead{display:flex;gap:13px;align-items:center;margin-bottom:20px}
.vthumb{width:110px;height:62px;object-fit:cover;border-radius:9px;flex-shrink:0;border:1px solid var(--gb)}
.vtitle{font-size:.92rem;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;margin-bottom:3px}
.vplat{font-size:.75rem;color:var(--tm)}
.slbl{font-size:.72rem;color:#334155;margin:10px 0 7px;font-weight:600;text-transform:uppercase;letter-spacing:.07em}

.dlb{display:flex;align-items:center;justify-content:space-between;width:100%;position:relative;overflow:hidden;background:rgba(255,255,255,.04);border:1px solid var(--gb);border-radius:11px;padding:12px 15px;color:var(--t);text-decoration:none;font-family:'Vazirmatn',sans-serif;font-size:.86rem;cursor:pointer;transition:all .25s;margin-bottom:7px}
.dlb::before{content:'';position:absolute;top:-50%;left:-60%;width:33%;height:200%;background:linear-gradient(105deg,transparent,rgba(255,255,255,.16),transparent);transform:skewX(-20deg);transition:left .5s ease}
.dlb:hover::before{left:130%}
.dlb.vb:hover{background:rgba(56,189,248,.08);border-color:rgba(56,189,248,.4);box-shadow:0 0 18px rgba(56,189,248,.1);transform:translateX(-2px)}
.dlb.ab:hover{background:rgba(129,140,248,.08);border-color:rgba(129,140,248,.4);box-shadow:0 0 18px rgba(129,140,248,.1);transform:translateX(-2px)}
.dll{display:flex;align-items:center;gap:9px}
.bdg{font-size:.68rem;padding:2px 8px;border-radius:20px;font-weight:600}
.bv{background:rgba(56,189,248,.1);color:var(--a);border:1px solid rgba(56,189,248,.22)}
.ba{background:rgba(129,140,248,.1);color:var(--a2);border:1px solid rgba(129,140,248,.22)}
.darr{color:var(--tm);transition:all .2s}
.dlb:hover .darr{transform:translateX(-3px)}

footer{margin-top:auto;padding-top:40px;text-align:center}
.fb{font-size:.85rem;font-weight:600;color:#334155}.fb span{color:var(--a)}
.fs{color:#1e293b;font-size:.72rem;margin-top:3px}

@keyframes fdown{from{opacity:0;transform:translateY(-16px)}to{opacity:1;transform:translateY(0)}}
@keyframes fup{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
@media(max-width:500px){.card,.rcard,.pcard{padding:17px}.row{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="orbs"><div class="orb o1"></div><div class="orb o2"></div><div class="orb o3"></div></div>
<div class="page">

<header>
  <div class="pill"><span style="font-size:1.1rem">⬇️</span><div class="pdot"></div><span class="pname">Sam Houston Downloader</span></div>
  <h1>دانلود سریع ویدیو</h1>
  <p class="sub">اینستاگرام • توییتر • تیک‌تاک • یوتیوب و ۱۰۰۰+ سایت دیگر</p>
</header>

<div class="card">
  <input class="ui" id="url" placeholder="لینک ویدیو را اینجا paste کنید...">
  <div class="row">
    <div>
      <div class="lbl">کیفیت ویدیو</div>
      <select class="sel" id="quality">
        <option value="best">بهترین کیفیت</option>
        <option value="2160">4K</option>
        <option value="1080" selected>1080p</option>
        <option value="720">720p</option>
        <option value="480">480p</option>
        <option value="360">360p</option>
      </select>
    </div>
  </div>
  <button class="bmain" onclick="go()" id="btn">⬇️ دانلود</button>
</div>

<div class="pcard" id="pcard">
  <div class="ptxt" id="ptxt">در حال پردازش...</div>
  <div class="pbar-bg"><div class="pbar" id="pbar"></div></div>
  <div class="ptxt" id="pspeed" style="font-size:.78rem;color:#475569"></div>
</div>

<div class="ecard" id="ecard"></div>

<div class="rcard" id="rcard">
  <div class="vhead" id="vhead"></div>
  <div id="vlinks"></div>
  <div id="alinks"></div>
</div>

<footer>
  <div class="fb">Sam <span>Houston</span> Downloader</div>
  <div class="fs">✨ Cloud Version | تمام سایت‌ها پشتیبانی می‌شوند</div>
</footer>
</div>

<script>
let currentId = null;
let pollTimer = null;

function showErr(msg){
  document.getElementById('ecard').textContent='⚠️ '+msg;
  document.getElementById('ecard').style.display='block';
  document.getElementById('pcard').style.display='none';
  document.getElementById('btn').disabled=false;
}

function showProgress(pct, txt, speed){
  document.getElementById('pcard').style.display='block';
  document.getElementById('pbar').style.width=pct+'%';
  document.getElementById('ptxt').textContent=txt||'در حال دانلود...';
  if(speed) document.getElementById('pspeed').textContent=speed;
}

function go(){
  const url = document.getElementById('url').value.trim();
  const quality = document.getElementById('quality').value;
  
  if(!url){
    showErr('لطفا یک لینک وارد کنید');
    return;
  }
  
  document.getElementById('btn').disabled=true;
  document.getElementById('ecard').style.display='none';
  document.getElementById('rcard').style.display='none';
  showProgress(5, 'در حال شروع...');
  
  fetch('/api/download', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({url, quality})
  })
  .then(r => r.json())
  .then(data => {
    if(data.error){
      showErr(data.error);
      return;
    }
    currentId = data.id;
    poll();
  })
  .catch(e => showErr(e.message));
}

function poll(){
  if(!currentId) return;
  clearTimeout(pollTimer);
  
  fetch(`/api/progress/${currentId}`)
  .then(r => r.json())
  .then(d => {
    showProgress(d.pct, d.status, d.speed);
    
    if(d.done){
      showResult(d);
    } else if(d.error){
      showErr(d.error);
    } else {
      pollTimer = setTimeout(poll, 500);
    }
  })
  .catch(e => {
    pollTimer = setTimeout(poll, 1000);
  });
}

function showResult(d){
  document.getElementById('pcard').style.display='none';
  const rcard = document.getElementById('rcard');
  rcard.style.display='block';
  
  let vhead = `<img src="${d.thumb}" class="vthumb"><div><div class="vtitle">${d.title}</div><div class="vplat">${d.platform}</div></div>`;
  document.getElementById('vhead').innerHTML = vhead;
  
  let vlinks = '<div class="slbl">📹 ویدیو</div>';
  let alinks = '<div class="slbl">🎵 صدا</div>';
  
  d.files.forEach(f => {
    if(f.type === 'video'){
      vlinks += `<a href="/api/file/${f.id}" class="dlb vb"><div class="dll"><span class="bdg bv">${f.ext}</span><span>${f.label}</span></div><span class="darr">↙️</span></a>`;
    } else {
      alinks += `<a href="/api/file/${f.id}" class="dlb ab"><div class="dll"><span class="bdg ba">${f.ext}</span><span>${f.label}</span></div><span class="darr">↙️</span></a>`;
    }
  });
  
  document.getElementById('vlinks').innerHTML = vlinks;
  document.getElementById('alinks').innerHTML = alinks || '';
}
</script>
</body>
</html>'''

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/api/download', methods=['POST'])
def start_download():
    data = request.get_json()
    url = data.get('url', '').strip()
    quality = data.get('quality', '1080')

    if not url:
        return jsonify({'error': 'لینک وارد نشده'})

    dl_id = str(uuid.uuid4())[:8]
    downloads[dl_id] = {
        'pct': 5, 'status': 'شروع...', 'done': False,
        'error': None, 'files': [], 'title': '', 'thumb': '',
        'platform': '', 'speed': ''
    }

    thread = threading.Thread(target=do_download, args=(dl_id, url, quality))
    thread.daemon = True
    thread.start()

    return jsonify({'id': dl_id})

def do_download(dl_id, url, quality):
    d = downloads[dl_id]
    tmp_dir = tempfile.mkdtemp(prefix='samhouston_')
    
    try:
        d['pct'] = 10
        d['status'] = 'در حال دریافت اطلاعات...'

        if quality == 'best':
            fmt = 'bestvideo+bestaudio/best'
        elif quality in ('2160','1080','720','480','360'):
            fmt = f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best'
        else:
            fmt = 'bestvideo+bestaudio/best'

        out_path = os.path.join(tmp_dir, '%(title)s.%(ext)s')

        def progress_hook(info):
            if info['status'] == 'downloading':
                total = info.get('total_bytes') or info.get('total_bytes_estimate', 0)
                downloaded = info.get('downloaded_bytes', 0)
                if total:
                    pct = int(downloaded / total * 80) + 15
                    d['pct'] = min(pct, 94)
                speed = info.get('_speed_str', '')
                eta = info.get('_eta_str', '')
                d['speed'] = f"{speed} — {eta}" if speed else ''
                d['status'] = 'در حال دانلود...'
            elif info['status'] == 'finished':
                d['pct'] = 95
                d['status'] = 'در حال پردازش...'

        ydl_opts = {
            'format': fmt,
            'outtmpl': out_path,
            'merge_output_format': 'mp4',
            'nocheckcertificate': True,
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warnings': False,
        }

        d['pct'] = 15
        d['status'] = 'در حال اتصال...'

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            d['title'] = info.get('title', 'ویدیو')
            d['thumb'] = info.get('thumbnail', '')
            d['platform'] = info.get('extractor_key', '')

        files = []
        for fname in os.listdir(tmp_dir):
            fpath = os.path.join(tmp_dir, fname)
            ext = fname.rsplit('.', 1)[-1].lower() if '.' in fname else ''
            fid = str(uuid.uuid4())[:8]
            is_audio = ext in ('mp3', 'm4a', 'aac', 'opus', 'ogg', 'wav')
            size = os.path.getsize(fpath)
            size_str = f"{size/1024/1024:.1f}MB" if size > 1024*1024 else f"{size/1024:.0f}KB"
            files.append({
                'id': fid,
                'path': fpath,
                'label': f"{'صدا' if is_audio else 'ویدیو'} — {size_str}",
                'ext': ext.upper(),
                'type': 'audio' if is_audio else 'video'
            })

        for f in files:
            fid = f['id']
            downloads[fid] = f

        # MongoDB میں history ذخیره کریں
        if db:
            try:
                db['downloads'].insert_one({
                    'download_id': dl_id,
                    'url': url,
                    'title': d['title'],
                    'platform': d['platform'],
                    'quality': quality,
                    'timestamp': datetime.utcnow(),
                    'status': 'completed',
                    'files_count': len(files)
                })
            except:
                pass

        d['files'] = files
        d['pct'] = 100
        d['done'] = True
        d['status'] = 'تمام!'

    except Exception as e:
        err = str(e)
        if 'HTTP Error 403' in err:
            d['error'] = 'دسترسی رد شد (403) — احتمالا لاگین نیاز است'
        elif 'not found' in err.lower():
            d['error'] = 'ویدیو پیدا نشد'
        else:
            d['error'] = err[:200]

@app.route('/api/progress/<dl_id>')
def get_progress(dl_id):
    if dl_id not in downloads:
        return jsonify({'error': 'ID نامعتبر'})
    return jsonify(downloads[dl_id])

@app.route('/api/file/<file_id>')
def get_file(file_id):
    if file_id not in downloads:
        return 'فایل پیدا نشد', 404
    f = downloads[file_id]
    path = f.get('path', '')
    if not path or not os.path.exists(path):
        return 'فایل پیدا نشد', 404
    fname = os.path.basename(path)
    return send_file(path, as_attachment=True, download_name=fname)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 7070))
    app.run(host='0.0.0.0', port=port, debug=False)

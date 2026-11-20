import io
from flask import Flask, request, send_file
from PIL import Image, ImageOps

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024

PAGE = """<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Nova Academy - محوّل الصور</title>
<style>
body{font-family:Arial,sans-serif;background:#f4f1ff;margin:0;padding:20px;color:#222}
.box{max-width:420px;margin:30px auto;background:#fff;padding:24px;border-radius:16px;box-shadow:0 4px 20px #0001}
h1{color:#6d28d9;font-size:22px;text-align:center}
label{display:block;margin:14px 0 6px;font-weight:bold}
input,select,button{width:100%;padding:12px;border-radius:10px;border:1px solid #ccc;font-size:16px;box-sizing:border-box}
button{background:#6d28d9;color:#fff;border:0;margin-top:20px;cursor:pointer}
img{max-width:100%;margin-top:12px;border-radius:10px;display:none}
</style>
</head>
<body>
<div class="box">
<h1>Nova Academy<br>محوّل الصور</h1>
<form method="post" action="/convert" enctype="multipart/form-data">
<label>اختار الصورة</label>
<input type="file" name="image" accept="image/*" required onchange="p(this)">
<img id="pv">
<label>حوّلها إلى</label>
<select name="fmt">
<option value="jpg">JPG</option>
<option value="png">PNG</option>
<option value="webp">WebP</option>
</select>
<label>العرض بالبكسل (اختياري)</label>
<input type="number" name="width" min="50" max="5000" placeholder="مثلا 800">
<button type="submit">حوّل وحمّل</button>
</form>
</div>
<script>
function p(i){var f=i.files[0];if(!f)return;var im=document.getElementById('pv');im.src=URL.createObjectURL(f);im.style.display='block'}
</script>
</body>
</html>"""


@app.route("/")
def home():
    return PAGE


@app.route("/convert", methods=["POST"])
def convert():
    f = request.files.get("image")
    if not f:
        return "مفيش صورة", 400
    try:
        img = Image.open(f.stream)
        img = ImageOps.exif_transpose(img)
    except Exception:
        return "الملف ده مش صورة صالحة", 400

    w = request.form.get("width", "").strip()
    if w.isdigit() and int(w) > 0:
        w = int(w)
        h = int(img.height * w / img.width)
        img = img.resize((w, h), Image.LANCZOS)

    fmt = request.form.get("fmt", "jpg")
    out = io.BytesIO()
    if fmt == "png":
        img.save(out, "PNG", optimize=True)
        mime, ext = "image/png", "png"
    elif fmt == "webp":
        img.save(out, "WEBP", quality=85)
        mime, ext = "image/webp", "webp"
    else:
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.save(out, "JPEG", quality=90, optimize=True)
        mime, ext = "image/jpeg", "jpg"
    out.seek(0)
    return send_file(out, mimetype=mime, as_attachment=True,
                     download_name=f"nova-image.{ext}")


if __name__ == "__main__":
    app.run(debug=True)

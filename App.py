from flask import Flask, request, jsonify, render_template_string
from analyzer import analyze_from_bytes

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB máx

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DeepFace — Análisis Facial</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0a0a0a;
      --surface: #141414;
      --card: #1a1a1a;
      --card-border: #2a2a2a;
      --text: #f0f0f0;
      --text-muted: #888;
      --text-label: #666;
      --accent: #00ffff;
      --accent-dim: rgba(0, 255, 255, 0.15);
      --green: #22c55e;
      --gradient: linear-gradient(90deg, #6366f1, #8b5cf6, #a78bfa);
      --radius: 16px;
      --radius-sm: 10px;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Inter', system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      line-height: 1.5;
    }

    /* ── Header ── */
    header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 14px 24px;
      border-bottom: 1px solid var(--card-border);
      background: var(--surface);
      position: sticky;
      top: 0;
      z-index: 100;
    }

    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    .logo {
      font-size: 1.1rem;
      font-weight: 700;
      letter-spacing: -0.02em;
    }

    .status-badge {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.8rem;
      color: var(--text-muted);
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--green);
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.4; }
    }

    .header-subtitle {
      font-size: 0.85rem;
      color: var(--text-muted);
    }

    /* ── Main ── */
    main {
      max-width: 960px;
      margin: 0 auto;
      padding: 32px 20px 60px;
    }

    .hero {
      text-align: center;
      margin-bottom: 32px;
    }

    .hero h1 {
      font-size: 1.75rem;
      font-weight: 700;
      margin-bottom: 6px;
    }

    .hero p {
      color: var(--text-muted);
      font-size: 0.95rem;
    }

    /* ── Upload zone ── */
    .upload-zone {
      border: 2px dashed var(--card-border);
      border-radius: var(--radius);
      padding: 40px 24px;
      text-align: center;
      cursor: pointer;
      transition: border-color 0.25s, background 0.25s;
      background: var(--surface);
      margin-bottom: 20px;
    }

    .upload-zone:hover,
    .upload-zone.dragover {
      border-color: var(--accent);
      background: var(--accent-dim);
    }

    .upload-zone .icon { font-size: 2.5rem; margin-bottom: 12px; }

    .upload-zone h3 {
      font-size: 1rem;
      font-weight: 600;
      margin-bottom: 4px;
    }

    .upload-zone p {
      font-size: 0.85rem;
      color: var(--text-muted);
    }

    #file-input { display: none; }

    .preview-thumb {
      max-height: 120px;
      border-radius: var(--radius-sm);
      margin-top: 16px;
      display: none;
    }

    .actions {
      display: flex;
      gap: 12px;
      justify-content: center;
      margin-bottom: 32px;
    }

    .btn {
      padding: 12px 28px;
      border-radius: var(--radius-sm);
      border: none;
      font-family: inherit;
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      transition: transform 0.15s, opacity 0.15s, box-shadow 0.15s;
    }

    .btn:disabled {
      opacity: 0.35;
      cursor: not-allowed;
    }

    .btn:not(:disabled):hover {
      transform: translateY(-1px);
    }

    .btn-primary {
      background: var(--gradient);
      color: #fff;
      box-shadow: 0 4px 20px rgba(99, 102, 241, 0.35);
    }

    .btn-primary:not(:disabled):hover {
      box-shadow: 0 6px 28px rgba(99, 102, 241, 0.5);
    }

    .btn-secondary {
      background: var(--card);
      color: var(--text-muted);
      border: 1px solid var(--card-border);
    }

    /* ── Loading ── */
    .loading {
      display: none;
      text-align: center;
      padding: 40px;
    }

    .loading.active { display: block; }

    .spinner {
      width: 44px;
      height: 44px;
      border: 3px solid var(--card-border);
      border-top-color: var(--accent);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
      margin: 0 auto 16px;
    }

    @keyframes spin { to { transform: rotate(360deg); } }

    .loading p { color: var(--text-muted); font-size: 0.9rem; }

    /* ── Error ── */
    .error-msg {
      display: none;
      background: rgba(239, 68, 68, 0.12);
      border: 1px solid rgba(239, 68, 68, 0.3);
      color: #fca5a5;
      padding: 14px 18px;
      border-radius: var(--radius-sm);
      margin-bottom: 24px;
      font-size: 0.9rem;
    }

    .error-msg.active { display: block; }

    /* ── Results ── */
    #results { display: none; }
    #results.active { display: block; }

    .image-container {
      border-radius: var(--radius);
      overflow: hidden;
      margin-bottom: 24px;
      background: var(--surface);
      border: 1px solid var(--card-border);
    }

    .image-container img {
      width: 100%;
      display: block;
    }

    .cards-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
    }

    .face-card {
      background: var(--card);
      border: 1px solid var(--card-border);
      border-radius: var(--radius);
      padding: 22px;
      animation: fadeUp 0.4s ease both;
    }

    .face-card:nth-child(2) { animation-delay: 0.1s; }
    .face-card:nth-child(3) { animation-delay: 0.2s; }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(16px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    .card-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 20px;
      font-weight: 600;
      font-size: 0.95rem;
    }

    .card-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--green);
    }

    .field {
      margin-bottom: 18px;
    }

    .field:last-child { margin-bottom: 0; }

    .field-label {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.7rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--text-label);
      margin-bottom: 6px;
    }

    .field-value {
      font-size: 1.05rem;
      font-weight: 600;
    }

    .progress-bar {
      height: 5px;
      background: #2a2a2a;
      border-radius: 99px;
      margin-top: 8px;
      overflow: hidden;
    }

    .progress-fill {
      height: 100%;
      border-radius: 99px;
      background: var(--gradient);
      transition: width 0.6s ease;
    }

    .emotion-tag {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: #252525;
      border: 1px solid var(--card-border);
      padding: 6px 14px;
      border-radius: 99px;
      font-size: 0.9rem;
      font-weight: 500;
    }

    @media (max-width: 600px) {
      header { padding: 12px 16px; }
      .header-subtitle { display: none; }
      main { padding: 20px 14px 40px; }
      .upload-zone { padding: 28px 16px; }
    }
  </style>
</head>
<body>
  <header>
    <div class="header-left">
      <span class="logo">DeepFace</span>
      <div class="status-badge">
        <span class="status-dot"></span>
        Running
      </div>
    </div>
    <span class="header-subtitle">Género · Edad · Emoción · Etnia</span>
  </header>

  <main>
    <div class="hero">
      <h1>Análisis Facial</h1>
      <p>Sube una imagen para detectar rostros y obtener atributos faciales</p>
    </div>

    <div class="upload-zone" id="drop-zone">
      <div class="icon">📷</div>
      <h3>Arrastra una imagen aquí</h3>
      <p>o haz clic para seleccionar · JPG, PNG, WEBP · Máx. 16 MB</p>
      <img class="preview-thumb" id="preview-thumb" alt="Vista previa">
      <input type="file" id="file-input" accept="image/*">
    </div>

    <div class="actions">
      <button class="btn btn-primary" id="analyze-btn" disabled>Analizar imagen</button>
      <button class="btn btn-secondary" id="clear-btn" disabled>Limpiar</button>
    </div>

    <div class="error-msg" id="error-msg"></div>

    <div class="loading" id="loading">
      <div class="spinner"></div>
      <p>Analizando rostros con DeepFace…</p>
    </div>

    <div id="results">
      <div class="image-container" id="image-container"></div>
      <div class="cards-grid" id="cards-grid"></div>
    </div>
  </main>

  <script>
    const dropZone    = document.getElementById('drop-zone');
    const fileInput   = document.getElementById('file-input');
    const previewThumb = document.getElementById('preview-thumb');
    const analyzeBtn  = document.getElementById('analyze-btn');
    const clearBtn    = document.getElementById('clear-btn');
    const loading     = document.getElementById('loading');
    const errorMsg    = document.getElementById('error-msg');
    const resultsDiv  = document.getElementById('results');
    const imageContainer = document.getElementById('image-container');
    const cardsGrid   = document.getElementById('cards-grid');

    let selectedFile = null;

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', e => {
      e.preventDefault();
      dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
      dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', e => {
      e.preventDefault();
      dropZone.classList.remove('dragover');
      const file = e.dataTransfer.files[0];
      if (file && file.type.startsWith('image/')) handleFile(file);
    });

    fileInput.addEventListener('change', e => {
      if (e.target.files[0]) handleFile(e.target.files[0]);
    });

    function handleFile(file) {
      selectedFile = file;
      analyzeBtn.disabled = false;
      clearBtn.disabled = false;
      hideError();
      resultsDiv.classList.remove('active');

      const reader = new FileReader();
      reader.onload = e => {
        previewThumb.src = e.target.result;
        previewThumb.style.display = 'block';
      };
      reader.readAsDataURL(file);
    }

    clearBtn.addEventListener('click', () => {
      selectedFile = null;
      fileInput.value = '';
      previewThumb.style.display = 'none';
      previewThumb.src = '';
      analyzeBtn.disabled = true;
      clearBtn.disabled = true;
      resultsDiv.classList.remove('active');
      hideError();
    });

    analyzeBtn.addEventListener('click', async () => {
      if (!selectedFile) return;

      loading.classList.add('active');
      resultsDiv.classList.remove('active');
      hideError();
      analyzeBtn.disabled = true;

      try {
        const fd = new FormData();
        fd.append('image', selectedFile);
        const resp = await fetch('/analyze', { method: 'POST', body: fd });
        const data = await resp.json();

        if (!resp.ok) throw new Error(data.error || 'Error desconocido');

        renderResults(data);
        resultsDiv.classList.add('active');
      } catch (err) {
        showError(err.message);
      } finally {
        loading.classList.remove('active');
        analyzeBtn.disabled = false;
      }
    });

    function showError(msg) {
      errorMsg.textContent = msg;
      errorMsg.classList.add('active');
    }

    function hideError() {
      errorMsg.classList.remove('active');
    }

    function renderResults(data) {
      const { faces, annotated_image } = data;

      imageContainer.innerHTML = '';
      if (annotated_image) {
        const img = document.createElement('img');
        img.src = 'data:image/jpeg;base64,' + annotated_image;
        img.alt = 'Imagen analizada';
        imageContainer.appendChild(img);
      }

      cardsGrid.innerHTML = faces.map((face, i) => `
        <div class="face-card">
          <div class="card-header">
            <span class="card-dot"></span>
            Rostro ${i + 1}
          </div>

          <div class="field">
            <div class="field-label">🎂 Edad Estimada</div>
            <div class="field-value">${face.edad_estimada} años</div>
          </div>

          <div class="field">
            <div class="field-label">⚧ Género</div>
            <div class="field-value">${face.genero} (${face.genero_confianza}%)</div>
            <div class="progress-bar">
              <div class="progress-fill" style="width: ${face.genero_confianza}%"></div>
            </div>
          </div>

          <div class="field">
            <div class="field-label">😶 Emoción</div>
            <span class="emotion-tag">${face.emocion_emoji} ${face.emocion}</span>
          </div>

          <div class="field">
            <div class="field-label">🌐 Etnia Estimada</div>
            <div class="field-value">${face.raza_dominante}</div>
          </div>
        </div>
      `).join('');
    }
  </script>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"error": "No se recibió ninguna imagen."}), 400
    file = request.files["image"]
    if not file.filename:
        return jsonify({"error": "No se seleccionó ningún archivo."}), 400
    try:
        faces, img_b64 = analyze_from_bytes(file.read())
        return jsonify({"faces": faces, "annotated_image": img_b64})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    print("App corriendo en http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)

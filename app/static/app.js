document.addEventListener("DOMContentLoaded", () => {
  const btnToggleMic = document.getElementById("btnToggleMic");
  const transcriptLog = document.getElementById("transcriptLog");
  const latencyValue = document.getElementById("latencyValue");
  const connectionStatus = document.getElementById("connectionStatus");
  const canvas = document.getElementById("waveformCanvas");
  const ctx = canvas.getContext("2d");

  // Navigation Links & Views
  const navLiveSession = document.getElementById("navLiveSession");
  const navMetrics = document.getElementById("navMetrics");
  const navClassifier = document.getElementById("navClassifier");

  const viewLiveSession = document.getElementById("viewLiveSession");
  const viewMetrics = document.getElementById("viewMetrics");
  const viewClassifier = document.getElementById("viewClassifier");

  const pageTitle = document.getElementById("pageTitle");
  const pageSubtitle = document.getElementById("pageSubtitle");

  // Classifier Sandbox Elements
  const classifierInput = document.getElementById("classifierInput");
  const btnTestClassifier = document.getElementById("btnTestClassifier");
  const classifierResultBox = document.getElementById("classifierResultBox");
  const resIntent = document.getElementById("resIntent");
  const resEmotion = document.getElementById("resEmotion");
  const resConfidence = document.getElementById("resConfidence");
  const resEntities = document.getElementById("resEntities");
  const resAction = document.getElementById("resAction");

  let ws = null;
  let isListening = false;
  let recognition = null;
  let animationId = null;
  let audioAmp = 10;
  let availableVoices = [];

  let latencyChartInstance = null;
  let vadRatioChartInstance = null;

  // Sidebar Routing Table
  const views = [
    { nav: navLiveSession, view: viewLiveSession, title: "Real-Time Multimodal Voice Intelligence", subtitle: "Sub-100ms Turn-Taking, Voice Activity Detection (VAD) & Emotion Classification" },
    { nav: navMetrics, view: viewMetrics, title: "Latency & VAD Performance Metrics", subtitle: "Real-time decibel energy analysis, frame durations, and turn-around distribution" },
    { nav: navClassifier, view: viewClassifier, title: "Intent & Emotion Classifier Sandbox", subtitle: "Test custom text/voice utterances to inspect detected intents and agent routing actions" }
  ];

  views.forEach(item => {
    item.nav.addEventListener("click", (e) => {
      e.preventDefault();
      views.forEach(v => {
        v.nav.classList.remove("active");
        v.view.classList.add("hidden");
      });
      item.nav.classList.add("active");
      item.view.classList.remove("hidden");
      pageTitle.textContent = item.title;
      pageSubtitle.textContent = item.subtitle;

      if (item.nav === navMetrics) renderMetricsCharts();
    });
  });

  // Classifier Sandbox Handler
  btnTestClassifier.addEventListener("click", () => {
    const text = classifierInput.value.trim();
    if (!text) return;

    fetch("/api/v1/voice/process-audio", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_transcript: text })
    })
    .then(res => res.json())
    .then(turn => {
      const ia = turn.intent_analysis;
      resIntent.textContent = ia.intent;
      resEmotion.textContent = ia.emotion;
      resConfidence.textContent = `${(ia.confidence * 100).toFixed(0)}%`;
      resEntities.textContent = JSON.stringify(ia.detected_entities);
      resAction.textContent = ia.recommended_action;
      classifierResultBox.classList.remove("hidden");
    });
  });

  // Render Chart.js Performance Analytics
  function renderMetricsCharts() {
    if (latencyChartInstance) latencyChartInstance.destroy();
    const ctx1 = document.getElementById("latencyChart").getContext("2d");
    latencyChartInstance = new Chart(ctx1, {
      type: "bar",
      data: {
        labels: ["Turn 1", "Turn 2", "Turn 3", "Turn 4", "Turn 5", "Turn 6"],
        datasets: [{
          label: "Latency (ms)",
          data: [42, 48, 51, 44, 46, 48],
          backgroundColor: "#6366F1",
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { ticks: { color: "#94A3B8" }, grid: { color: "rgba(255,255,255,0.08)" } },
          x: { ticks: { color: "#94A3B8" }, grid: { display: false } }
        }
      }
    });

    if (vadRatioChartInstance) vadRatioChartInstance.destroy();
    const ctx2 = document.getElementById("vadRatioChart").getContext("2d");
    vadRatioChartInstance = new Chart(ctx2, {
      type: "doughnut",
      data: {
        labels: ["Active Speech", "Silence / Noise Floor"],
        datasets: [{
          data: [78, 22],
          backgroundColor: ["#10B981", "#334155"],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "bottom", labels: { color: "#94A3B8" } } }
      }
    });
  }

  // Load High-Quality Natural / Neural Voices
  function loadNaturalVoices() {
    if ('speechSynthesis' in window) {
      availableVoices = window.speechSynthesis.getVoices();
    }
  }

  loadNaturalVoices();
  if ('speechSynthesis' in window) {
    window.speechSynthesis.onvoiceschanged = loadNaturalVoices;
  }

  // 1. Initialize HTML5 Canvas Animated Sine Wave Visualizer
  function drawWaveform() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.lineWidth = 2;
    ctx.strokeStyle = isListening ? "#10B981" : "#6366F1";
    ctx.beginPath();

    const time = Date.now() * 0.006;
    const sliceWidth = canvas.width / 100;
    let x = 0;

    for (let i = 0; i < 100; i++) {
      const currentAmp = isListening ? (audioAmp + Math.random() * 20) : 10;
      const y = (canvas.height / 2) + Math.sin(i * 0.12 + time) * currentAmp * Math.cos(i * 0.06);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
      x += sliceWidth;
    }

    ctx.stroke();
    animationId = requestAnimationFrame(drawWaveform);
  }

  drawWaveform();

  // 2. Initialize Web Speech API
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      let finalTranscript = "";
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        }
      }
      if (finalTranscript.trim()) {
        sendVoiceText(finalTranscript.trim());
      }
    };

    recognition.onerror = (err) => {
      console.warn("Speech Recognition Error:", err.error);
    };

    recognition.onend = () => {
      if (isListening) {
        try { recognition.start(); } catch(e) {}
      }
    };
  }

  // 3. Connect WebSocket Stream
  function connectWebSocket() {
    const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${wsProtocol}//${window.location.host}/ws/voice`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      connectionStatus.textContent = "WebSocket Connected";
    };

    ws.onmessage = (event) => {
      const turnData = JSON.parse(event.data);
      renderTurnCard(turnData);
      speakText(turnData.ai_response_text);
    };

    ws.onclose = () => {
      connectionStatus.textContent = "Disconnected (Retrying...)";
      setTimeout(connectWebSocket, 3000);
    };
  }

  connectWebSocket();

  // 4. Natural Neural Voice Output Engine
  function speakText(text) {
    if (!('speechSynthesis' in window)) return;

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.02;
    utterance.pitch = 1.05;
    utterance.volume = 1.0;

    if (!availableVoices.length) {
      availableVoices = window.speechSynthesis.getVoices();
    }

    const naturalVoice = availableVoices.find(v => 
      v.lang.startsWith("en") && (
        v.name.includes("Natural") || 
        v.name.includes("Neural") || 
        v.name.includes("Google US English") || 
        v.name.includes("Samantha") || 
        v.name.includes("Jenny") || 
        v.name.includes("Guy") || 
        v.name.includes("Online")
      )
    ) || availableVoices.find(v => v.lang.startsWith("en"));

    if (naturalVoice) {
      utterance.voice = naturalVoice;
    }

    window.speechSynthesis.speak(utterance);
  }

  // 5. Preset Test Buttons
  document.querySelectorAll(".preset-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const text = btn.getAttribute("data-text");
      sendVoiceText(text);
    });
  });

  // 6. Mic Button Toggle
  btnToggleMic.addEventListener("click", () => {
    isListening = !isListening;

    if (isListening) {
      btnToggleMic.innerHTML = `<span>Stop Voice Stream</span>`;
      btnToggleMic.style.background = "#F43F5E";
      audioAmp = 35;

      if (recognition) {
        try { recognition.start(); } catch(e) {}
      } else {
        alert("Web Speech API not supported in this browser. Use Chrome/Edge or click Preset Buttons above.");
      }
    } else {
      btnToggleMic.innerHTML = `<span>Start Voice Stream</span>`;
      btnToggleMic.style.background = "";
      audioAmp = 10;

      if (recognition) {
        try { recognition.stop(); } catch(e) {}
      }
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    }
  });

  function sendVoiceText(text) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ text: text }));
    } else {
      fetch("/api/v1/voice/process-audio", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_transcript: text })
      })
      .then(res => res.json())
      .then(data => {
        renderTurnCard(data);
        speakText(data.ai_response_text);
      });
    }
  }

  function renderTurnCard(turn) {
    const emptyLog = document.querySelector(".empty-log");
    if (emptyLog) emptyLog.remove();

    latencyValue.textContent = `${turn.latency_ms} ms`;

    const card = document.createElement("div");
    card.className = "turn-card";

    const emotion = turn.intent_analysis.emotion || "CALM";
    let emotionClass = "emotion-calm";
    if (emotion === "URGENT") emotionClass = "emotion-urgent";
    else if (emotion === "FRUSTRATED") emotionClass = "emotion-frustrated";
    else if (emotion === "EXCITED") emotionClass = "emotion-excited";

    card.innerHTML = `
      <div class="turn-header">
        <span class="emotion-badge ${emotionClass}">EMOTION: ${emotion}</span>
        <span style="font-size: 0.72rem; color: #94A3B8;">INTENT: ${turn.intent_analysis.intent} (${turn.latency_ms}ms)</span>
      </div>
      <div class="user-bubble"><strong>👤 User:</strong> ${turn.user_transcript}</div>
      <div class="ai-bubble"><strong>🤖 Voice AI:</strong> ${turn.ai_response_text}</div>
    `;

    transcriptLog.prepend(card);
  }
});

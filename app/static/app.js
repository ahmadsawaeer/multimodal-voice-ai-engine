document.addEventListener("DOMContentLoaded", () => {
  const btnToggleMic = document.getElementById("btnToggleMic");
  const transcriptLog = document.getElementById("transcriptLog");
  const latencyValue = document.getElementById("latencyValue");
  const canvas = document.getElementById("waveformCanvas");
  const ctx = canvas.getContext("2d");

  let ws = null;
  let isStreaming = false;
  let animationId = null;

  // Initialize Animated Sine Wave Visualizer
  function drawWaveform() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.lineWidth = 2;
    ctx.strokeStyle = isStreaming ? "#10B981" : "#6366F1";
    ctx.beginPath();

    const time = Date.now() * 0.005;
    const sliceWidth = canvas.width / 100;
    let x = 0;

    for (let i = 0; i < 100; i++) {
      const amp = isStreaming ? 35 : 12;
      const y = (canvas.height / 2) + Math.sin(i * 0.1 + time) * amp * Math.cos(i * 0.05);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
      x += sliceWidth;
    }

    ctx.stroke();
    animationId = requestAnimationFrame(drawWaveform);
  }

  drawWaveform();

  // Connect WebSocket
  function connectWebSocket() {
    const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${wsProtocol}//${window.location.host}/ws/voice`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      document.getElementById("connectionStatus").textContent = "WebSocket Connected";
    };

    ws.onmessage = (event) => {
      const turnData = JSON.parse(event.data);
      renderTurnCard(turnData);
    };

    ws.onclose = () => {
      document.getElementById("connectionStatus").textContent = "Disconnected (Retrying...)";
      setTimeout(connectWebSocket, 3000);
    };
  }

  connectWebSocket();

  // Preset Buttons Click Handler
  document.querySelectorAll(".preset-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const text = btn.getAttribute("data-text");
      sendVoiceText(text);
    });
  });

  btnToggleMic.addEventListener("click", () => {
    isStreaming = !isStreaming;
    if (isStreaming) {
      btnToggleMic.innerHTML = `<span>Stop Voice Stream</span>`;
      btnToggleMic.style.background = "#F43F5E";
      sendVoiceText("Hello Voice Assistant, I want to inquire about Burj Khalifa tours");
    } else {
      btnToggleMic.innerHTML = `<span>Start Voice Stream</span>`;
      btnToggleMic.style.background = "";
    }
  });

  function sendVoiceText(text) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ text: text }));
    } else {
      // HTTP Fallback
      fetch("/api/v1/voice/process-audio", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_transcript: text })
      })
      .then(res => res.json())
      .then(data => renderTurnCard(data));
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

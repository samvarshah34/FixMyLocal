// Toast helper
function showToast(message, duration = 3500) {
  const toast = document.getElementById('toast');
  const toastMsg = document.getElementById('toastMsg');
  toastMsg.textContent = message;
  toast.classList.remove('hidden');
  toast.style.animation = 'none';
  void toast.offsetWidth;
  toast.style.animation = `fadeOut ${duration/1000}s forwards`;
  setTimeout(() => toast.classList.add('hidden'), duration);
}

// Form validation
const form = document.getElementById('reportForm');
const typeInput = document.getElementById('type');
const descInput = document.getElementById('desc');
const typeError = document.getElementById('typeError');
const descError = document.getElementById('descError');
const submitBtn = document.getElementById('submitBtn');

form.addEventListener('submit', e => {
  let valid = true;
  if (!typeInput.value) {
    typeError.classList.remove('hidden'); valid = false;
  } else typeError.classList.add('hidden');
  if (!descInput.value.trim()) {
    descError.classList.remove('hidden'); valid = false;
  } else descError.classList.add('hidden');
  if (!valid) {
    e.preventDefault();
    showToast('Please fix errors before submitting.');
    return;
  }
  submitBtn.disabled = true;
  submitBtn.textContent = 'Submitting...';
});

// Geolocation
window.onload = () => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(pos => {
      // lat/lng handled on server or separate map page
    }, () => showToast('⚠️ Could not get location.'));
  } else showToast('⚠️ Geolocation not supported.');
};

// Voice input with continuous 60s listening and timer
let recog, recording = false, timerInterval;
const startBtn = document.getElementById('startRec');
const stopBtn = document.getElementById('stopRec');
const recStatus = document.getElementById('recStatus');
const timerSpan = document.getElementById('timer');

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  recog = new SpeechRec();
  recog.interimResults = false;
  recog.continuous = true;

  let finalTranscript = '';

  recog.onresult = e => {
    for (let i = e.resultIndex; i < e.results.length; ++i) {
      if (e.results[i].isFinal) {
        finalTranscript += (finalTranscript ? ' ' : '') + e.results[i][0].transcript;
      }
    }
    descInput.value = finalTranscript;
    recStatus.textContent = '🎙️ Listening...';
  };

  recog.onerror = e => {
    recStatus.textContent = '🎙️ Error: ' + e.error;
    showToast('🎙️ Speech recognition error: ' + e.error);
  };

  recog.onend = () => {
    if (recording) recog.start();
    else {
      startBtn.disabled = false;
      stopBtn.disabled = true;
      recStatus.textContent = '';
      clearInterval(timerInterval);
      timerSpan.textContent = '';
    }
  };
} else {
  recStatus.textContent = '⚠️ Speech API not supported.';
  startBtn.disabled = true;
}

function startTimer(seconds) {
  let timeLeft = seconds;
  timerSpan.textContent = formatTime(timeLeft);
  timerInterval = setInterval(() => {
    timeLeft--;
    timerSpan.textContent = formatTime(timeLeft);
    if (timeLeft <= 0) {
      clearInterval(timerInterval);
      stopRecording();
    }
  }, 1000);
}

function formatTime(sec) {
  const m = Math.floor(sec/60).toString().padStart(2,'0');
  const s = (sec%60).toString().padStart(2,'0');
  return `${m}:${s}`;
}

function stopRecording() {
  if (recording) {
    recording = false;
    recog.stop();
    startBtn.disabled = false;
    stopBtn.disabled = true;
    recStatus.textContent = '🎙️ Processing...';
    clearInterval(timerInterval);
    timerSpan.textContent = '';
  }
}

startBtn.onclick = () => {
  if (!recording) {
    finalTranscript = '';
    recog.lang = document.getElementById('lang').value;
    const utterance = new SpeechSynthesisUtterance('Recording now');
    speechSynthesis.speak(utterance);
    recog.start();
    recording = true;
    recStatus.textContent = '🎙️ Listening...';
    startBtn.disabled = true;
    stopBtn.disabled = false;
    startTimer(60);
  }
};
stopBtn.onclick = stopRecording;

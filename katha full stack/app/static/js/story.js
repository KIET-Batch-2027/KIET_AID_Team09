(() => {
  const storyTextElement = document.getElementById('storyText');
  if (!storyTextElement) return;

  let currentUtterance = null;
  let translatedText = storyTextElement.textContent;

  const playBtn = document.getElementById('playBtn');
  const pauseBtn = document.getElementById('pauseBtn');
  const stopBtn = document.getElementById('stopBtn');
  const voiceSelect = document.getElementById('voiceSelect');
  const translateBtn = document.getElementById('translateBtn');
  const translateLang = document.getElementById('translateLang');
  const promptInput = document.getElementById('promptInput');
  const voiceInputBtn = document.getElementById('voiceInputBtn');

  const stripForSpeech = (text) => text.replace(/[\*\"'`:;!?#~.,()\[\]{}]/g, ' ');

  const stopSpeech = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      currentUtterance = null;
    }
  };

  const pickVoice = (langCode) => {
    const voices = window.speechSynthesis.getVoices();
    const exact = voices.find((v) => v.lang.toLowerCase() === langCode.toLowerCase());
    if (exact) return exact;
    return voices.find((v) => v.lang.toLowerCase().startsWith(langCode.split('-')[0].toLowerCase()));
  };

  playBtn?.addEventListener('click', () => {
    stopSpeech();
    const text = stripForSpeech(translatedText || storyTextElement.textContent || '');
    currentUtterance = new SpeechSynthesisUtterance(text);
    const selectedLang = voiceSelect?.value || 'en-IN';
    currentUtterance.lang = selectedLang;
    const voice = pickVoice(selectedLang);
    if (voice) currentUtterance.voice = voice;
    window.speechSynthesis.speak(currentUtterance);
  });

  pauseBtn?.addEventListener('click', () => {
    if (window.speechSynthesis.speaking) {
      if (window.speechSynthesis.paused) window.speechSynthesis.resume();
      else window.speechSynthesis.pause();
    }
  });

  stopBtn?.addEventListener('click', stopSpeech);

  translateBtn?.addEventListener('click', async () => {
    const text = storyTextElement.textContent;
    const language = translateLang?.value || 'en';

    try {
      const res = await fetch(window.kathaTranslateEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text, language })
      });
      const data = await res.json();
      if (!data.ok) return;
      translatedText = data.text;
      storyTextElement.textContent = data.text;
      if (voiceSelect) voiceSelect.value = data.voice;
      stopSpeech();
    } catch (_err) {
      // Keep page usable even when translation API fails.
    }
  });

  if (voiceInputBtn && promptInput) {
    voiceInputBtn.addEventListener('click', () => {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) return;

      const recognition = new SpeechRecognition();
      recognition.lang = 'en-IN';
      recognition.interimResults = false;
      recognition.maxAlternatives = 1;
      recognition.start();
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        promptInput.value = transcript;
      };
    });
  }

  window.addEventListener('beforeunload', stopSpeech);
  document.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', stopSpeech);
  });
})();
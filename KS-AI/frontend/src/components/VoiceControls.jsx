import { useState } from "react";

export default function VoiceControls() {
  const [listening, setListening] = useState(false);

  const startListening = () => {
    const recognition = new window.webkitSpeechRecognition();
    recognition.lang = "en-US";
    recognition.start();
    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript;
      document.getElementById("msgInput").value = text;
    };
    setListening(true);
    recognition.onend = () => setListening(false);
  };

  return (
    <div className="p-2 bg-gray-200">
      <button
        className={`px-4 py-2 rounded ${listening ? "bg-red-500" : "bg-green-500"} text-white`}
        onClick={startListening}
      >
        {listening ? "🎙 Listening..." : "🎤 Voice Input"}
      </button>
    </div>
  );
}

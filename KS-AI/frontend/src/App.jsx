import { useState } from "react";
import AgentSelect from "./components/AgentSelect";
import ChatWindow from "./components/ChatWindow";
import UploadBox from "./components/UploadBox";
import VoiceControls from "./components/VoiceControls";

function App() {
  const [agent, setAgent] = useState("default");

  return (
    <div className="flex flex-col h-screen">
      <header className="flex items-center gap-2 bg-green-700 text-white p-3 font-bold text-lg">
        <img src="/KSAI logo.png" alt="KS-AI Logo" className="h-10" />
        KS-AI
      </header>
      <AgentSelect agent={agent} setAgent={setAgent} />
      <UploadBox />
      <VoiceControls />
      <ChatWindow agent={agent} />
    </div>
  );
}

export default App;

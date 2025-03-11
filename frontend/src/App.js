import React, { useState } from "react";

function App() {
  const [logText, setLogText] = useState("");
  const [resolution, setResolution] = useState("");
  const [responseMessage, setResponseMessage] = useState("");

  // Function to send log data to FastAPI backend
  const submitLog = async () => {
    if (!logText.trim() || !resolution.trim()) {
      setResponseMessage("Both log text and resolution fields are required.");
      return;
    }
    try {
      const response = await fetch("http://localhost:8000/logs/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          log_text: logText,
          resolution: resolution
        }),
      });
  
      const data = await response.json();
      setResponseMessage(data.message);
    } catch (error) {
      console.error("Error:", error);
      setResponseMessage("Failed to submit log.");
    }
  };

  return (
    <div className="container">
      <h1>Log Input Chatbot</h1>
      <textarea
        placeholder="Enter log text..."
        value={logText}
        onChange={(e) => setLogText(e.target.value)}
      />
      <textarea
        placeholder="Enter resolution..."
        value={resolution}
        onChange={(e) => setResolution(e.target.value)}
      />
      <button onClick={submitLog}>Submit Log</button>
      {responseMessage && <p className="response">{responseMessage}</p>}
    </div>
  );
}

export default App;

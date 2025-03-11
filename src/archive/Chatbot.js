import React, { useState } from 'react';
import './Chatbot.css';

const Chatbot = () => {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState([]);

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Display user message
        setMessages([...messages, { text: input, from: 'user' }]);

        // Send input to the backend API
        try {
            const response = await fetch('http://127.0.0.1:8000/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ input: parseFloat(input) }),
            });
            const data = await response.json();
            // Display AI response
            setMessages([...messages, { text: input, from: 'user' }, { text: data.prediction, from: 'bot' }]);
        } catch (error) {
            console.error('Error:', error);
        }

        setInput('');
    };

    return (
        <div>
            <div className="chat-box">
                {messages.map((message, index) => (
                    <div key={index} className={message.from === 'user' ? 'user-message' : 'bot-message'}>
                        {message.text}
                    </div>
                ))}
            </div>
            <form onSubmit={handleSubmit}>
                <input
                    type="number"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type a number"
                />
                <button type="submit">Send</button>
            </form>
        </div>
    );
};

export default Chatbot;

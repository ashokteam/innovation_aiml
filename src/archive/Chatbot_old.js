import React, { useState } from 'react';

function Chatbot() {
    const [input, setInput] = useState('');
    
    const handleChange = (e) => {
        setInput(e.target.value);
    };

    const handleSubmit = () => {
        console.log('User Input:', input);
        // Add your logic to call the backend API for predictions
    };

    return (
        <div className="chatbot-container">
            <input 
                type="text" 
                value={input} 
                onChange={handleChange} 
                placeholder="Enter your message"
            />
            <button onClick={handleSubmit}>Submit</button>
        </div>
    );
}

export default Chatbot;

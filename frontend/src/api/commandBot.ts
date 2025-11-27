import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const askCommandBot = async (question: string): Promise<{ answer: string }> => {
    const response = await axios.post(`${API_BASE}/api/command-bot/query`, { question });
    return response.data;
};

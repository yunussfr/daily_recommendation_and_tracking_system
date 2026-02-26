import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const submitDailyData = async (payload: any) => {
    const response = await api.post('/submit_daily', payload);
    return response.data;
};

// Mock endpoint that might be added to backend later for dashboard stats
export const getStats = async (_userId: string) => {
    // In a real scenario, this would call GET /api/stats
    // For now, let's mock the response:
    return {
        streak: 5,
        totalEntries: 20,
        averageMood: 'Happy',
        completedHabits: 85
    };
};

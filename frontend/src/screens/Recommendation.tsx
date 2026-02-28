import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Sparkles, Home } from 'lucide-react';

export const Recommendation = () => {
    const navigate = useNavigate();
    const [data, setData] = useState<{ message: string; suggested_activity: string } | null>(null);

    useEffect(() => {
        const raw = localStorage.getItem('recommendation');
        if (raw) {
            try {
                setData(JSON.parse(raw));
            } catch (e) {
                console.error("Parse error", e);
            }
        }
    }, []);

    if (!data) {
        return (
            <div className="glass-card p-6 text-center">
                <p>No recommendation available. Try submitting your daily logs first.</p>
                <button onClick={() => navigate('/dashboard')} className="text-purple-400 mt-4 underline">
                    Go back to Goals
                </button>
            </div>
        );
    }

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="glass-card p-8 flex flex-col items-center text-center gap-6"
        >
            <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-purple-500 to-pink-500 flex items-center justify-center animate-bounce-soft">
                <Sparkles className="text-white" size={32} />
            </div>

            <div className="space-y-4">
                <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-purple-200">
                    Your Daily Insight
                </h2>
                <p className="text-gray-200 leading-relaxed font-medium">
                    "{data.message}"
                </p>
            </div>

            <div className="bg-white/10 rounded-xl p-4 w-full border border-white/5 space-y-2 text-left">
                <div className="text-xs uppercase text-purple-300 font-bold tracking-wider">
                    Suggested Activity
                </div>
                <p className="text-sm text-gray-300">
                    {data.suggested_activity}
                </p>
            </div>

            <button
                onClick={() => {
                    localStorage.removeItem('recommendation');
                    navigate('/');
                }}
                className="w-full bg-white/5 border border-white/10 rounded-xl py-3 flex items-center justify-center gap-2 transition-all hover:bg-white/10 active:scale-95"
            >
                <Home size={18} />
                <span>Return Home</span>
            </button>
        </motion.div>
    );
};

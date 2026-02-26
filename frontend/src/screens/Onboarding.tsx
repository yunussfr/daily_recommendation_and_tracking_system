import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { LogIn } from 'lucide-react';

export const Onboarding = () => {
    const [telegramId, setTelegramId] = useState('');
    const navigate = useNavigate();

    const handleStart = (e: React.FormEvent) => {
        e.preventDefault();
        if (telegramId.trim()) {
            localStorage.setItem('telegramId', telegramId);
            navigate('/mood');
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.4 }}
            className="glass-card p-8 flex flex-col gap-6"
        >
            <div className="text-center space-y-2">
                <h1 className="text-3xl font-bold">Welcome back.</h1>
                <p className="text-purple-300 font-medium">Let's crush today.</p>
            </div>

            <p className="text-center text-sm text-gray-400">
                Enter your Telegram ID to track your progress and receive personalized daily motivation.
            </p>

            <form onSubmit={handleStart} className="flex flex-col gap-4">
                <div className="relative">
                    <input
                        type="text"
                        value={telegramId}
                        onChange={(e) => setTelegramId(e.target.value)}
                        placeholder="Telegram Chat ID"
                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/30 focus:outline-none focus:ring-2 focus:ring-purple-500/50 transition-all"
                        required
                    />
                </div>

                <button type="submit" className="glass-button flex items-center justify-center gap-2">
                    <span>Get Started</span>
                    <LogIn size={18} />
                </button>
            </form>
        </motion.div>
    );
};

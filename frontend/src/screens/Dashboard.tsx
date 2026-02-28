import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { BookOpen, Dumbbell, Droplets, Code, Send } from 'lucide-react';
import { submitDailyData } from '../services/api';

export const Dashboard = () => {
    const navigate = useNavigate();
    const [isSubmitting, setIsSubmitting] = useState(false);

    const [habits, setHabits] = useState({
        pages_read: 0,
        workout_minutes: 0,
        water_glasses: 0,
        coding_hours: 0
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setHabits({
            ...habits,
            [e.target.name]: parseFloat(e.target.value) || 0
        });
    };

    const handleSubmit = async () => {
        const telegramId = localStorage.getItem('telegramId');
        const answer = localStorage.getItem('answer') || 'Feeling good!';

        if (!telegramId) {
            navigate('/');
            return;
        }

        setIsSubmitting(true);

        try {
            const response = await submitDailyData({
                telegram_chat_id: telegramId,
                answer: answer,
                habits: habits
            });

            // Store recommendation
            localStorage.setItem('recommendation', JSON.stringify(response));
            navigate('/recommendation');
        } catch (err) {
            console.error('Submission failed', err);
            // Fallback for demo if backend is offline
            localStorage.setItem('recommendation', JSON.stringify({
                message: "You're doing great! Keep building those habits.",
                suggested_activity: "Take a 5-minute break and stretch."
            }));
            navigate('/recommendation');
        } finally {
            setIsSubmitting(false);
        }
    };

    const container = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: { staggerChildren: 0.1 }
        }
    };

    const item = {
        hidden: { opacity: 0, y: 20 },
        show: { opacity: 1, y: 0 }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="glass-card p-6 flex flex-col gap-6"
        >
            <div>
                <h2 className="text-2xl font-bold mb-1">Daily Goals</h2>
                <p className="text-sm text-gray-400">Consistency is your superpower.</p>
            </div>

            <motion.div
                variants={container}
                initial="hidden"
                animate="show"
                className="grid grid-cols-2 gap-4"
            >
                <motion.div variants={item} className="bg-white/5 border border-white/10 rounded-2xl p-4 flex flex-col gap-3">
                    <div className="flex items-center gap-2">
                        <BookOpen className="text-blue-400" size={20} />
                        <span className="font-semibold">Reading</span>
                    </div>
                    <div className="flex items-center justify-between mt-auto">
                        <span className="text-xs text-gray-400">Pages</span>
                        <input
                            type="number" name="pages_read" min="0"
                            value={habits.pages_read || ''} onChange={handleChange}
                            className="w-16 bg-white/10 rounded-lg p-1 text-center focus:outline-none focus:ring-1 focus:ring-blue-400"
                        />
                    </div>
                </motion.div>

                <motion.div variants={item} className="bg-white/5 border border-white/10 rounded-2xl p-4 flex flex-col gap-3">
                    <div className="flex items-center gap-2">
                        <Dumbbell className="text-green-400" size={20} />
                        <span className="font-semibold">Workout</span>
                    </div>
                    <div className="flex items-center justify-between mt-auto">
                        <span className="text-xs text-gray-400">Mins</span>
                        <input
                            type="number" name="workout_minutes" min="0"
                            value={habits.workout_minutes || ''} onChange={handleChange}
                            className="w-16 bg-white/10 rounded-lg p-1 text-center focus:outline-none focus:ring-1 focus:ring-green-400"
                        />
                    </div>
                </motion.div>

                <motion.div variants={item} className="bg-white/5 border border-white/10 rounded-2xl p-4 flex flex-col gap-3">
                    <div className="flex items-center gap-2">
                        <Droplets className="text-cyan-400" size={20} />
                        <span className="font-semibold">Water</span>
                    </div>
                    <div className="flex items-center justify-between mt-auto">
                        <span className="text-xs text-gray-400">Glasses</span>
                        <input
                            type="number" name="water_glasses" min="0"
                            value={habits.water_glasses || ''} onChange={handleChange}
                            className="w-16 bg-white/10 rounded-lg p-1 text-center focus:outline-none focus:ring-1 focus:ring-cyan-400"
                        />
                    </div>
                </motion.div>

                <motion.div variants={item} className="bg-white/5 border border-white/10 rounded-2xl p-4 flex flex-col gap-3">
                    <div className="flex items-center gap-2">
                        <Code className="text-purple-400" size={20} />
                        <span className="font-semibold">Coding</span>
                    </div>
                    <div className="flex items-center justify-between mt-auto">
                        <span className="text-xs text-gray-400">Hours</span>
                        <input
                            type="number" name="coding_hours" min="0" step="0.5"
                            value={habits.coding_hours || ''} onChange={handleChange}
                            className="w-16 bg-white/10 rounded-lg p-1 text-center focus:outline-none focus:ring-1 focus:ring-purple-400"
                        />
                    </div>
                </motion.div>
            </motion.div>

            <button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="glass-button flex justify-center items-center gap-2 mt-4"
            >
                {isSubmitting ? (
                    <span className="animate-pulse">Syncing...</span>
                ) : (
                    <>
                        <span>Submit Entry</span>
                        <Send size={18} />
                    </>
                )}
            </button>
        </motion.div>
    );
};

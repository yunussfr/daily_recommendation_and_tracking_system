import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { BookOpen, Dumbbell, Droplets, Code, Send, CheckCircle2, Circle } from 'lucide-react';
import { submitDailyData } from '../services/api';

export const Dashboard = () => {
    const navigate = useNavigate();
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [username, setUsername] = useState('Misafir');

    // Hedeflerin tamamlanma durumunu tutan state (Sayı yerine boolean mantığı)
    const [habits, setHabits] = useState({
        reading: false,
        workout: false,
        water: false,
        coding: false
    });

    useEffect(() => {
        // Login ekranından kaydedilen kullanıcı adını çekiyoruz
        const storedUser = localStorage.getItem('dailyflow_user');
        if (storedUser) {
            setUsername(storedUser);
        }
    }, []);

    const toggleHabit = (habitName: keyof typeof habits) => {
        setHabits(prev => ({
            ...prev,
            [habitName]: !prev[habitName]
        }));
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
            // API'ye boolean değerleri (veya backend nasıl istiyorsa ona göre sayı) gönderiyoruz
            const response = await submitDailyData({
                telegram_chat_id: telegramId,
                answer: answer,
                habits: {
                    pages_read: habits.reading ? 1 : 0,
                    workout_minutes: habits.workout ? 1 : 0,
                    water_glasses: habits.water ? 1 : 0,
                    coding_hours: habits.coding ? 1 : 0
                }
            });

            localStorage.setItem('recommendation', JSON.stringify(response));
            navigate('/recommendation');
        } catch (err) {
            console.error('Submission failed', err);
            localStorage.setItem('recommendation', JSON.stringify({
                message: "Harika gidiyorsun! Bu alışkanlıkları inşa etmeye devam et.",
                suggested_activity: "Kısa bir mola ver ve esne."
            }));
            navigate('/recommendation');
        } finally {
            setIsSubmitting(false);
        }
    };

    const container = {
        hidden: { opacity: 0 },
        show: { opacity: 1, transition: { staggerChildren: 0.1 } }
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
            className="w-full flex flex-col gap-6"
        >
            {/* Karşılama Alanı */}
            <div className="bg-white/60 dark:bg-dark/40 backdrop-blur-xl rounded-3xl p-8 border border-gray-200 dark:border-gray-800 shadow-xl">
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                    Tekrar Hoş Geldin, <span className="text-primary">{username}</span> 👋
                </h1>
                <p className="text-gray-600 dark:text-gray-400">
                    Bugün hangi hedeflerini tamamladın? İşaretle ve gününü taçlandır.
                </p>
            </div>

            {/* Hedefler Alanı */}
            <motion.div
                variants={container}
                initial="hidden"
                animate="show"
                className="grid grid-cols-1 sm:grid-cols-2 gap-4"
            >
                {/* Okuma Hedefi */}
                <motion.div 
                    variants={item}
                    onClick={() => toggleHabit('reading')}
                    className={`cursor-pointer rounded-2xl p-5 flex items-center justify-between transition-all duration-300 border ${
                        habits.reading 
                        ? 'bg-blue-500/10 border-blue-500/50 shadow-[0_0_15px_rgba(59,130,246,0.2)]' 
                        : 'bg-white/50 dark:bg-dark/30 border-gray-200 dark:border-gray-800 hover:border-blue-500/30'
                    }`}
                >
                    <div className="flex items-center gap-4">
                        <div className={`p-3 rounded-xl ${habits.reading ? 'bg-blue-500 text-white' : 'bg-gray-100 dark:bg-dark text-blue-400'}`}>
                            <BookOpen size={24} />
                        </div>
                        <div>
                            <h3 className="font-semibold text-gray-900 dark:text-white text-lg">Kitap Okuma</h3>
                            <p className="text-sm text-gray-500 dark:text-gray-400">Günlük hedefini tamamla</p>
                        </div>
                    </div>
                    {habits.reading ? <CheckCircle2 className="text-blue-500" size={28} /> : <Circle className="text-gray-300 dark:text-gray-600" size={28} />}
                </motion.div>

                {/* Egzersiz Hedefi */}
                <motion.div 
                    variants={item}
                    onClick={() => toggleHabit('workout')}
                    className={`cursor-pointer rounded-2xl p-5 flex items-center justify-between transition-all duration-300 border ${
                        habits.workout 
                        ? 'bg-green-500/10 border-green-500/50 shadow-[0_0_15px_rgba(34,197,94,0.2)]' 
                        : 'bg-white/50 dark:bg-dark/30 border-gray-200 dark:border-gray-800 hover:border-green-500/30'
                    }`}
                >
                    <div className="flex items-center gap-4">
                        <div className={`p-3 rounded-xl ${habits.workout ? 'bg-green-500 text-white' : 'bg-gray-100 dark:bg-dark text-green-400'}`}>
                            <Dumbbell size={24} />
                        </div>
                        <div>
                            <h3 className="font-semibold text-gray-900 dark:text-white text-lg">Egzersiz</h3>
                            <p className="text-sm text-gray-500 dark:text-gray-400">Günlük sporu yap</p>
                        </div>
                    </div>
                    {habits.workout ? <CheckCircle2 className="text-green-500" size={28} /> : <Circle className="text-gray-300 dark:text-gray-600" size={28} />}
                </motion.div>

                {/* Su Hedefi */}
                <motion.div 
                    variants={item}
                    onClick={() => toggleHabit('water')}
                    className={`cursor-pointer rounded-2xl p-5 flex items-center justify-between transition-all duration-300 border ${
                        habits.water 
                        ? 'bg-cyan-500/10 border-cyan-500/50 shadow-[0_0_15px_rgba(6,182,212,0.2)]' 
                        : 'bg-white/50 dark:bg-dark/30 border-gray-200 dark:border-gray-800 hover:border-cyan-500/30'
                    }`}
                >
                    <div className="flex items-center gap-4">
                        <div className={`p-3 rounded-xl ${habits.water ? 'bg-cyan-500 text-white' : 'bg-gray-100 dark:bg-dark text-cyan-400'}`}>
                            <Droplets size={24} />
                        </div>
                        <div>
                            <h3 className="font-semibold text-gray-900 dark:text-white text-lg">Su Tüketimi</h3>
                            <p className="text-sm text-gray-500 dark:text-gray-400">Hedeflenen suyu iç</p>
                        </div>
                    </div>
                    {habits.water ? <CheckCircle2 className="text-cyan-500" size={28} /> : <Circle className="text-gray-300 dark:text-gray-600" size={28} />}
                </motion.div>

                {/* Kodlama Hedefi */}
                <motion.div 
                    variants={item}
                    onClick={() => toggleHabit('coding')}
                    className={`cursor-pointer rounded-2xl p-5 flex items-center justify-between transition-all duration-300 border ${
                        habits.coding 
                        ? 'bg-purple-500/10 border-purple-500/50 shadow-[0_0_15px_rgba(168,85,247,0.2)]' 
                        : 'bg-white/50 dark:bg-dark/30 border-gray-200 dark:border-gray-800 hover:border-purple-500/30'
                    }`}
                >
                    <div className="flex items-center gap-4">
                        <div className={`p-3 rounded-xl ${habits.coding ? 'bg-purple-500 text-white' : 'bg-gray-100 dark:bg-dark text-purple-400'}`}>
                            <Code size={24} />
                        </div>
                        <div>
                            <h3 className="font-semibold text-gray-900 dark:text-white text-lg">Kodlama (C)</h3>
                            <p className="text-sm text-gray-500 dark:text-gray-400">Günlük pratiğini yap</p>
                        </div>
                    </div>
                    {habits.coding ? <CheckCircle2 className="text-purple-500" size={28} /> : <Circle className="text-gray-300 dark:text-gray-600" size={28} />}
                </motion.div>
            </motion.div>

            {/* Gönder Butonu */}
            <button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="w-full mt-4 py-4 px-6 rounded-xl flex justify-center items-center gap-2 text-white bg-primary hover:bg-primaryHover focus:ring-4 focus:ring-primary/50 transition-all font-semibold text-lg shadow-lg disabled:opacity-70"
            >
                {isSubmitting ? (
                    <span className="animate-pulse">Güncelleniyor...</span>
                ) : (
                    <>
                        <span>Günü Kaydet</span>
                        <Send size={20} />
                    </>
                )}
            </button>
        </motion.div>
    );
};

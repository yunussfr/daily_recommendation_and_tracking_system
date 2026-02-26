import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';

const MOODS = [
    { id: 'happy', emoji: '🤩', label: 'Hyped', desc: 'LFG!' },
    { id: 'neutral', emoji: '😎', label: 'Chilled', desc: 'VIBING' },
    { id: 'sad', emoji: '😴', label: 'Tired', desc: 'NEED REST' },
    { id: 'motivated', emoji: '🎯', label: 'Focused', desc: 'IN THE ZONE' },
    { id: 'stressed', emoji: '🤯', label: 'Stressed', desc: 'OVERWHELMED' }
];

export const MoodSelection = () => {
    const [selectedMood, setSelectedMood] = useState<string | null>(null);
    const [answer, setAnswer] = useState('');
    const navigate = useNavigate();

    const handleNext = () => {
        if (selectedMood && answer.trim()) {
            localStorage.setItem('mood', selectedMood);
            localStorage.setItem('answer', answer);
            navigate('/dashboard');
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="glass-card p-6 flex flex-col gap-6"
        >
            <div>
                <h2 className="text-2xl font-bold mb-1">How are you feeling right now?</h2>
                <div className="h-1 w-16 bg-gradient-to-r from-green-400 to-emerald-400 rounded-full"></div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {MOODS.map((mood) => (
                    <button
                        key={mood.id}
                        onClick={() => setSelectedMood(mood.id)}
                        className={`mood-btn ${selectedMood === mood.id ? 'selected' : ''}`}
                    >
                        <span className="text-4xl mb-2">{mood.emoji}</span>
                        <span className="font-semibold text-sm">{mood.label}</span>
                        <span className="text-[10px] text-gray-400 mt-1">{mood.desc}</span>
                    </button>
                ))}
            </div>

            <div className="mt-4">
                <label className="text-sm text-gray-300 font-medium mb-2 block">
                    Journal Entry
                </label>
                <textarea
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                    placeholder="What's on your mind? e.g. 'Ready to conquer the day!'"
                    className="w-full bg-white/5 border border-white/10 rounded-xl p-4 text-sm text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 resize-none h-24"
                />
            </div>

            <button
                onClick={handleNext}
                disabled={!selectedMood || !answer.trim()}
                className="glass-button flex items-center justify-between mt-2"
            >
                <span>Continue to Goals</span>
                <ArrowRight size={18} />
            </button>
        </motion.div>
    );
};

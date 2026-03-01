import { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Moon, Sun } from 'lucide-react'; // İkonları ekledik

export const Layout = () => {
    // Tema state'i (Varsayılan olarak karanlık)
    const [isDarkMode, setIsDarkMode] = useState(true);

    // Tema değiştiğinde body class'ını ve localStorage'ı güncelle
    useEffect(() => {
        const storedTheme = localStorage.getItem('theme');
        if (storedTheme === 'light') {
            setIsDarkMode(false);
            document.documentElement.classList.remove('dark');
        } else {
            setIsDarkMode(true);
            document.documentElement.classList.add('dark');
        }
    }, []);

    const toggleTheme = () => {
        setIsDarkMode(!isDarkMode);
        if (isDarkMode) {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        } else {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        }
    };

    return (
        <div className="relative min-h-screen w-full flex flex-col items-center justify-center p-4 bg-gray-50 dark:bg-darker transition-colors duration-300">
            {/* Şık Arka Plan Gradient'leri */}
            <motion.div
                animate={{ scale: [1, 1.2, 1], rotate: [0, 90, 0] }}
                transition={{ duration: 15, repeat: Infinity, ease: 'linear' }}
                className="fixed top-[-10%] left-[-10%] w-96 h-96 bg-primary/20 rounded-full blur-[100px] pointer-events-none"
            />
            <motion.div
                animate={{ scale: [1, 1.5, 1], rotate: [0, -90, 0] }}
                transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                className="fixed bottom-[-10%] right-[-10%] w-96 h-96 bg-blue-500/20 rounded-full blur-[100px] pointer-events-none"
            />

            <div className="z-10 w-full max-w-2xl relative">
                <header className="mb-8 flex justify-between items-center w-full">
                    <motion.div
                        initial={{ y: -20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        className="flex items-center gap-2"
                    >
                        <span className="text-3xl font-bold text-gray-900 dark:text-white tracking-tight">
                            Daily<span className="text-primary">Flow</span>
                        </span>
                    </motion.div>

                    {/* Tema Değiştirme Butonu */}
                    <motion.button
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        onClick={toggleTheme}
                        className="p-2 rounded-full bg-white/50 dark:bg-dark/50 backdrop-blur-md border border-gray-200 dark:border-gray-800 text-gray-700 dark:text-gray-300 hover:text-primary transition-all"
                    >
                        {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
                    </motion.button>
                </header>

                <main className="w-full">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

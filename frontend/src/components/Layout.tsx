
import { Outlet } from 'react-router-dom';
import { motion } from 'framer-motion';

export const Layout = () => {
    return (
        <div className="relative min-h-screen w-full flex flex-col items-center justify-center p-4">
            {/* Background blobs for aesthetics */}
            <motion.div
                animate={{ scale: [1, 1.2, 1], rotate: [0, 90, 0] }}
                transition={{ duration: 15, repeat: Infinity, ease: 'linear' }}
                className="fixed top-[-10%] left-[-10%] w-96 h-96 bg-purple-600/20 rounded-full blur-[100px] pointer-events-none"
            />
            <motion.div
                animate={{ scale: [1, 1.5, 1], rotate: [0, -90, 0] }}
                transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                className="fixed bottom-[-10%] right-[-10%] w-96 h-96 bg-blue-600/20 rounded-full blur-[100px] pointer-events-none"
            />

            <div className="z-10 w-full max-w-md">
                <header className="mb-8 flex justify-center">
                    <motion.div
                        initial={{ y: -20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        className="flex items-center gap-2"
                    >
                        <span className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-400">
                            ⚡ DailyFlow
                        </span>
                    </motion.div>
                </header>

                <main className="w-full">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

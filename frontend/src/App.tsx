import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';

import { Layout } from './components/Layout';
import { Login } from './screens/Login'; // YENİ EKLENDİ
import { Onboarding } from './screens/Onboarding';
import { MoodSelection } from './screens/MoodSelection';
import { Dashboard } from './screens/Dashboard';
import { Recommendation } from './screens/Recommendation';

function App() {
  return (
    <BrowserRouter>
      <AnimatePresence mode="wait">
        <Routes>
          {/* Ana sayfa artık Login ekranı. Layout'un dışında tutuyoruz ki tam ekran olsun. */}
          <Route path="/" element={<Login />} />

          {/* Diğer sayfalar Layout'un içinde */}
          <Route element={<Layout />}>
            <Route path="onboarding" element={<Onboarding />} />
            <Route path="mood" element={<MoodSelection />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="recommendation" element={<Recommendation />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AnimatePresence>
    </BrowserRouter>
  );
}

export default App;

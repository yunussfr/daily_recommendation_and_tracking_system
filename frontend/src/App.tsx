
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';

import { Layout } from './components/Layout';
import { Onboarding } from './screens/Onboarding';
import { MoodSelection } from './screens/MoodSelection';
import { Dashboard } from './screens/Dashboard';
import { Recommendation } from './screens/Recommendation';

function App() {
  return (
    <BrowserRouter>
      <AnimatePresence mode="wait">
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Onboarding />} />
            <Route path="mood" element={<MoodSelection />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="recommendation" element={<Recommendation />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </AnimatePresence>
    </BrowserRouter>
  );
}

export default App;

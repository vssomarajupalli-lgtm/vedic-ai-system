import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';

import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Results from './pages/Results';
import QuestionEngine from './pages/QuestionEngine';
import ExportReport from './pages/ExportReport';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="upload" element={<Upload />} />
          <Route path="results" element={<Results />} />
          <Route path="ask" element={<QuestionEngine />} />
          <Route path="export" element={<ExportReport />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;

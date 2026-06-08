import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';

// Placeholder Pages
const Dashboard = () => <div className="p-8 text-center text-xl text-slate-500">Dashboard Page Coming Soon</div>;
const Upload = () => <div className="p-8 text-center text-xl text-slate-500">Upload Page Coming Soon</div>;
const Results = () => <div className="p-8 text-center text-xl text-slate-500">Results Page Coming Soon</div>;
const QuestionEngine = () => <div className="p-8 text-center text-xl text-slate-500">Question Engine Coming Soon</div>;
const ExportReport = () => <div className="p-8 text-center text-xl text-slate-500">Export Page Coming Soon</div>;

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

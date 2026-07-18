import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import LiveDashboard from './components/LiveDashboard';
import AnalyticsView from './components/AnalyticsView';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* The Layout acts as the shell (Sidebar/Navbar) */}
        <Route path="/" element={<Layout />}>
          {/* Default page is the Live Dashboard */}
          <Route index element={<LiveDashboard />} />
          {/* Analytics page */}
          <Route path="analytics" element={<AnalyticsView />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;

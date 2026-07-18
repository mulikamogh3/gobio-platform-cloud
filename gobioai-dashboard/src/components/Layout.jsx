import { Outlet, Link, useLocation } from 'react-router-dom';
import { Activity, BarChart2, Droplet } from 'lucide-react';

export default function Layout() {
  const location = useLocation();

  return (
    <div className="flex h-screen bg-slate-900 text-slate-100 font-sans">
      {/* Sidebar */}
      <div className="w-64 bg-slate-950 border-r border-slate-800 p-4 flex flex-col gap-6">
        <div className="flex items-center gap-3 text-2xl font-bold text-white px-2 mt-4">
          <Droplet className="w-8 h-8 text-blue-500 fill-blue-500" />
          GoBioAI
        </div>
        
        <div className="text-xs font-bold tracking-wider text-slate-500 uppercase px-2 mt-4">Main Menu</div>
        
        <nav className="flex flex-col gap-1">
          <Link 
            to="/" 
            className={`flex items-center gap-3 p-3 rounded-xl transition-all font-medium ${location.pathname === '/' ? 'bg-blue-600/10 text-blue-400' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
          >
            <Activity className="w-5 h-5" />
            Live Dashboard
          </Link>
          <Link 
            to="/analytics" 
            className={`flex items-center gap-3 p-3 rounded-xl transition-all font-medium ${location.pathname === '/analytics' ? 'bg-blue-600/10 text-blue-400' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
          >
            <BarChart2 className="w-5 h-5" />
            Analytics
          </Link>
        </nav>
      </div>
      
      {/* Main Content Area */}
      <div className="flex-1 overflow-auto bg-slate-900 p-8">
        <Outlet />
      </div>
    </div>
  );
}

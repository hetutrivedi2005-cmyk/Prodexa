import React from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('PRODEXA UI ErrorBoundary caught an exception:', error, errorInfo);
    this.setState({ errorInfo });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.reload();
  };

  handleNavigateHome = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.href = '/user/dashboard';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-[60vh] flex items-center justify-center p-6 font-mono text-xs">
          <div className="max-w-lg w-full p-8 rounded-2xl bg-[#0E131B] border border-rose-500/40 text-slate-100 shadow-[0_0_50px_rgba(244,63,94,0.15)] space-y-5 text-center">
            <div className="w-12 h-12 rounded-2xl bg-rose-500/10 border border-rose-500/40 text-rose-400 mx-auto flex items-center justify-center">
              <AlertTriangle className="w-6 h-6" />
            </div>

            <div className="space-y-1.5">
              <h2 className="text-base font-bold text-rose-300 font-display">
                Workspace Component Render Warning
              </h2>
              <p className="text-[#94A3B8] text-[11px] leading-relaxed">
                An unexpected state initialization occurred while mounting this view.
              </p>
            </div>

            {this.state.error && (
              <div className="p-3 rounded-xl bg-[#070A0F] border border-[#202B3B] text-left text-[10px] text-rose-400 max-h-32 overflow-y-auto font-mono">
                {this.state.error.toString()}
              </div>
            )}

            <div className="flex items-center justify-center gap-3 pt-2">
              <button
                onClick={this.handleNavigateHome}
                className="px-4 py-2.5 rounded-xl bg-[#161F2E] border border-[#202B3B] hover:border-cyan-400 text-cyan-300 font-bold flex items-center gap-2 cursor-pointer transition-all"
              >
                <Home className="w-3.5 h-3.5" />
                <span>Return to Overview</span>
              </button>

              <button
                onClick={this.handleReset}
                className="px-4 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-bold flex items-center gap-2 cursor-pointer transition-all shadow-md"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Reload View</span>
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

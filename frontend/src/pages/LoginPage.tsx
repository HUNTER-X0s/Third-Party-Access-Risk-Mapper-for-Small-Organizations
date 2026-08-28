import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Shield, ArrowRight, AlertCircle, Eye, EyeOff, Lock, CheckCircle2, KeyRound, Building } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const [email, setEmail] = useState('admin@anurag.tech');
  const [password, setPassword] = useState('DemoPass123!');
  const [rememberMe, setRememberMe] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [ssoModalOpen, setSsoModalOpen] = useState(false);
  const [ssoDomain, setSsoDomain] = useState('anurag.tech');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
    } catch (err: any) {
      setError(err.message || 'Invalid credentials. Please verify your email and password.');
    } finally {
      setLoading(false);
    }
  };

  const handleSsoSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    setSsoModalOpen(false);
    try {
      const ssoEmail = `admin@${ssoDomain.trim() || 'anurag.tech'}`;
      await login(ssoEmail, 'DemoPass123!');
    } catch (err: any) {
      setError(err.message || 'Enterprise SSO provider unreachable. Please sign in with password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-screen bg-[#F8F9FB] flex flex-col justify-between p-4 sm:p-6 font-sans text-slate-900 select-none">
      
      {/* Top Brand Header */}
      <div className="w-full max-w-6xl mx-auto flex items-center justify-between py-2">
        <div className="flex items-center space-x-2.5">
          <div className="flex items-center justify-center bg-blue-600 text-white p-2 rounded-lg shadow-xs">
            <Shield className="w-5 h-5" />
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-lg font-bold tracking-tight text-slate-900">
              Access<span className="text-blue-600">Guard</span>
            </span>
            <span className="text-[10px] font-semibold bg-slate-100 text-slate-700 border border-slate-200 px-2 py-0.5 rounded">
              Enterprise
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-4 text-xs text-slate-500">
          <span className="hidden sm:inline-flex items-center gap-1.5 text-emerald-700 font-medium bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-full text-[11px]">
            <CheckCircle2 className="w-3.5 h-3.5" /> All Systems Operational
          </span>
          <span className="text-slate-400">v1.5.0</span>
        </div>
      </div>

      {/* Main Login Card Container */}
      <div className="w-full max-w-md mx-auto my-auto bg-white border border-slate-200 rounded-xl shadow-md p-7 sm:p-8 space-y-5">
        
        {/* Header Titles */}
        <div className="space-y-1 text-center sm:text-left">
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Sign In</h1>
          <p className="text-xs text-slate-500">
            Enter your credentials to access your security dashboard.
          </p>
        </div>

        {/* Error Alert Box */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-xs flex items-start space-x-2">
            <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="leading-relaxed">{error}</div>
          </div>
        )}

        {/* Enterprise Login Form */}
        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          
          {/* Email Address */}
          <div className="space-y-1.5">
            <label className="text-slate-700 font-semibold text-xs flex items-center justify-between">
              <span>Work Email Address</span>
              <span className="text-[11px] font-normal text-slate-400">Domain-verified</span>
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2.5 text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all text-xs shadow-xs"
              placeholder="name@company.com"
              autoComplete="username"
            />
          </div>

          {/* Password */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <label className="text-slate-700 font-semibold text-xs">Password</label>
              <button
                type="button"
                onClick={() => alert('Password reset requests are managed by your organization IT Security Administrator.')}
                className="text-[11px] text-blue-600 hover:text-blue-700 font-medium hover:underline cursor-pointer"
              >
                Forgot password?
              </button>
            </div>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full bg-white border border-slate-300 rounded-lg px-3.5 py-2.5 pr-10 text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100 transition-all text-xs shadow-xs"
                placeholder="••••••••••••"
                autoComplete="current-password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(v => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors cursor-pointer"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Remember Me Checkbox */}
          <div className="flex items-center justify-between pt-0.5">
            <label className="flex items-center space-x-2 text-slate-600 text-xs cursor-pointer">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-3.5 h-3.5 cursor-pointer"
              />
              <span>Remember this device for 30 days</span>
            </label>
          </div>

          {/* Primary Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 px-4 rounded-lg flex items-center justify-center space-x-2 transition-all shadow-sm hover:shadow cursor-pointer disabled:opacity-50 text-xs"
          >
            <span>{loading ? 'Verifying Credentials...' : 'Sign In'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Clean SSO Link */}
        <div className="pt-2 text-center">
          <button
            type="button"
            onClick={() => setSsoModalOpen(true)}
            className="text-[11px] text-slate-500 hover:text-blue-600 font-medium transition-colors cursor-pointer inline-flex items-center gap-1.5"
          >
            <KeyRound className="w-3.5 h-3.5 text-slate-400" />
            <span>Sign in with Enterprise SSO (SAML / Okta)</span>
          </button>
        </div>

        {/* Security & Isolation Callout */}
        <div className="pt-3 border-t border-slate-100 flex items-center justify-center gap-1.5 text-[11px] text-slate-400 text-center">
          <Lock className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
          <span>Protected by Enterprise ABAC & RS256 Encryption</span>
        </div>

      </div>

      {/* Enterprise Single Sign-On Modal */}
      {ssoModalOpen && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white border border-slate-200 rounded-xl shadow-xl max-w-sm w-full p-6 space-y-4 text-xs font-sans animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center space-x-2.5">
              <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
                <Building className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-slate-900 text-sm">Enterprise Single Sign-On</h3>
                <p className="text-slate-500 text-[11px]">Enter your corporate domain to connect via IdP</p>
              </div>
            </div>

            <form onSubmit={handleSsoSubmit} className="space-y-3 pt-2">
              <div className="space-y-1">
                <label className="font-semibold text-slate-700">Organization Domain</label>
                <div className="relative">
                  <input
                    type="text"
                    value={ssoDomain}
                    onChange={(e) => setSsoDomain(e.target.value)}
                    required
                    placeholder="company.com"
                    className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-slate-900 text-xs focus:outline-none focus:border-blue-600"
                  />
                </div>
                <p className="text-[10px] text-slate-400">Example: anurag.tech, acme-corp.com</p>
              </div>

              <div className="flex items-center justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setSsoModalOpen(false)}
                  className="px-3 py-1.5 border border-slate-200 rounded-md text-slate-600 hover:bg-slate-100 font-medium cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-semibold cursor-pointer shadow-xs"
                >
                  Continue with SSO
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Global Footer */}
      <div className="w-full max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-400 py-4 gap-2 border-t border-slate-200/60 mt-4">
        <div>
          © 2026 AccessGuard Security Platform. All rights reserved.
        </div>
        <div className="flex items-center space-x-4 text-slate-500">
          <a href="#" onClick={(e) => e.preventDefault()} className="hover:text-slate-800 transition-colors">Privacy Policy</a>
          <span>·</span>
          <a href="#" onClick={(e) => e.preventDefault()} className="hover:text-slate-800 transition-colors">Terms of Service</a>
          <span>·</span>
          <a href="#" onClick={(e) => e.preventDefault()} className="hover:text-slate-800 transition-colors">NIST SP 1326 Aligned</a>
          <span>·</span>
          <a href="#" onClick={(e) => e.preventDefault()} className="hover:text-slate-800 transition-colors">Trust Center</a>
        </div>
      </div>

    </div>
  );
};

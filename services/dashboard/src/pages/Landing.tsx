import { Link } from 'react-router-dom';
import { Camera, Activity, Map, ArrowRight, ShieldCheck, Zap, Database, Cpu, Network, Server } from 'lucide-react';
import { useEffect, useState } from 'react';

export default function Landing() {
  return (
    <div className="min-h-screen bg-black text-white overflow-hidden relative font-sans">
      
      {/* Dynamic Grid Background */}
      <div className="absolute inset-0 bg-grid-pattern pointer-events-none z-0 opacity-50" />
      
      {/* Background ambient glows */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-blue-600/20 rounded-full blur-[120px] pointer-events-none blob-animation" />
      <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-blue-700/20 rounded-full blur-[150px] pointer-events-none blob-animation" style={{ animationDelay: '-10s' }} />

      {/* Navigation */}
      <nav className="glass-medium fixed top-0 w-full z-50 border-b border-white/10 px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Camera className="text-blue-500 w-6 h-6" />
            <span className="font-bold text-xl tracking-tight">Store<span className="text-blue-500">Intelligence</span></span>
          </div>
          <div className="flex gap-4">
            <Link to="/login" className="px-5 py-2 rounded-lg text-sm font-medium hover:bg-white/5 transition-colors border border-transparent hover:border-white/10">
              Sign In
            </Link>
            <Link to="/dashboard" className="px-5 py-2 rounded-lg text-sm font-bold bg-blue-600 hover:bg-blue-500 text-white transition-colors flex items-center gap-2 btn-shimmer shadow-[0_0_15px_rgba(37,99,235,0.5)]">
              Launch Platform
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="pt-32 pb-20 px-6 relative z-10 flex items-center min-h-[85vh]">
        <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-16 items-center w-full">
          
          {/* Left: Text Content */}
          <div className="text-left mt-10 lg:mt-0 order-2 lg:order-1">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass-light border border-blue-500/30 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-8 animate-fade-in-up">
              <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
              Live Edge Processing Online
            </div>
            
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-extrabold tracking-tight mb-8 animate-fade-in-up stagger-1 leading-[1.1]">
              Transform CCTV into <br className="hidden md:block" />
              <span className="gradient-text-primary">Actionable Retail Metrics</span>
            </h1>
            
            <p className="text-lg md:text-xl font-light text-slate-300 max-w-xl mb-10 animate-fade-in-up stagger-2 leading-relaxed">
              The world's most advanced computer vision platform for brick-and-mortar retail. Monitor foot traffic, prevent bottlenecks, and optimize store layouts in real-time.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 animate-fade-in-up stagger-3">
              <Link to="/dashboard" className="px-8 py-4 rounded-xl font-bold bg-blue-600 text-white hover:bg-blue-500 transition-all flex items-center justify-center gap-2 text-lg shadow-[0_0_30px_rgba(37,99,235,0.3)] hover:shadow-[0_0_40px_rgba(37,99,235,0.5)] hover:scale-105">
                Enter Dashboard <ArrowRight className="w-5 h-5" />
              </Link>
              <a href="#features" className="px-8 py-4 rounded-xl font-semibold glass-medium hover:glass-strong transition-all flex items-center justify-center text-lg shadow-xl">
                Explore Capabilities
              </a>
            </div>
          </div>

          {/* Right: Image Visual */}
          <div className="relative w-full flex justify-end items-center order-1 lg:order-2 group mt-4 lg:-mt-8 lg:translate-x-8 lg:-translate-y-6">
            {/* Massive Ambient Back Glow */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[120%] h-[120%] bg-blue-500/20 blur-[120px] rounded-full mix-blend-screen pointer-events-none animate-pulse-glow"></div>
            
            {/* Glassmorphic Pedestal/Container */}
            <div className="relative w-full max-w-[550px] aspect-square rounded-3xl border border-white/10 bg-gradient-to-br from-blue-900/20 via-black/40 to-blue-600/10 backdrop-blur-xl shadow-[0_0_50px_rgba(37,99,235,0.2)] overflow-hidden flex justify-center items-center group-hover:border-blue-500/30 transition-all duration-700">
              
              {/* Inner animated grid/accents */}
              <div className="absolute inset-0 bg-grid-pattern opacity-20" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />
              
              {/* Corner Accents */}
              <div className="absolute top-0 left-0 w-16 h-16 border-t-2 border-l-2 border-blue-500/40 rounded-tl-3xl z-30"></div>
              <div className="absolute bottom-0 right-0 w-16 h-16 border-b-2 border-r-2 border-blue-500/40 rounded-br-3xl z-30"></div>

              {/* The Robot UI Image Wrapper */}
              <div className="relative z-20 w-[120%] h-[120%] animate-[float_6s_ease-in-out_infinite] group-hover:scale-[1.03] transition-transform duration-700 flex items-center justify-center">
                
                {/* The Base Image */}
                <img 
                  src="/robot-ui.png" 
                  alt="Store Intelligence Robot UI" 
                  className="w-full h-full object-cover"
                />

                {/* The Radial Blur Overlay (blurs edges, keeps center sharp) */}
                <div 
                  className="absolute inset-0 backdrop-blur-xl pointer-events-none"
                  style={{
                    maskImage: 'radial-gradient(circle at center, transparent 35%, black 75%)',
                    WebkitMaskImage: 'radial-gradient(circle at center, transparent 35%, black 75%)'
                  }}
                />
              </div>

              {/* Dynamic decorative elements around container */}
              <div className="absolute -right-4 top-1/4 w-8 h-8 rounded-full bg-blue-500/20 blur-md animate-pulse z-30"></div>
              <div className="absolute -left-4 bottom-1/4 w-12 h-12 rounded-full bg-blue-400/10 blur-xl animate-pulse z-30" style={{ animationDelay: '1s' }}></div>
            </div>
          </div>

        </div>
      </main>

      {/* Feature Grid */}
      <section id="features" className="py-20 px-6 relative z-10">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20 relative">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-24 h-1 bg-gradient-to-r from-transparent via-blue-500 to-transparent mb-8"></div>
            <h2 className="text-5xl md:text-6xl font-extrabold mb-6 tracking-tight pt-8 bg-clip-text text-transparent bg-gradient-to-b from-white via-blue-100 to-blue-500 drop-shadow-sm">
              Designed for scale. <br className="md:hidden" /> Built for accuracy.
            </h2>
            <p className="text-xl md:text-2xl font-light text-blue-200/80 max-w-3xl mx-auto leading-relaxed">
              A complete end-to-end intelligence suite that replaces fragmented analytics with a single source of truth.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            
            {/* Card 1 */}
            <div className="glass-strong p-10 rounded-3xl hover:-translate-y-4 transition-all duration-500 border-t border-white/10 shadow-[0_20px_40px_-15px_rgba(37,99,235,0.15)] group">
              <div className="w-14 h-14 rounded-2xl bg-blue-600/20 flex items-center justify-center mb-6 border border-blue-500/30 group-hover:scale-110 transition-transform duration-500 group-hover:bg-blue-600/30">
                <Zap className="text-blue-500 w-7 h-7" />
              </div>
              <h3 className="text-2xl font-bold mb-4">Real-Time Telemetry</h3>
              <p className="text-lg text-slate-400 leading-relaxed">
                Sub-millisecond WebSocket data streams. Monitor queue lengths and store occupancy exactly as it happens, with zero perceived latency.
              </p>
            </div>

            {/* Card 2 */}
            <div className="glass-strong p-10 rounded-3xl hover:-translate-y-4 transition-all duration-500 border-t border-white/10 shadow-[0_20px_40px_-15px_rgba(37,99,235,0.15)] group">
              <div className="w-14 h-14 rounded-2xl bg-blue-600/20 flex items-center justify-center mb-6 border border-blue-500/30 group-hover:scale-110 transition-transform duration-500 group-hover:bg-blue-600/30">
                <Activity className="text-blue-500 w-7 h-7" />
              </div>
              <h3 className="text-2xl font-bold mb-4">Conversion Intelligence</h3>
              <p className="text-lg text-slate-400 leading-relaxed">
                Track visitors from entry to checkout. Build powerful conversion funnels while automatically excluding staff and security from analytics.
              </p>
            </div>

            {/* Card 3 */}
            <div className="glass-strong p-10 rounded-3xl hover:-translate-y-4 transition-all duration-500 border-t border-white/10 shadow-[0_20px_40px_-15px_rgba(37,99,235,0.15)] group">
              <div className="w-14 h-14 rounded-2xl bg-blue-600/20 flex items-center justify-center mb-6 border border-blue-500/30 group-hover:scale-110 transition-transform duration-500 group-hover:bg-blue-600/30">
                <Map className="text-blue-500 w-7 h-7" />
              </div>
              <h3 className="text-2xl font-bold mb-4">Fleet Management</h3>
              <p className="text-lg text-slate-400 leading-relaxed">
                Monitor thousands of stores simultaneously. View aggregated health metrics and resolve active anomalies across your entire enterprise footprint.
              </p>
            </div>

            {/* Card 4 */}
            <div className="glass-strong p-10 rounded-3xl hover:-translate-y-4 transition-all duration-500 border-t border-white/10 shadow-[0_20px_40px_-15px_rgba(37,99,235,0.15)] group">
              <div className="w-14 h-14 rounded-2xl bg-blue-600/20 flex items-center justify-center mb-6 border border-blue-500/30 group-hover:scale-110 transition-transform duration-500 group-hover:bg-blue-600/30">
                <Server className="text-blue-500 w-7 h-7" />
              </div>
              <h3 className="text-2xl font-bold mb-4">Enterprise Architecture</h3>
              <p className="text-lg text-slate-400 leading-relaxed">
                Engineered for maximum fault tolerance. Powered by Kafka event streams, Redis caching, TimescaleDB, and an asynchronous FastAPI backend.
              </p>
            </div>

          </div>
        </div>
      </section>

      {/* Architecture Showcase */}
      <section id="architecture" className="py-24 px-6 relative z-10 overflow-hidden mt-10">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-28 relative">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-24 h-1 bg-gradient-to-r from-transparent via-blue-500 to-transparent mb-8"></div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full glass-light border border-blue-500/30 text-blue-400 text-xs font-semibold uppercase tracking-widest mb-6 shadow-[0_0_15px_rgba(37,99,235,0.2)] mt-8">
              Architecture
            </div>
            <h2 className="text-5xl md:text-6xl font-extrabold mb-6 tracking-tight bg-clip-text text-transparent bg-gradient-to-b from-white via-blue-100 to-blue-500 drop-shadow-sm">
              The Intelligence Pipeline
            </h2>
            <p className="text-xl md:text-2xl font-light text-blue-200/80 max-w-3xl mx-auto leading-relaxed">
              From raw pixels to actionable business metrics in <span className="font-semibold text-blue-400">under 50 milliseconds</span>.
            </p>
          </div>

          {/* Pipeline Visual */}
          <div className="relative flex flex-col md:flex-row items-center justify-between max-w-6xl mx-auto gap-8 md:gap-0 mt-16 group">
            {/* Animated Connection Lines */}
            <div className="hidden md:block absolute top-1/2 left-[5%] right-[5%] h-[2px] bg-white/10 -translate-y-1/2 z-0 overflow-hidden">
              <div className="absolute top-0 left-0 h-full w-[30%] bg-gradient-to-r from-transparent via-blue-400 to-transparent animate-[data-stream_2.5s_linear_infinite] shadow-[0_0_10px_rgba(96,165,250,0.8)]"></div>
              <div className="absolute top-0 left-0 h-full w-[15%] bg-gradient-to-r from-transparent via-blue-300 to-transparent animate-[data-stream_1.5s_linear_infinite_0.5s] shadow-[0_0_15px_rgba(147,197,253,1)]"></div>
            </div>

            {/* Vertical Lines for Mobile */}
            <div className="md:hidden absolute top-[5%] bottom-[5%] left-1/2 w-[2px] bg-white/10 -translate-x-1/2 z-0 overflow-hidden">
               <div className="absolute top-0 left-0 w-full h-[30%] bg-gradient-to-b from-transparent via-blue-400 to-transparent animate-[float_2.5s_linear_infinite]"></div>
            </div>

            {/* Nodes */}
            <div className="z-10 flex flex-col items-center gap-4 glass-strong p-6 rounded-2xl border border-white/10 hover:border-blue-500/50 w-full md:w-auto shadow-xl hover:shadow-[0_0_30px_rgba(37,99,235,0.3)] transition-all duration-300 bg-[#0A0A0F] hover:-translate-y-2">
              <div className="w-16 h-16 rounded-xl bg-blue-600/10 flex items-center justify-center border border-blue-500/20 mb-2">
                <Camera className="w-8 h-8 text-blue-400" />
              </div>
              <div className="font-bold text-center text-white text-lg">CCTV Edge</div>
              <div className="text-xs text-blue-300 font-mono bg-blue-500/10 px-3 py-1 rounded-full border border-blue-500/20">YOLO11 • ByteTrack</div>
            </div>

            <div className="hidden md:block w-8"></div>

            <div className="z-10 flex flex-col items-center gap-4 glass-strong p-6 rounded-2xl border border-blue-500/30 hover:border-blue-400 w-full md:w-auto shadow-[0_0_30px_rgba(37,99,235,0.15)] hover:shadow-[0_0_40px_rgba(37,99,235,0.4)] transition-all duration-300 bg-[#0A0A0F] hover:-translate-y-2 relative group/node">
              <div className="absolute inset-0 rounded-2xl border border-blue-500 opacity-50 animate-pulse pointer-events-none"></div>
              <div className="w-16 h-16 rounded-xl bg-blue-600/20 flex items-center justify-center border border-blue-500/40 mb-2 group-hover/node:scale-110 transition-transform">
                <Network className="w-8 h-8 text-blue-500" />
              </div>
              <div className="font-bold text-center text-white text-lg">Event Stream</div>
              <div className="text-xs text-blue-300 font-mono bg-blue-500/10 px-3 py-1 rounded-full border border-blue-500/20">Apache Kafka</div>
            </div>

            <div className="hidden md:block w-8"></div>

            <div className="z-10 flex flex-col items-center gap-4 glass-strong p-6 rounded-2xl border border-blue-500/30 hover:border-blue-400 w-full md:w-auto shadow-[0_0_30px_rgba(37,99,235,0.15)] hover:shadow-[0_0_40px_rgba(37,99,235,0.4)] transition-all duration-300 bg-[#0A0A0F] hover:-translate-y-2 relative group/node">
              <div className="w-16 h-16 rounded-xl bg-blue-600/20 flex items-center justify-center border border-blue-500/40 mb-2 group-hover/node:rotate-12 transition-transform">
                <Cpu className="w-8 h-8 text-blue-500" />
              </div>
              <div className="font-bold text-center text-white text-lg">Processing</div>
              <div className="text-xs text-blue-300 font-mono bg-blue-500/10 px-3 py-1 rounded-full border border-blue-500/20">FastAPI • Redis</div>
            </div>

            <div className="hidden md:block w-8"></div>

            <div className="z-10 flex flex-col items-center gap-4 glass-strong p-6 rounded-2xl border border-white/10 hover:border-blue-500/50 w-full md:w-auto shadow-xl hover:shadow-[0_0_30px_rgba(37,99,235,0.3)] transition-all duration-300 bg-[#0A0A0F] hover:-translate-y-2">
              <div className="w-16 h-16 rounded-xl bg-blue-600/10 flex items-center justify-center border border-blue-500/20 mb-2">
                <Database className="w-8 h-8 text-blue-400" />
              </div>
              <div className="font-bold text-center text-white text-lg">Storage</div>
              <div className="text-xs text-blue-300 font-mono bg-blue-500/10 px-3 py-1 rounded-full border border-blue-500/20">TimescaleDB</div>
            </div>
          </div>
        </div>
      </section>

      {/* Bottom CTA */}
      <div className="max-w-4xl mx-auto mt-20 mb-32 text-center p-16 rounded-3xl border border-white/10 bg-gradient-to-b from-slate-900 to-black relative z-10 shadow-2xl">
        <ShieldCheck className="w-12 h-12 text-blue-500 mx-auto mb-6" />
        <h2 className="text-4xl font-bold mb-4">Enterprise Grade Intelligence</h2>
        <p className="text-xl text-slate-400 mb-10 max-w-2xl mx-auto leading-relaxed">
          Deployed on edge devices to preserve customer privacy. Built with robust TimescaleDB and Kafka integrations.
        </p>
        <Link to="/dashboard" className="px-10 py-4 rounded-xl font-bold bg-blue-600 hover:bg-blue-500 text-white transition-all shadow-[0_0_20px_rgba(37,99,235,0.3)] hover:shadow-[0_0_30px_rgba(37,99,235,0.5)] inline-block text-lg">
          Experience the Demo
        </Link>
      </div>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8 text-center text-slate-500 text-sm mt-12 glass-light relative z-10">
        <p>© 2026 Store Intelligence Platform. Submitted for Purplle Tech Challenge.</p>
      </footer>
    </div>
  );
}

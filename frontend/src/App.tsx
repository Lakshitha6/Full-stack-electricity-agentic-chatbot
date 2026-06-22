import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { Zap, MessageSquare, Shield, Clock, BarChart3, Lightbulb, ArrowRight, Mail, Phone, MapPin, Bot, HelpCircle, Users, Target, Heart } from 'lucide-react';

import { MainLayout } from '@/components/layout/MainLayout';
import { ProtectedRoute } from '@/components/layout/ProtectedRoute';
import { useAuthStore, initAuth } from '@/store/authStore';
import LoginPage from '@/pages/Login';
import SignupPage from '@/pages/Signup';
import ProfilePage from '@/pages/Profile';
import { ToastContainer } from '@/components/ui/Toast';


// Initialize auth from localStorage on app load
initAuth();

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
});


const Home = () => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  return (
    <div className="w-full max-w-7xl mx-auto px-4 sm:px-8">
      {/* ─── Hero Section ─── */}
      <section className="relative py-16 sm:py-24 text-center overflow-hidden">
        {/* Background glow blobs */}
        <div className="absolute inset-0 -z-10 overflow-hidden pointer-events-none" aria-hidden="true">
          <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl animate-float" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/8 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }} />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-pink-500/6 rounded-full blur-3xl animate-float" style={{ animationDelay: '4s' }} />
        </div>

        {/* Floating icon */}
        <div className="animate-fade-in-up flex justify-center mb-8">
          <div className="relative">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/25 animate-float">
              <Zap className="w-10 h-10 text-white" />
            </div>
            <div className="absolute -inset-1 rounded-2xl bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-600 opacity-20 blur-lg -z-10" />
          </div>
        </div>

        <h1 className="animate-fade-in-up stagger-1 text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight leading-tight mb-6">
          Your electricity bills,{' '}
          <span className="text-gradient">decoded instantly</span>
        </h1>

        <p className="animate-fade-in-up stagger-2 text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed">
          An AI-powered assistant that understands your electricity account. Ask questions in plain English and get clear, accurate answers in seconds.
        </p>

        {/* CTA area */}
        <div className="animate-fade-in-up stagger-3 flex flex-col sm:flex-row items-center justify-center gap-4 mb-6">
          {isAuthenticated ? (
            <div className="inline-flex items-center gap-2 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 px-6 py-3 rounded-full text-sm font-medium">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              You're logged in - click the chat icon to start!
            </div>
          ) : (
            <>
              <a href="/signup" className="group inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white px-8 py-3.5 rounded-xl text-sm font-semibold shadow-lg shadow-blue-500/25 transition-all duration-300 hover:shadow-xl hover:shadow-blue-500/30 hover:-translate-y-0.5">
                Get Started Free
                <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
              </a>
              <a href="/login" className="inline-flex items-center gap-2 border border-border hover:border-foreground/20 hover:bg-muted/50 px-8 py-3.5 rounded-xl text-sm font-semibold transition-all duration-300">
                Sign In
              </a>
            </>
          )}
        </div>
      </section>

      {/* ─── Feature Cards ─── */}
      <section className="py-12 sm:py-16">
        <div className="text-center mb-12">
          <p className="text-xs font-semibold uppercase tracking-widest text-blue-600 dark:text-blue-400 mb-3">Why choose us</p>
          <h2 className="text-2xl sm:text-3xl font-bold">Everything you need, in one place</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {[
            { icon: MessageSquare, title: 'Natural Conversations', desc: 'Ask about your bills in plain English. No jargon, no complicated menus.', color: 'from-blue-500 to-cyan-400' },
            { icon: Shield, title: 'Secure & Private', desc: 'Your account data is accessed through encrypted APIs with JWT authentication.', color: 'from-indigo-500 to-purple-500' },
            { icon: Clock, title: '24/7 Availability', desc: 'Get answers anytime, day or night. No waiting on hold or business hours.', color: 'from-purple-500 to-pink-500' },
            { icon: BarChart3, title: 'Usage Analytics', desc: 'Understand your consumption patterns and find ways to reduce your bills.', color: 'from-amber-500 to-orange-500' },
            { icon: Lightbulb, title: 'Smart Insights', desc: 'AI-generated tips based on your actual usage data to help you save money.', color: 'from-emerald-500 to-teal-500' },
            { icon: Zap, title: 'Instant Answers', desc: 'Powered by Gemini & Groq for lightning-fast, accurate responses.', color: 'from-rose-500 to-red-500' },
          ].map((f, i) => (
            <div key={f.title} className={`animate-fade-in-up stagger-${i + 1} group relative border border-border rounded-2xl p-6 bg-card hover:shadow-xl hover:shadow-black/5 dark:hover:shadow-black/20 transition-all duration-500 hover:-translate-y-1`}>
              <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${f.color} flex items-center justify-center mb-4 shadow-lg shadow-black/10 transition-transform duration-500 group-hover:scale-110`}>
                <f.icon className="w-5 h-5 text-white" />
              </div>
              <h3 className="text-base font-semibold mb-2">{f.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ─── Stats Bar ─── */}
      <section className="py-10 sm:py-14">
        <div className="rounded-2xl border border-border bg-gradient-to-r from-muted/50 via-muted/30 to-muted/50 p-8 sm:p-10">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 text-center">
            {[
              { value: '1k+', label: 'Active Users' },
              { value: '99.9%', label: 'Uptime' },
              { value: '<10s', label: 'Response Time' },
              { value: '24/7', label: 'Availability' },
            ].map((s) => (
              <div key={s.label}>
                <div className="text-3xl sm:text-4xl font-extrabold text-gradient mb-1">{s.value}</div>
                <div className="text-sm text-muted-foreground font-medium">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── Bottom CTA ─── */}
      <section className="py-12 sm:py-16 text-center">
        <div className="relative rounded-2xl overflow-hidden p-10 sm:p-14">
          {/* Gradient background */}
          <div className="absolute inset-0 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 opacity-[0.06] dark:opacity-[0.12]" />
          <div className="absolute inset-0 border border-blue-500/10 rounded-2xl" />
          <div className="relative">
            <h2 className="text-2xl sm:text-3xl font-bold mb-4">Ready to simplify your electricity bills?</h2>
            <p className="text-muted-foreground max-w-lg mx-auto mb-8">Join thousands of users who get instant, clear answers about their electricity accounts.</p>
            {!isAuthenticated && (
              <a href="/signup" className="group inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white px-8 py-3.5 rounded-xl text-sm font-semibold shadow-lg shadow-blue-500/25 transition-all duration-300 hover:shadow-xl hover:shadow-blue-500/30 hover:-translate-y-0.5">
                Create Your Free Account
                <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
              </a>
            )}
          </div>
        </div>
      </section>
    </div>
  );
};



/* ------------------------------------------------  About --------------------------------------------------------------------*/

const About = () => (
  <div className="w-full max-w-7xl mx-auto px-4 sm:px-8 py-8 sm:py-12">
    {/* ─── Hero Section ─── */}
    <section className="relative text-center py-12 sm:py-16 mb-16 overflow-hidden">
      <div className="absolute inset-0 -z-10 pointer-events-none" aria-hidden="true">
        <div className="absolute top-0 left-1/3 w-80 h-80 bg-indigo-500/8 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-64 h-64 bg-blue-500/6 rounded-full blur-3xl" />
      </div>
      <div className="animate-fade-in-up">
        <p className="text-xs font-semibold uppercase tracking-widest text-blue-600 dark:text-blue-400 mb-4">About us</p>
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold leading-tight mb-6 max-w-3xl mx-auto">
          Built to make electricity billing{' '}
          <span className="text-gradient">less confusing</span> for everyone
        </h1>
        <p className="text-muted-foreground leading-relaxed text-base sm:text-lg max-w-2xl mx-auto">
          The Electricity Board AI Assistant was built because billing statements are
          often dense and hard to interpret. We wanted consumers to get clear, instant
          answers - without calling a hotline.
        </p>
      </div>
    </section>

    {/* ─── Values / Mission Cards ─── */}
    <section className="mb-16">
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        {[
          { icon: Users, title: 'User-First', desc: 'Every feature is designed with the consumer in mind - simple, clear, and accessible.', color: 'from-blue-500 to-cyan-400' },
          { icon: Target, title: 'Accuracy', desc: 'Responses are grounded in your real account data. No hallucinations, no guesses.', color: 'from-indigo-500 to-purple-500' },
          { icon: Heart, title: 'Transparency', desc: 'Open about how we use your data and how our AI generates responses.', color: 'from-rose-500 to-pink-500' },
        ].map((v, i) => (
          <div key={v.title} className={`animate-fade-in-up stagger-${i + 1} group border border-border rounded-2xl p-6 bg-card hover:shadow-xl hover:shadow-black/5 dark:hover:shadow-black/20 transition-all duration-500 hover:-translate-y-1 text-center`}>
            <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${v.color} flex items-center justify-center mx-auto mb-4 shadow-lg shadow-black/10 transition-transform duration-500 group-hover:scale-110`}>
              <v.icon className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-base font-semibold mb-2">{v.title}</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">{v.desc}</p>
          </div>
        ))}
      </div>
    </section>

    {/* ─── How It Works ─── */}
    <section className="mb-16">
      <div className="flex flex-col lg:flex-row lg:gap-16">
        <div className="flex-1 mb-10 lg:mb-0">
          <p className="text-xs font-semibold uppercase tracking-widest text-blue-600 dark:text-blue-400 mb-3">How it works</p>
          <h2 className="text-2xl sm:text-3xl font-bold mb-4">Powered by AI, grounded in your data</h2>
          <p className="text-muted-foreground leading-relaxed mb-8">
            When you ask a question, the agent retrieves your account data -
            units consumed, payment history, due amounts - and generates a clear,
            human-readable response. No hallucinations, no guesses.
          </p>
          <div className="flex flex-wrap gap-2">
            {["FastAPI", "React", "Gemini + Groq", "Secure account API", "JWT auth", "Real-time data"].map((t) => (
              <span key={t} className="text-xs bg-gradient-to-r from-blue-500/10 to-indigo-500/10 text-blue-700 dark:text-blue-300 px-4 py-2 rounded-full border border-blue-500/20 font-medium">{t}</span>
            ))}
          </div>
        </div>
        {/* Steps */}
        <div className="flex-shrink-0 lg:w-80 flex flex-col gap-4">
          {[
            { step: "1", title: "You ask", desc: "Type your question in plain English." },
            { step: "2", title: "We fetch", desc: "Your account data is retrieved securely." },
            { step: "3", title: "You get an answer", desc: "A clear, accurate response in seconds." },
          ].map((s, i) => (
            <div key={s.step} className={`animate-fade-in-up stagger-${i + 1} group flex gap-4 items-start border border-border rounded-2xl p-5 bg-card hover:shadow-lg hover:shadow-black/5 dark:hover:shadow-black/15 transition-all duration-400 hover:-translate-y-0.5`}>
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 text-white text-sm font-bold flex items-center justify-center flex-shrink-0 shadow-md shadow-blue-500/20">{s.step}</div>
              <div>
                <div className="text-sm font-semibold mb-1">{s.title}</div>
                <div className="text-xs text-muted-foreground leading-relaxed">{s.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>

    {/* ─── Mission Statement ─── */}
    <section className="text-center py-10 sm:py-14">
      <div className="relative rounded-2xl overflow-hidden p-10 sm:p-14">
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-600 via-blue-600 to-cyan-500 opacity-[0.06] dark:opacity-[0.12]" />
        <div className="absolute inset-0 border border-indigo-500/10 rounded-2xl" />
        <div className="relative">
          <p className="text-lg sm:text-xl font-semibold mb-2">Our Mission</p>
          <p className="text-muted-foreground max-w-xl mx-auto leading-relaxed">
            To provide better, faster, and modern service to electricity consumers - making every interaction effortless and transparent.
          </p>
        </div>
      </div>
    </section>
  </div>
);


/* ------------------------------------------------------  Contact  ---------------------------------------------------------------*/

const Contact = () => (
  <div className="w-full max-w-7xl mx-auto px-4 sm:px-8 py-8 sm:py-12">
    {/* ─── Hero Header ─── */}
    <section className="relative text-center py-10 sm:py-14 mb-14 overflow-hidden">
      <div className="absolute inset-0 -z-10 pointer-events-none" aria-hidden="true">
        <div className="absolute top-0 right-1/4 w-72 h-72 bg-emerald-500/8 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-1/3 w-60 h-60 bg-blue-500/6 rounded-full blur-3xl" />
      </div>
      <div className="animate-fade-in-up">
        <p className="text-xs font-semibold uppercase tracking-widest text-emerald-600 dark:text-emerald-400 mb-4">Contact us</p>
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold leading-tight mb-5">
          We're here to <span className="text-gradient">help</span>
        </h1>
        <p className="text-muted-foreground leading-relaxed text-base sm:text-lg max-w-2xl mx-auto">
          For billing disputes, technical issues, or general enquiries - reach us
          through any of the channels below. For instant answers, use the AI chat assistant.
        </p>
      </div>
    </section>

    {/* ─── Contact Cards + Support Hours ─── */}
    <section className="flex flex-col lg:flex-row lg:gap-8 mb-16">
      {/* Contact channel cards */}
      <div className="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8 lg:mb-0">
        {[
          { icon: Mail, title: 'Email support', detail: 'support@billbot.abcd', sub: 'We respond within 24 hours', color: 'from-blue-500 to-cyan-400' },
          { icon: Phone, title: 'Phone helpline', detail: '1800-000-1234', sub: 'Mon–Fri, 9 am – 5 pm', color: 'from-emerald-500 to-teal-500' },
          { icon: MapPin, title: 'Office', detail: 'Electricity Board HQ', sub: '12 Power Street, Colombo 03', color: 'from-purple-500 to-pink-500' },
          { icon: Bot, title: 'AI chatbot', detail: 'Bills & usage queries', sub: 'Instant answers, 24/7', color: 'from-amber-500 to-orange-500' },
        ].map((c, i) => (
          <div key={c.title} className={`animate-fade-in-up stagger-${i + 1} group border border-border rounded-2xl p-6 bg-card hover:shadow-xl hover:shadow-black/5 dark:hover:shadow-black/20 transition-all duration-500 hover:-translate-y-1`}>
            <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${c.color} flex items-center justify-center mb-4 shadow-lg shadow-black/10 transition-transform duration-500 group-hover:scale-110`}>
              <c.icon className="w-5 h-5 text-white" />
            </div>
            <div className="text-sm font-semibold mb-1">{c.title}</div>
            <div className="text-sm text-foreground/80 font-medium">{c.detail}</div>
            <div className="text-xs text-muted-foreground mt-1.5">{c.sub}</div>
          </div>
        ))}
      </div>

      {/* Support hours — sticky sidebar */}
      <div className="flex-shrink-0 lg:w-72">
        <div className="animate-fade-in-up stagger-3 border border-border rounded-2xl overflow-hidden bg-card">
          <div className="px-5 py-4 bg-gradient-to-r from-blue-500/10 to-indigo-500/10 border-b border-border">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <p className="text-xs font-semibold uppercase tracking-widest text-blue-600 dark:text-blue-400">Support hours</p>
            </div>
          </div>
          <div className="divide-y divide-border">
            {[
              { day: 'Monday – Friday', time: '9:00 am – 4:00 pm' },
              { day: 'Saturday', time: 'Closed' },
              { day: 'Sunday & holidays', time: 'Closed' },
            ].map((r) => (
              <div key={r.day} className="flex justify-between text-sm px-5 py-3.5">
                <span className="text-muted-foreground">{r.day}</span>
                <span className="font-medium">{r.time}</span>
              </div>
            ))}
          </div>
          <div className="px-5 py-4 bg-emerald-500/5 border-t border-border">
            <p className="text-xs text-emerald-600 dark:text-emerald-400 font-medium">💬 AI chatbot available 24/7</p>
          </div>
        </div>
      </div>
    </section>

    {/* ─── FAQ ─── */}
    <section>
      <div className="text-center mb-10">
        <p className="text-xs font-semibold uppercase tracking-widest text-blue-600 dark:text-blue-400 mb-3">Common questions</p>
        <h2 className="text-2xl sm:text-3xl font-bold">Frequently asked questions</h2>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {[
          { q: 'How do I view my bill online?', a: 'Log in and ask the assistant "Show me my latest bill" - it will display your bill summary right in the chat.' },
          { q: 'I was overcharged - what do I do?', a: 'Email us at support@billbot.local with your account number and the bill month. Our billing team responds within one business day.' },
          { q: 'Can the chatbot make payments for me?', a: "Not yet - the assistant is read-only for now. Payment options are available through the Electricity Board's main portal." },
          { q: 'Is this chatbot working anytime?', a: 'Yes! The AI chatbot is available 24 hours a day, 7 days a week. You can ask questions anytime you want.' },
        ].map((f, i) => (
          <div key={f.q} className={`animate-fade-in-up stagger-${i + 1} group border border-border rounded-2xl p-6 bg-card hover:shadow-lg hover:shadow-black/5 dark:hover:shadow-black/15 transition-all duration-400 hover:-translate-y-0.5`}>
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500/10 to-indigo-500/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                <HelpCircle className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <div className="text-sm font-semibold mb-2">{f.q}</div>
                <div className="text-sm text-muted-foreground leading-relaxed">{f.a}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  </div>
);


export default function App() {

  const [isAppReady, setIsAppReady] = useState(false);

  // Initialize auth on app mount
  useEffect(() => {
    initAuth().finally(() => setIsAppReady(true));
  }, []);

  if (!isAppReady) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Home />} />
            <Route path="about" element={<About />} />
            <Route path="contact" element={<Contact />} />
            <Route path="login" element={<LoginPage />} />
            <Route path="signup" element={<SignupPage />} />
            <Route path="profile" element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            } />
          </Route>
          {/* Catch-all redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>

        <ToastContainer />
      </BrowserRouter>
    </QueryClientProvider>
  );
}
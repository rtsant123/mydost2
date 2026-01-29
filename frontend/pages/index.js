import Head from 'next/head';
import Link from 'next/link';
import { Shield, Brain, Sparkles, Activity, BookOpen, Stars } from 'lucide-react';

const features = [
  {
    title: 'Sports Predictions',
    desc: 'Data-aware match insights and win probabilities tailored for cricket & football fans.',
    icon: Activity,
  },
  {
    title: 'Homework Help',
    desc: 'Multi-language tutoring (English, Hinglish, Hindi, Assamese) with concise steps and examples.',
    icon: BookOpen,
  },
  {
    title: 'Horoscope',
    desc: 'Daily/weekly guidance with friendly, actionable advice for every zodiac sign.',
    icon: Stars,
  },
  {
    title: 'Memory Built In',
    desc: 'Secure personal notes and recall across chats—preferences, files, and past questions.',
    icon: Brain,
  },
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-100 via-slate-200 to-slate-50 text-slate-900">
      <Head>
        <title>MyDost AI | Memory-first assistant for sports, study, and guidance</title>
      </Head>

      {/* Navbar */}
      <header className="sticky top-0 z-20 bg-slate-100/60 backdrop-blur border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2 font-semibold text-slate-900">
            <Shield size={20} className="text-slate-700" />
            <span>MyDost AI</span>
          </div>
          <div className="flex items-center gap-3 text-sm font-medium">
            <Link href="/signin" className="px-4 py-2 rounded-lg hover:bg-slate-200 text-slate-800">
              Sign In
            </Link>
            <Link
              href="/signup"
              className="px-4 py-2 rounded-lg bg-slate-900 text-white hover:bg-slate-800 shadow"
            >
              Get Started
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <main className="max-w-6xl mx-auto px-4 py-14">
        <div className="grid md:grid-cols-2 gap-10 items-center">
          <div className="space-y-6">
            <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Memory-first AI for India</p>
            <h1 className="text-4xl md:text-5xl font-bold leading-tight text-slate-900">
              Smarter chats with personal memory, sports brains, and study focus.
            </h1>
            <p className="text-lg text-slate-700 max-w-xl">
              MyDost blends reliable predictions, multi-language study help, and horoscope guidance—grounded by
              your saved notes and preferences. No more starting from scratch every session.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link
                href="/signup"
                className="px-5 py-3 rounded-lg bg-slate-900 text-white text-sm font-semibold hover:bg-slate-800 shadow"
              >
                Get Started
              </Link>
              <Link
                href="/signin"
                className="px-5 py-3 rounded-lg border border-slate-300 text-sm font-semibold text-slate-800 hover:bg-white"
              >
                Sign In
              </Link>
            </div>
            <div className="flex items-center gap-3 text-sm text-slate-600">
              <Sparkles size={16} className="text-amber-500" />
              <span>Secure personal memory • Multi-language • Fast RAG responses</span>
            </div>
          </div>

          <div className="rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-700 text-white p-8 shadow-2xl border border-slate-700">
            <div className="flex items-center gap-3 mb-4">
              <Brain size={22} className="text-amber-300" />
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Memory Preview</p>
                <p className="text-lg font-semibold">Today’s context snapshot</p>
              </div>
            </div>
            <div className="space-y-3 text-sm text-slate-100">
              <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                <p className="font-semibold text-amber-200">Sports cues</p>
                <p>Chasing team bias: prefers chasing; asks for toss update.</p>
              </div>
              <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                <p className="font-semibold text-emerald-200">Study focus</p>
                <p>Prefers Hinglish explanations + bullet steps, short examples.</p>
              </div>
              <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                <p className="font-semibold text-indigo-200">Horoscope notes</p>
                <p>Sun: Leo • Looking for career guidance this week.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Features */}
        <section className="mt-16">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-full bg-slate-900 text-white flex items-center justify-center">
              <Shield size={18} />
            </div>
            <div>
              <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Why MyDost</p>
              <h2 className="text-2xl font-bold text-slate-900">Built for everyday answers that remember you</h2>
            </div>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            {features.map(({ title, desc, icon: Icon }) => (
              <div key={title} className="p-5 rounded-xl bg-white/70 border border-slate-200 shadow-sm hover:shadow-md transition">
                <div className="flex items-center gap-3 mb-2 text-slate-900">
                  <div className="w-10 h-10 rounded-lg bg-slate-900 text-white flex items-center justify-center">
                    <Icon size={18} />
                  </div>
                  <h3 className="text-lg font-semibold">{title}</h3>
                </div>
                <p className="text-sm text-slate-700 leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}

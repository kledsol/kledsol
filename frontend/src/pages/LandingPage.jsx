import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { HeartLensIcon } from "@/components/custom/Logo";
import { useAnalysis } from "@/App";
import { startAnalysis } from "@/lib/api";
import { toast } from "sonner";
import {
  Activity,
  Brain,
  Shield,
  ChevronRight,
  Menu,
  X,
} from "lucide-react";

const LandingPage = () => {
  const { setSessionId, setAnalysisType } = useAnalysis();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  const handleStartAnalysis = async (type) => {
    setLoading(true);
    try {
      const response = await startAnalysis(type);
      setSessionId(response.session_id);
      setAnalysisType(type);
      navigate("/clarity");
    } catch (error) {
      console.error("Failed to start:", error);
      toast.error("Failed to start analysis");
    } finally {
      setLoading(false);
    }
  };

  const isLoggedIn = !!localStorage.getItem("trustlens_user");

  const navItems = [
    { label: "Home", href: "/" },
    { label: "Why TrustLens", href: "#why" },
    { label: "How It Works", href: "#how" },
    { label: "Privacy", href: "#privacy" },
    ...(isLoggedIn ? [{ label: "My Analyses", href: "/my-analyses" }] : []),
  ];

  const whyBlocks = [
    {
      icon: Activity,
      accent: "#FF4D6D",
      title: "The Reality of Infidelity",
      description: "20-40% of relationships face infidelity. If something feels off, your instincts are worth exploring — not dismissing.",
    },
    {
      icon: Brain,
      accent: "#FCA311",
      title: "Why People Miss the Signs",
      description: "Love creates blind spots. When emotions run deep, small behavioral shifts get rationalized. Objective analysis becomes nearly impossible alone.",
    },
    {
      icon: Activity,
      accent: "#3DD9C5",
      title: "What TrustLens Does",
      description: "Maps relationship patterns — communication shifts, emotional distance, routine changes — using behavioral psychology and AI to reveal what they may mean.",
    },
    {
      icon: Shield,
      accent: "#6EE7B7",
      title: "Not Accusations, Only Clarity",
      description: "We don't tell you what to think. We give you structured analysis so you can see clearly and decide with empathy, not paranoia.",
    },
  ];

  return (
    <div className="min-h-screen bg-[#0B132B] relative overflow-hidden">
      {/* Cinematic Background Slideshow */}
      <div className="hero-slideshow">
        <div
          className="hero-slide"
          style={{ backgroundImage: "url(/hero_scene_1.jpg)" }}
        />
        <div
          className="hero-slide"
          style={{ backgroundImage: "url(/hero_scene_2.jpg)" }}
        />
      </div>
      <div className="hero-overlay" />
      <div className="absolute inset-0 hero-glow opacity-30 z-[2]" />

      {/* Navigation */}
      <header className="relative z-50">
        <nav className="container mx-auto px-6 py-6 flex items-center justify-between">
          <Link to="/" data-testid="logo-link">
            <img
              src="/trustlens-logo.png"
              alt="TrustLens"
              className="h-10 md:h-12 w-auto"
              data-testid="trustlens-logo"
            />
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-8">
            {navItems.map((item) => (
              <a
                key={item.label}
                href={item.href}
                className="text-sm text-muted-foreground hover:text-[#3DD9C5] transition-colors"
              >
                {item.label}
              </a>
            ))}
            <Button
              onClick={() => handleStartAnalysis("deep")}
              disabled={loading}
              className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-6 btn-glow"
              data-testid="nav-start-btn"
            >
              Start Analysis
            </Button>
          </div>

          {/* Mobile Menu Toggle */}
          <button
            className="md:hidden p-2 text-white"
            onClick={() => setMenuOpen(!menuOpen)}
            data-testid="mobile-menu-toggle"
          >
            {menuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </nav>

        {/* Mobile Menu */}
        {menuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="md:hidden absolute top-full left-0 right-0 bg-[#0A1120] border-b border-white/10 p-6"
          >
            {navItems.map((item) => (
              <a
                key={item.label}
                href={item.href}
                className="block py-3 text-muted-foreground hover:text-[#3DD9C5]"
              >
                {item.label}
              </a>
            ))}
            <Button
              onClick={() => handleStartAnalysis("deep")}
              className="mt-4 w-full bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full"
            >
              Start Analysis
            </Button>
          </motion.div>
        )}
      </header>

      {/* Hero Section */}
      <main className="relative z-10 container mx-auto px-6 pt-16 md:pt-24 pb-32">
        <div className="max-w-3xl flex flex-col justify-center">
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            className="font-light text-white tracking-tight mb-8 leading-[1.15]"
            style={{ fontFamily: 'Fraunces, serif', fontSize: 'clamp(38px, 6vw, 64px)' }}
            data-testid="hero-headline"
          >
            Millions of people question what is really happening in their relationship.
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.15, ease: [0.22, 1, 0.36, 1] }}
            className="text-[#C8D3DC] max-w-2xl mb-4 leading-relaxed"
            style={{ fontSize: 'clamp(18px, 2.5vw, 22px)' }}
            data-testid="hero-subheadline"
          >
            Sometimes it's distance.
            <br />
            Sometimes it's misunderstanding.
            <br />
            Sometimes it's something deeper.
          </motion.p>

          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.25, ease: [0.22, 1, 0.36, 1] }}
            className="text-[#3DD9C5] font-medium max-w-2xl mb-12"
            style={{ fontSize: 'clamp(18px, 2.5vw, 22px)' }}
            data-testid="hero-tagline"
          >
            TrustLens helps you interpret the signals.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.35, ease: [0.22, 1, 0.36, 1] }}
            className="flex flex-col sm:flex-row gap-4"
          >
            <Button
              onClick={() => handleStartAnalysis("deep")}
              disabled={loading}
              size="lg"
              className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-10 py-7 text-lg sm:text-xl font-semibold btn-glow transition-all hover:scale-105 shadow-lg shadow-[#3DD9C5]/25"
              data-testid="start-analysis-btn"
            >
              {loading ? "Starting..." : "Start Relationship Analysis"}
              <ChevronRight className="w-6 h-6 ml-2" />
            </Button>
            <Button
              onClick={() => handleStartAnalysis("pulse")}
              disabled={loading}
              variant="outline"
              size="lg"
              className="border-white/30 text-white hover:bg-white/10 rounded-full px-8 py-7 text-base sm:text-lg"
              data-testid="pulse-btn"
            >
              <HeartLensIcon size={22} />
              <span className="ml-2">Check Relationship Pulse</span>
            </Button>
          </motion.div>

          {/* Reassurance Line */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.7, delay: 0.45 }}
            className="mt-8 text-[#8899A6]"
            style={{ fontSize: 'clamp(16px, 2vw, 18px)' }}
            data-testid="privacy-reassurance"
          >
            Private. Anonymous. No account required.
          </motion.p>
        </div>

        {/* Why TrustLens Section */}
        <motion.section
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.7, delay: 0.5 }}
          className="mt-32"
          id="why"
        >
          <h2
            className="text-3xl sm:text-4xl font-light text-[#E6EDF3] mb-4"
            style={{ fontFamily: "Fraunces, serif" }}
          >
            Why TrustLens
          </h2>
          <p className="text-base text-[#8899A6] max-w-xl mb-14 leading-relaxed">
            Understanding your relationship shouldn't require guesswork.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {whyBlocks.map((block, index) => (
              <motion.div
                key={block.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.6 + index * 0.1 }}
                className="glass-card rounded-2xl p-6 sm:p-8 hover:border-[#3DD9C5]/30 transition-all duration-500 group"
                data-testid={`why-block-${index}`}
              >
                <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-4" style={{ backgroundColor: `${block.accent}15` }}>
                  <block.icon className="w-5 h-5" style={{ color: block.accent }} />
                </div>
                <h3 className="text-base font-medium text-[#E6EDF3] mb-2">
                  {block.title}
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {block.description}
                </p>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* How It Works Section */}
        <motion.section
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.7, delay: 0.8 }}
          className="mt-32"
          id="how"
        >
          <h2 className="text-4xl md:text-5xl font-light text-[#E6EDF3] mb-16" style={{ fontFamily: 'Fraunces, serif' }}>
            How TrustLens Works
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { step: "01", title: "Share Your Experience", desc: "Answer questions about recent changes you've noticed in your relationship" },
              { step: "02", title: "AI Analysis", desc: "Our empathetic AI analyzes patterns using relationship psychology principles" },
              { step: "03", title: "Gain Clarity", desc: "Receive insights and suggested actions to improve communication" },
            ].map((item, i) => (
              <div key={i} className="relative">
                <span className="text-7xl font-light text-[#3DD9C5]/20" style={{ fontFamily: 'Fraunces, serif' }}>
                  {item.step}
                </span>
                <h3 className="text-xl font-medium text-[#E6EDF3] mt-4 mb-2">
                  {item.title}
                </h3>
                <p className="text-muted-foreground">{item.desc}</p>
              </div>
            ))}
          </div>
        </motion.section>

        {/* Privacy Section */}
        <motion.section
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.7, delay: 1 }}
          className="mt-32 glass-card rounded-3xl p-12"
          id="privacy"
        >
          <div className="flex items-start gap-6">
            <Shield className="w-12 h-12 text-[#3DD9C5] flex-shrink-0" />
            <div>
              <h2 className="text-3xl font-light text-[#E6EDF3] mb-4" style={{ fontFamily: 'Fraunces, serif' }}>
                Your Privacy is Sacred
              </h2>
              <p className="text-muted-foreground leading-relaxed max-w-2xl">
                TrustLens does not spy on anyone. We don't track phones, locations, or
                messages. All analysis is based solely on what you choose to share.
                Your data is never stored permanently and is never shared with anyone.
                You can run analyses completely anonymously.
              </p>
            </div>
          </div>
        </motion.section>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/10 py-12">
        <div className="container mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6">
          <img src="/trustlens-logo.png" alt="TrustLens" className="h-8 w-auto" />
          <p className="text-sm text-muted-foreground">
            Empathetic relationship analysis powered by AI
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;

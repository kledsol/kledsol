import { useState, useEffect, useCallback } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { useAnalysis } from "@/App";
import { startAnalysis } from "@/lib/api";
import { toast } from "sonner";
import {
  Shield,
  Menu,
  X,
  MessageCircle,
  Brain,
  Sun,
} from "lucide-react";

const ScannerLogo = ({ size = 24 }) => (
  <svg width={size} height={size} viewBox="0 0 40 40" className="mx-[3px]">
    {/* Outer ring */}
    <circle cx="20" cy="20" r="16" fill="none" stroke="#3DD9C5" strokeWidth="1.5" opacity="0.5" />
    {/* Middle ring */}
    <circle cx="20" cy="20" r="11" fill="none" stroke="#3DD9C5" strokeWidth="1.8" opacity="0.7" />
    {/* Inner dot */}
    <circle cx="20" cy="20" r="5" fill="#3DD9C5" opacity="0.8" />
    {/* Scanner tick marks — cardinal */}
    <line x1="20" y1="1" x2="20" y2="6" stroke="#3DD9C5" strokeWidth="1.5" opacity="0.6" />
    <line x1="20" y1="34" x2="20" y2="39" stroke="#3DD9C5" strokeWidth="1.5" opacity="0.6" />
    <line x1="1" y1="20" x2="6" y2="20" stroke="#3DD9C5" strokeWidth="1.5" opacity="0.6" />
    <line x1="34" y1="20" x2="39" y2="20" stroke="#3DD9C5" strokeWidth="1.5" opacity="0.6" />
    {/* Scanner tick marks — diagonal */}
    <line x1="7.5" y1="7.5" x2="10.5" y2="10.5" stroke="#3DD9C5" strokeWidth="1.2" opacity="0.4" />
    <line x1="29.5" y1="7.5" x2="32.5" y2="10.5" stroke="#3DD9C5" strokeWidth="1.2" opacity="0.4" style={{ transform: 'rotate(90deg)', transformOrigin: '31px 9px' }} />
    <line x1="7.5" y1="32.5" x2="10.5" y2="29.5" stroke="#3DD9C5" strokeWidth="1.2" opacity="0.4" />
    <line x1="29.5" y1="29.5" x2="32.5" y2="32.5" stroke="#3DD9C5" strokeWidth="1.2" opacity="0.4" />
  </svg>
);

const LandingPage = () => {
  const { setSessionId, setAnalysisType } = useAnalysis();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [textVisible, setTextVisible] = useState(false);

  const slides = [
    { image: "/hero_scene_1.jpg" },
    { image: "/hero_scene_2.jpg" },
    { image: "/hero_scene_3.jpg" },
  ];

  const advanceSlide = useCallback(() => {
    setTextVisible(false);
    setTimeout(() => {
      setCurrentSlide((prev) => (prev + 1) % 3);
    }, 600);
  }, []);

  useEffect(() => {
    const durations = [5000, 8000, 7000];
    const textDelays = [400, 1200, 1200];
    const textTimer = setTimeout(() => setTextVisible(true), textDelays[currentSlide]);
    const slideTimer = setTimeout(advanceSlide, durations[currentSlide]);
    return () => { clearTimeout(textTimer); clearTimeout(slideTimer); };
  }, [currentSlide, advanceSlide]);

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
      image: "/why_trustlens_1.jpg",
      title: "The Reality of Infidelity",
      text: "1 in 5 people admits having cheated at least once in a long-term relationship. Yet most partners discover it months or even years later. Why? Because the signs usually appear gradually and are easy to misinterpret.",
    },
    {
      image: "/why_trustlens_2.jpg",
      title: "Why People Miss the Signs",
      text: "When emotions are involved, it becomes difficult to evaluate situations objectively. People often ignore warning signs, rationalize unusual behavior, or doubt their own perception. TrustLens helps structure these signals into a clearer analysis.",
    },
    {
      image: "/why_trustlens_3.jpg",
      title: "What TrustLens Actually Does",
      text: "TrustLens analyzes patterns such as behavioral changes, secrecy around phone or schedule, emotional distancing, and inconsistencies in explanations. Your responses are compared with documented relationship patterns to provide an objective clarity score.",
    },
    {
      image: "/why_trustlens_4.jpg",
      title: "Not Accusations, Only Clarity",
      text: "TrustLens does not accuse anyone. Instead, it helps answer a question many people quietly ask themselves: \"Is something really going on, or am I imagining things?\"",
    },
  ];

  return (
    <div className="bg-[#0B132B]">
      {/* ===== HERO ===== */}
      <div className="relative overflow-hidden">
        <div className="hero-slideshow">
          {slides.map((slide, i) => (
            <div
              key={i}
              className={`hero-slide ${currentSlide === i ? 'active' : ''}`}
              style={{ backgroundImage: `url(${slide.image})` }}
            />
          ))}
        </div>
        <div className="hero-overlay" />
        <div className="absolute inset-0 hero-glow opacity-30 z-[2]" />

        {/* Navigation */}
        <header className="relative z-50">
          <nav className="container mx-auto px-6 md:px-10 py-6 md:py-8 flex items-center justify-between">
            <Link to="/" className="flex items-center" data-testid="logo-link">
              <span
                className="text-white text-2xl md:text-[1.7rem] font-light tracking-tight drop-shadow-[0_1px_8px_rgba(255,255,255,0.15)] flex items-center"
                style={{ fontFamily: 'Fraunces, serif' }}
                data-testid="trustlens-logo"
              >
                Trust
                <ScannerLogo size={28} />
                <span className="text-[#3DD9C5]">Lens</span>
              </span>
            </Link>
            <div className="hidden md:flex items-center gap-8">
              {navItems.map((item) => (
                <a key={item.label} href={item.href} className="text-[15px] text-white/65 hover:text-[#3DD9C5] transition-colors">
                  {item.label}
                </a>
              ))}
              <Button
                onClick={() => handleStartAnalysis("deep")}
                disabled={loading}
                className="bg-[#ff2e8b] text-white hover:bg-[#e0267a] rounded-full px-6 text-[15px]"
                data-testid="nav-start-btn"
              >
                Start Analysis
              </Button>
            </div>
            <button className="md:hidden p-2 text-white" onClick={() => setMenuOpen(!menuOpen)} data-testid="mobile-menu-toggle">
              {menuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </nav>
          {menuOpen && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="md:hidden absolute top-full left-0 right-0 bg-[#0A1120] border-b border-white/10 p-6 z-50"
            >
              {navItems.map((item) => (
                <a key={item.label} href={item.href} className="block py-3 text-white/60 hover:text-[#3DD9C5]">{item.label}</a>
              ))}
              <Button onClick={() => handleStartAnalysis("deep")} className="mt-4 w-full bg-[#ff2e8b] text-white hover:bg-[#e0267a] rounded-full">
                Start Analysis
              </Button>
            </motion.div>
          )}
        </header>

        {/* Hero Content */}
        <section className="relative z-10 min-h-screen flex items-center">
          {/* Side margin — left (desktop only) */}
          <div className="hidden lg:flex absolute left-6 top-1/2 -translate-y-1/2 z-20">
            <p className="text-[11px] text-white/30 tracking-wide [writing-mode:vertical-lr] rotate-180">
              Based on 300+ documented relationship cases
            </p>
          </div>

          {/* Side margin — right (desktop only) */}
          <div className="hidden lg:flex absolute right-6 top-1/2 -translate-y-1/2 z-20">
            <p className="text-[11px] text-white/30 tracking-wide [writing-mode:vertical-lr]">
              Private &bull; Anonymous &bull; No account required
            </p>
          </div>

          {/* Centered hero text — 3-act storytelling */}
          <div className="w-full max-w-[680px] mx-auto px-6 sm:px-10 text-center -mt-36 ml-auto mr-auto md:mr-[15%] md:ml-[5%]">
            {/* ACT 1: The Question (Slide 1 — Woman) */}
            {currentSlide === 0 && (
              <div className={`hero-text-block ${textVisible ? 'visible' : ''}`}>
                <h1
                  className="text-white font-light tracking-tight mb-10 leading-[1.1]"
                  style={{ fontFamily: 'Fraunces, serif', fontSize: 'clamp(46px, 9.6vw, 86px)' }}
                  data-testid="hero-headline"
                >
                  Is my partner cheating?
                </h1>
              </div>
            )}

            {/* ACT 2: The Signs (Slide 2 — Gay couple) */}
            {currentSlide === 1 && (
              <div className={`hero-text-block ${textVisible ? 'visible' : ''}`} data-testid="hero-narrative">
                <p className="text-white/80 leading-[1.7] mb-4" style={{ fontSize: 'clamp(20px, 4.8vw, 26px)' }}>
                  Sometimes the signs are subtle.
                </p>
                <p className="text-white/60 leading-[1.8] mb-4" style={{ fontSize: 'clamp(19px, 4.2vw, 24px)' }}>
                  Late nights.<br />
                  A locked phone.<br />
                  Emotional distance.
                </p>
                <p className="text-white/70 leading-[1.7]" style={{ fontSize: 'clamp(19px, 4.2vw, 24px)' }}>
                  Small changes that slowly start to feel like signals.
                </p>
              </div>
            )}

            {/* ACT 3: The Solution (Slide 3 — Mixed couple) */}
            {currentSlide === 2 && (
              <div className={`hero-text-block ${textVisible ? 'visible' : ''}`}>
                <p className="text-white/90 leading-[1.7]" style={{ fontSize: 'clamp(19px, 4.6vw, 25px)' }}>
                  TrustLens analyzes relationship behaviors,<br className="hidden sm:block" />
                  compares them with real relationship patterns,<br className="hidden sm:block" />
                  and helps you understand what those signals might actually mean.
                </p>
              </div>
            )}

            {/* CTA — always visible */}
            <div className="mt-10">
              <Button
                onClick={() => handleStartAnalysis("deep")}
                disabled={loading}
                size="lg"
                className="bg-[#ff2e8b] text-white hover:bg-[#ff3c8f] rounded-full px-12 py-7 text-lg sm:text-xl font-semibold transition-all hover:scale-105 shadow-lg shadow-[#ff2e8b]/30"
                data-testid="start-analysis-btn"
              >
                {loading ? "Starting..." : "Start Relationship Analysis"}
              </Button>
              <p className="text-white/60 text-base mt-4" data-testid="hero-duration">
                3-minute relationship analysis
              </p>
              <p className="text-white/45 text-sm tracking-wide mt-1" data-testid="privacy-reassurance">
                Private &bull; Anonymous &bull; No account required
              </p>
            </div>
          </div>
        </section>
      </div>

      {/* ===== CONTENT SECTIONS ===== */}
      <main className="bg-[#0B132B] px-5 sm:px-10 md:px-16 pb-32">

        {/* Why TrustLens Section */}
        <section className="pt-24 md:pt-32 max-w-6xl mx-auto" id="why">
          <h2
            className="text-3xl sm:text-4xl md:text-5xl font-light text-[#E6EDF3] mb-6"
            style={{ fontFamily: "Fraunces, serif" }}
          >
            Why TrustLens Exists
          </h2>
          <div className="max-w-2xl mb-16 space-y-4">
            <p className="text-sm sm:text-base text-[#A0AEC0] leading-relaxed">
              Millions of people suspect something in their relationship but struggle to interpret the signs.
            </p>
            <p className="text-sm sm:text-base text-[#A0AEC0] leading-relaxed">
              Small changes in behavior — late nights, secrecy, emotional distance — can create doubt.
              But doubt alone does not provide clarity.
            </p>
            <p className="text-sm sm:text-base text-white/80 leading-relaxed font-medium">
              TrustLens helps analyze these signals objectively.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8">
            {whyBlocks.map((block, index) => (
              <motion.div
                key={block.title}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.5, delay: index * 0.08 }}
                className="rounded-2xl overflow-hidden flex flex-col bg-[#111B33] border border-white/[0.07] shadow-lg shadow-black/20"
                data-testid={`why-block-${index}`}
              >
                <img
                  src={block.image}
                  alt={block.title}
                  className="w-full h-48 sm:h-52 object-cover"
                  loading="lazy"
                />
                <div className="p-6 sm:p-8 flex-1">
                  <h3
                    className="text-lg sm:text-xl font-semibold text-white mb-3"
                    style={{ fontFamily: "Fraunces, serif" }}
                  >
                    {block.title}
                  </h3>
                  <p className="text-sm sm:text-base text-[#A0AEC0] leading-relaxed">
                    {block.text}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </section>

        {/* How It Works Section */}
        <section className="mt-32 max-w-6xl mx-auto" id="how">
          <h2 className="text-4xl md:text-5xl font-light text-[#E6EDF3] mb-16" style={{ fontFamily: 'Fraunces, serif' }}>
            How TrustLens Works
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { step: "01", icon: <MessageCircle className="w-10 h-10" />, title: "Share Your Experience", desc: "Answer questions about recent changes you've noticed in your relationship" },
              { step: "02", icon: <Brain className="w-10 h-10" />, title: "AI Analysis", desc: "Our empathetic AI analyzes patterns using relationship psychology principles" },
              { step: "03", icon: <Sun className="w-10 h-10" />, title: "Gain Clarity", desc: "Receive insights and suggested actions to improve communication" },
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.5, delay: i * 0.12 }}
                className="relative bg-[#111B33]/50 border border-white/[0.07] rounded-2xl p-8"
              >
                <div className="flex items-center gap-4 mb-6">
                  <span className="text-5xl font-light text-[#3DD9C5]/20" style={{ fontFamily: 'Fraunces, serif' }}>{item.step}</span>
                  <div className="w-14 h-14 rounded-full bg-[#3DD9C5]/10 border border-[#3DD9C5]/20 flex items-center justify-center text-[#3DD9C5]">
                    {item.icon}
                  </div>
                </div>
                <h3 className="text-xl font-medium text-[#E6EDF3] mb-3">{item.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </section>

        {/* Privacy Section */}
        <section className="mt-32 max-w-6xl mx-auto glass-card rounded-3xl p-12" id="privacy">
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
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 py-12">
        <div className="container mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6">
          <span className="text-white text-lg font-light tracking-tight flex items-center" style={{ fontFamily: 'Fraunces, serif' }}>
            Trust
            <ScannerLogo size={22} />
            <span className="text-[#3DD9C5]">Lens</span>
          </span>
          <p className="text-sm text-muted-foreground">Empathetic relationship analysis powered by AI</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;

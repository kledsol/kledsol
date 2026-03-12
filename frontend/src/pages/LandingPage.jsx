import { useState } from "react";
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
      image: "https://images.unsplash.com/photo-1717381539587-efe2070e4b92?w=800&q=80",
      title: "The Reality of Infidelity",
      text: "1 in 5 people admits having cheated at least once in a long-term relationship. Yet most partners discover it months or even years later. Why? Because the signs usually appear gradually and are easy to misinterpret.",
    },
    {
      image: "https://images.unsplash.com/photo-1710503701213-6b79941f5660?w=800&q=80",
      title: "Why People Miss the Signs",
      text: "When emotions are involved, it becomes difficult to evaluate situations objectively. People often ignore warning signs, rationalize unusual behavior, or doubt their own perception. TrustLens helps structure these signals into a clearer analysis.",
    },
    {
      image: "https://images.unsplash.com/photo-1654764450273-59862da1a259?w=800&q=80",
      title: "What TrustLens Actually Does",
      text: "TrustLens analyzes patterns such as behavioral changes, secrecy around phone or schedule, emotional distancing, and inconsistencies in explanations. Your responses are compared with documented relationship patterns to provide an objective clarity score.",
    },
    {
      image: "https://images.unsplash.com/photo-1663361963652-e7c0a08c06d3?w=800&q=80",
      title: "Not Accusations, Only Clarity",
      text: "TrustLens does not accuse anyone. Instead, it helps answer a question many people quietly ask themselves: \"Is something really going on, or am I imagining things?\"",
    },
  ];

  return (
    <div className="bg-[#0B132B]">
      {/* ===== HERO ===== */}
      <div className="relative overflow-hidden">
        <div className="hero-slideshow">
          <div className="hero-slide" style={{ backgroundImage: "url(/hero_scene_1.jpg)" }} />
          <div className="hero-slide" style={{ backgroundImage: "url(/hero_scene_2.jpg)" }} />
        </div>
        <div className="hero-overlay" />
        <div className="absolute inset-0 hero-glow opacity-30 z-[2]" />

        {/* Navigation */}
        <header className="relative z-50">
          <nav className="container mx-auto px-6 py-6 flex items-center justify-between">
            <Link to="/" data-testid="logo-link">
              <img src="/trustlens-logo.png" alt="TrustLens" className="h-10 md:h-12 w-auto" data-testid="trustlens-logo" />
            </Link>
            <div className="hidden md:flex items-center gap-8">
              {navItems.map((item) => (
                <a key={item.label} href={item.href} className="text-sm text-white/60 hover:text-[#3DD9C5] transition-colors">
                  {item.label}
                </a>
              ))}
              <Button
                onClick={() => handleStartAnalysis("deep")}
                disabled={loading}
                className="bg-[#ff2e8b] text-white hover:bg-[#e0267a] rounded-full px-6"
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
        <section className="relative z-10 min-h-[72vh] md:min-h-[88vh] flex items-center">
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

          {/* Centered hero text */}
          <div className="w-full max-w-[620px] mx-auto px-6 sm:px-10 text-center">
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
              className="text-white font-light tracking-tight mb-10 leading-[1.1]"
              style={{ fontFamily: 'Fraunces, serif', fontSize: 'clamp(36px, 8vw, 68px)' }}
              data-testid="hero-headline"
            >
              Is my partner cheating?
            </motion.h1>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.15, ease: [0.22, 1, 0.36, 1] }}
              className="mb-10 space-y-5"
              data-testid="hero-narrative"
            >
              <p className="text-white/70 leading-[1.7]" style={{ fontSize: 'clamp(16px, 3.8vw, 20px)' }}>
                Sometimes the signs are subtle.
              </p>
              <p className="text-white/50 leading-[1.7]" style={{ fontSize: 'clamp(15px, 3.5vw, 18px)' }}>
                Late nights.<br />
                A locked phone.<br />
                Emotional distance.
              </p>
              <p className="text-white/60 leading-[1.7]" style={{ fontSize: 'clamp(15px, 3.5vw, 18px)' }}>
                Small changes that slowly start to feel like signals.
              </p>
              <p className="text-white/80 leading-[1.7]" style={{ fontSize: 'clamp(15px, 3.5vw, 18px)' }}>
                TrustLens analyzes relationship behaviors,<br className="hidden sm:block" />
                compares them with real relationship patterns,<br className="hidden sm:block" />
                and helps you understand what those signals might actually mean.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.35, ease: [0.22, 1, 0.36, 1] }}
              className="flex flex-col items-center gap-4"
            >
              <Button
                onClick={() => handleStartAnalysis("deep")}
                disabled={loading}
                size="lg"
                className="bg-[#ff2e8b] text-white hover:bg-[#ff3c8f] rounded-full px-12 py-7 text-lg sm:text-xl font-semibold transition-all hover:scale-105 shadow-lg shadow-[#ff2e8b]/30"
                data-testid="start-analysis-btn"
              >
                {loading ? "Starting..." : "Start Relationship Analysis"}
              </Button>
              <p className="text-white/50 text-sm" data-testid="hero-duration">
                3-minute relationship analysis
              </p>
              <p className="text-white/35 text-xs tracking-wide" data-testid="privacy-reassurance">
                Private &bull; Anonymous &bull; No account required
              </p>
            </motion.div>
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
          <div className="max-w-2xl mb-20 space-y-4">
            <p className="text-sm sm:text-base text-[#8899A6] leading-relaxed">
              Millions of people suspect something in their relationship but struggle to interpret the signs.
            </p>
            <p className="text-sm sm:text-base text-[#8899A6] leading-relaxed">
              Small changes in behavior — late nights, secrecy, emotional distance — can create doubt.
              But doubt alone does not provide clarity.
            </p>
            <p className="text-sm sm:text-base text-[#E6EDF3]/80 leading-relaxed font-medium">
              TrustLens helps analyze these signals objectively.
            </p>
          </div>

          <div className="space-y-10">
            {whyBlocks.map((block, index) => (
              <motion.div
                key={block.title}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.5, delay: index * 0.08 }}
                className="glass-card rounded-2xl overflow-hidden flex flex-col md:flex-row"
                data-testid={`why-block-${index}`}
              >
                <div className="md:w-[320px] flex-shrink-0">
                  <img
                    src={block.image}
                    alt={block.title}
                    className="w-full h-48 sm:h-52 md:h-full object-cover"
                    loading="lazy"
                  />
                </div>
                <div className="p-6 sm:p-8 flex-1 flex flex-col justify-center">
                  <h3
                    className="text-lg sm:text-xl font-medium text-[#E6EDF3] mb-3"
                    style={{ fontFamily: "Fraunces, serif" }}
                  >
                    {block.title}
                  </h3>
                  <p className="text-sm sm:text-base text-[#8899A6] leading-relaxed">
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
              { step: "01", title: "Share Your Experience", desc: "Answer questions about recent changes you've noticed in your relationship" },
              { step: "02", title: "AI Analysis", desc: "Our empathetic AI analyzes patterns using relationship psychology principles" },
              { step: "03", title: "Gain Clarity", desc: "Receive insights and suggested actions to improve communication" },
            ].map((item, i) => (
              <div key={i} className="relative">
                <span className="text-7xl font-light text-[#3DD9C5]/20" style={{ fontFamily: 'Fraunces, serif' }}>{item.step}</span>
                <h3 className="text-xl font-medium text-[#E6EDF3] mt-4 mb-2">{item.title}</h3>
                <p className="text-muted-foreground">{item.desc}</p>
              </div>
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
          <img src="/trustlens-logo.png" alt="TrustLens" className="h-8 w-auto" />
          <p className="text-sm text-muted-foreground">Empathetic relationship analysis powered by AI</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;

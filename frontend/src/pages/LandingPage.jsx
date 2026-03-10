import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { TrustLensLogo, HeartLensIcon } from "@/components/custom/Logo";
import { useAnalysis } from "@/App";
import { startAnalysis } from "@/lib/api";
import { toast } from "sonner";
import {
  Activity,
  Brain,
  Shield,
  Heart,
  MessageSquare,
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

  const navItems = [
    { label: "Home", href: "/" },
    { label: "Why TrustLens", href: "#why" },
    { label: "How It Works", href: "#how" },
    { label: "Privacy", href: "#privacy" },
  ];

  const features = [
    {
      icon: Brain,
      title: "AI-Powered Analysis",
      description: "Intelligent pattern recognition using relationship psychology",
    },
    {
      icon: Activity,
      title: "Behavioral Signals",
      description: "Track and analyze changes in relationship dynamics",
    },
    {
      icon: Heart,
      title: "Emotional Intelligence",
      description: "Empathetic insights without judgment or accusations",
    },
    {
      icon: Shield,
      title: "Complete Privacy",
      description: "Anonymous analysis with no data sharing or tracking",
    },
  ];

  return (
    <div className="min-h-screen bg-[#14213D] relative overflow-hidden">
      {/* Hero Background */}
      <div
        className="absolute inset-0 bg-cover bg-center opacity-10"
        style={{
          backgroundImage:
            "url(https://images.unsplash.com/photo-1566121822676-ce12612f5600?crop=entropy&cs=srgb&fm=jpg&q=85)",
        }}
      />
      <div className="absolute inset-0 hero-glow" />

      {/* Navigation */}
      <header className="relative z-50">
        <nav className="container mx-auto px-6 py-6 flex items-center justify-between">
          <Link to="/" data-testid="logo-link">
            <TrustLensLogo size="md" />
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-8">
            {navItems.map((item) => (
              <a
                key={item.label}
                href={item.href}
                className="text-sm text-muted-foreground hover:text-[#2EC4B6] transition-colors"
              >
                {item.label}
              </a>
            ))}
            <Button
              onClick={() => handleStartAnalysis("deep")}
              disabled={loading}
              className="bg-[#2EC4B6] text-black hover:bg-[#259F94] rounded-full px-6 btn-glow"
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
                className="block py-3 text-muted-foreground hover:text-[#2EC4B6]"
              >
                {item.label}
              </a>
            ))}
            <Button
              onClick={() => handleStartAnalysis("deep")}
              className="mt-4 w-full bg-[#2EC4B6] text-black hover:bg-[#259F94] rounded-full"
            >
              Start Analysis
            </Button>
          </motion.div>
        )}
      </header>

      {/* Hero Section */}
      <main className="relative z-10 container mx-auto px-6 pt-16 pb-32">
        <div className="max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            className="mb-6"
          >
            <span className="text-sm tracking-wider uppercase text-[#2EC4B6] font-mono">
              Wondering if something is going on behind your back?
            </span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
            className="text-5xl md:text-7xl font-light text-[#F5F7FA] tracking-tight leading-none mb-8"
            style={{ fontFamily: 'Fraunces, serif' }}
          >
            Is your partner cheating?
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
            className="text-lg text-muted-foreground max-w-2xl mb-12 leading-relaxed"
          >
            Millions of people ask themselves the same question.
            Most struggle to interpret the signs.
            <br /><br />
            TrustLens helps you understand what may really be happening through intelligent relationship analysis.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
            className="flex flex-col sm:flex-row gap-4"
          >
            <Button
              onClick={() => handleStartAnalysis("deep")}
              disabled={loading}
              size="lg"
              className="bg-[#2EC4B6] text-black hover:bg-[#259F94] rounded-full px-8 py-6 text-lg font-medium btn-glow transition-all hover:scale-105"
              data-testid="start-analysis-btn"
            >
              {loading ? "Starting..." : "Start Relationship Analysis"}
              <ChevronRight className="w-5 h-5 ml-2" />
            </Button>
            <Button
              onClick={() => handleStartAnalysis("pulse")}
              disabled={loading}
              variant="outline"
              size="lg"
              className="border-white/20 text-white hover:bg-white/5 rounded-full px-8 py-6 text-lg"
              data-testid="pulse-btn"
            >
              <HeartLensIcon size={20} />
              <span className="ml-2">Check Relationship Pulse</span>
            </Button>
          </motion.div>

          {/* Reassurance Line */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.7, delay: 0.4 }}
            className="mt-6 text-sm text-muted-foreground"
          >
            Private. Anonymous. No account required.
          </motion.p>
        </div>

        {/* Features Grid */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.7, delay: 0.5 }}
          className="mt-32 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
          id="why"
        >
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.6 + index * 0.1 }}
              className="glass-card rounded-2xl p-8 hover:border-[#2EC4B6]/30 transition-all duration-500"
              data-testid={`feature-${index}`}
            >
              <div className="w-12 h-12 rounded-xl bg-[#2EC4B6]/10 flex items-center justify-center mb-6">
                <feature.icon className="w-6 h-6 text-[#2EC4B6]" />
              </div>
              <h3 className="text-lg font-medium text-[#F5F7FA] mb-2">
                {feature.title}
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </motion.div>

        {/* How It Works Section */}
        <motion.section
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.7, delay: 0.8 }}
          className="mt-32"
          id="how"
        >
          <h2 className="text-4xl md:text-5xl font-light text-[#F5F7FA] mb-16" style={{ fontFamily: 'Fraunces, serif' }}>
            How TrustLens Works
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { step: "01", title: "Share Your Experience", desc: "Answer questions about recent changes you've noticed in your relationship" },
              { step: "02", title: "AI Analysis", desc: "Our empathetic AI analyzes patterns using relationship psychology principles" },
              { step: "03", title: "Gain Clarity", desc: "Receive insights and suggested actions to improve communication" },
            ].map((item, i) => (
              <div key={i} className="relative">
                <span className="text-7xl font-light text-[#2EC4B6]/20" style={{ fontFamily: 'Fraunces, serif' }}>
                  {item.step}
                </span>
                <h3 className="text-xl font-medium text-[#F5F7FA] mt-4 mb-2">
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
            <Shield className="w-12 h-12 text-[#2EC4B6] flex-shrink-0" />
            <div>
              <h2 className="text-3xl font-light text-[#F5F7FA] mb-4" style={{ fontFamily: 'Fraunces, serif' }}>
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
          <TrustLensLogo size="sm" />
          <p className="text-sm text-muted-foreground">
            Empathetic relationship analysis powered by AI
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;

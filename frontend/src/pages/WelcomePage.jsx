import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { useTheme, useAnalysis } from "@/App";
import { startAnalysis } from "@/lib/api";
import { toast } from "sonner";
import {
  Eye,
  Shield,
  Brain,
  Activity,
  Moon,
  Sun,
  ChevronRight,
  Lock,
} from "lucide-react";

const WelcomePage = () => {
  const { theme, toggleTheme } = useTheme();
  const { setSessionId, setCurrentStep } = useAnalysis();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleStartAnalysis = async () => {
    setLoading(true);
    try {
      const response = await startAnalysis();
      setSessionId(response.session_id);
      setCurrentStep("baseline");
      toast.success("Analysis session started");
      navigate("/baseline");
    } catch (error) {
      console.error("Failed to start analysis:", error);
      toast.error("Failed to start analysis. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const features = [
    {
      icon: Brain,
      title: "Behavioral Pattern Analysis",
      description: "AI-powered detection of behavioral changes and patterns",
    },
    {
      icon: Activity,
      title: "Probabilistic Inference",
      description: "Multiple competing hypotheses evaluated simultaneously",
    },
    {
      icon: Eye,
      title: "Narrative Consistency",
      description: "Detection of micro-contradictions and timeline shifts",
    },
    {
      icon: Shield,
      title: "Privacy-First Design",
      description: "No surveillance, no tracking, your data stays private",
    },
  ];

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Background */}
      <div
        className="absolute inset-0 bg-cover bg-center opacity-20"
        style={{
          backgroundImage:
            "url(https://images.unsplash.com/photo-1638804092353-58df91a322ad?crop=entropy&cs=srgb&fm=jpg&q=85)",
        }}
      />
      <div className="absolute inset-0 bg-gradient-to-b from-background/80 via-background/95 to-background" />

      {/* Theme Toggle */}
      <motion.button
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        onClick={toggleTheme}
        className="absolute top-6 right-6 p-3 rounded-full bg-card/80 backdrop-blur border border-border/50 hover:bg-accent/20 transition-all z-10"
        data-testid="theme-toggle"
      >
        {theme === "dark" ? (
          <Sun className="w-5 h-5 text-foreground" />
        ) : (
          <Moon className="w-5 h-5 text-foreground" />
        )}
      </motion.button>

      {/* Main Content */}
      <div className="relative z-10 container mx-auto px-6 py-12 min-h-screen flex flex-col justify-center">
        <div className="max-w-4xl mx-auto text-center">
          {/* Logo/Brand */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mb-8"
          >
            <div className="inline-flex items-center gap-3 mb-6">
              <div className="w-12 h-12 rounded-xl bg-accent/20 flex items-center justify-center pulse-glow">
                <Eye className="w-6 h-6 text-accent" />
              </div>
              <span className="text-3xl font-bold tracking-tight text-foreground">
                TrustLens
              </span>
            </div>
          </motion.div>

          {/* Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-4xl sm:text-5xl lg:text-6xl font-bold text-foreground mb-6 tracking-tight"
          >
            See what relationship
            <br />
            <span className="text-accent">patterns reveal</span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-base sm:text-lg text-muted-foreground max-w-2xl mx-auto mb-12"
          >
            Understand behavioral changes and trust dynamics through intelligent
            pattern analysis. No accusations, no surveillance — just clarity
            through data.
          </motion.p>

          {/* CTA Button */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="mb-16"
          >
            <Button
              onClick={handleStartAnalysis}
              disabled={loading}
              size="lg"
              data-testid="start-analysis-btn"
              className="bg-accent hover:bg-accent/90 text-accent-foreground px-8 py-6 text-lg rounded-xl shadow-lg hover:shadow-xl transition-all group"
            >
              {loading ? (
                "Starting..."
              ) : (
                <>
                  Start Relationship Analysis
                  <ChevronRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </Button>
          </motion.div>

          {/* Features Grid */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
          >
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.5 + index * 0.1 }}
                className="p-6 rounded-xl bg-card/60 backdrop-blur border border-border/50 hover:border-accent/30 transition-all group"
                data-testid={`feature-card-${index}`}
              >
                <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center mb-4 group-hover:bg-accent/20 transition-colors">
                  <feature.icon className="w-5 h-5 text-accent" />
                </div>
                <h3 className="font-semibold text-foreground mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-muted-foreground">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </motion.div>

          {/* Privacy Notice */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.9 }}
            className="mt-16 flex items-center justify-center gap-2 text-sm text-muted-foreground"
          >
            <Lock className="w-4 h-4" />
            <span>
              Your data is private. No surveillance tools. No data sharing.
            </span>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default WelcomePage;

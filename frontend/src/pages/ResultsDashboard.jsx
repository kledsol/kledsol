import { useState, useEffect, useRef } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { TrustLensLogo, HeartLensIcon } from "@/components/custom/Logo";
import { TrustGauge, TrustIndexLabel } from "@/components/custom/TrustGauge";
import { useAnalysis } from "@/App";
import { getResults } from "@/lib/api";
import { toast } from "sonner";
import {
  Heart,
  Shield,
  Brain,
  MessageSquare,
  Activity,
  Target,
  Lightbulb,
  Users,
  Briefcase,
  Smartphone,
  Home,
  RefreshCw,
  ChevronRight,
} from "lucide-react";

// Animated counter hook
const useAnimatedCounter = (target, duration = 1200, start = false) => {
  const [value, setValue] = useState(0);
  const rafRef = useRef(null);

  useEffect(() => {
    if (!start) return;
    const startTime = performance.now();

    const tick = (now) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      setValue(Math.round(eased * target));
      if (progress < 1) {
        rafRef.current = requestAnimationFrame(tick);
      }
    };

    rafRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafRef.current);
  }, [target, duration, start]);

  return value;
};

// Suspicion Score color based on value
const getScoreColor = (score) => {
  if (score <= 30) return "#6EE7B7";
  if (score <= 60) return "#FCA311";
  if (score <= 80) return "#F97316";
  return "#FF4D6D";
};

// Circular progress indicator
const SuspicionScoreRing = ({ score, animatedScore, revealed }) => {
  const color = getScoreColor(score);
  const radius = 90;
  const circumference = 2 * Math.PI * radius;
  const progress = revealed ? (animatedScore / 100) * circumference : 0;

  return (
    <div className="relative w-[240px] h-[240px] mx-auto" data-testid="suspicion-score-ring">
      <svg viewBox="0 0 200 200" className="w-full h-full -rotate-90">
        {/* Background ring */}
        <circle
          cx="100" cy="100" r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.08)"
          strokeWidth="8"
        />
        {/* Progress ring */}
        <circle
          cx="100" cy="100" r={radius}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={circumference - progress}
          style={{ transition: "stroke-dashoffset 1.2s cubic-bezier(0.22, 1, 0.36, 1), stroke 0.3s" }}
        />
      </svg>
      {/* Score number in center */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span
          className="text-7xl font-light"
          style={{ fontFamily: "Fraunces, serif", color }}
          data-testid="suspicion-score-value"
        >
          {animatedScore}
        </span>
        <span className="text-sm text-muted-foreground mt-1">/100</span>
      </div>
    </div>
  );
};

const ResultsDashboard = () => {
  const { sessionId, resetAnalysis } = useAnalysis();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [results, setResults] = useState(null);
  const [revealStage, setRevealStage] = useState(0);
  // Stages: 0=loading, 1=transition, 2=suspicion-score, 3=hearts, 4=diagnosis, 5=patterns, 6=perspective, 7=comparison, 8=context, 9=actions, 10=complete

  useEffect(() => {
    if (!sessionId) {
      toast.error("No session found");
      navigate("/");
      return;
    }
    fetchResults();
  }, [sessionId]);

  const fetchResults = async () => {
    try {
      const data = await getResults(sessionId);
      setResults(data);
      setLoading(false);
      // Start reveal sequence
      startRevealSequence();
    } catch (e) {
      toast.error("Failed to load results");
      navigate("/");
    }
  };

  const startRevealSequence = () => {
    setTimeout(() => setRevealStage(1), 100);
    setTimeout(() => setRevealStage(2), 2000);   // Suspicion Score
    setTimeout(() => setRevealStage(3), 4500);   // Hearts
    setTimeout(() => setRevealStage(4), 6000);   // Diagnosis
    setTimeout(() => setRevealStage(5), 7200);   // Patterns
    setTimeout(() => setRevealStage(6), 8200);   // Perspective
    setTimeout(() => setRevealStage(7), 9200);   // Comparison
    setTimeout(() => setRevealStage(8), 10000);  // Context
    setTimeout(() => setRevealStage(9), 10800);  // Actions
    setTimeout(() => setRevealStage(10), 11500); // Complete
  };

  const handleStartOver = () => {
    resetAnalysis();
    navigate("/");
  };

  const getStabilityLabel = (hearts) => {
    if (hearts >= 4) return "Stable";
    if (hearts >= 3) return "Noticeable strain";
    if (hearts >= 2) return "Significant relationship stress";
    return "Severe trust disruption";
  };

  const getSecondaryPattern = (hypotheses) => {
    if (!hypotheses) return null;
    const sorted = Object.entries(hypotheses).sort(([, a], [, b]) => b - a);
    if (sorted.length > 1 && sorted[1][1] > 0.2) {
      return sorted[1][0].replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
    }
    return null;
  };

  const contextIcons = {
    workplace: Briefcase,
    digital: Smartphone,
    social: Users,
  };

  // Suspicion score animated counter — hook must be at component level
  const suspicionTarget = results?.suspicion_score ?? 0;
  const animatedSuspicionScore = useAnimatedCounter(suspicionTarget, 1200, revealStage >= 2);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0B132B] flex items-center justify-center">
        <div className="text-center">
          <HeartLensIcon size={80} animate />
          <p className="mt-6 text-muted-foreground">Loading analysis...</p>
        </div>
      </div>
    );
  }

  if (!results) return null;

  const secondaryPattern = getSecondaryPattern(results.hypotheses);

  return (
    <div className="min-h-screen bg-[#0B132B]">
      {/* Header - Always visible */}
      <header className="glass border-b border-white/10 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/">
            <TrustLensLogo size="md" />
          </Link>
          {revealStage >= 9 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <Button
                variant="outline"
                onClick={handleStartOver}
                className="border-white/20 text-white hover:bg-white/5 rounded-full"
                data-testid="start-over-btn"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                New Analysis
              </Button>
            </motion.div>
          )}
        </div>
      </header>

      <main className="container mx-auto px-6 py-12 max-w-4xl">
        <AnimatePresence mode="wait">
          {/* Stage 1: Transition Message */}
          {revealStage === 1 && (
            <motion.div
              key="transition"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="min-h-[60vh] flex flex-col items-center justify-center text-center"
            >
              <HeartLensIcon size={100} animate />
              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="mt-8 text-xl text-muted-foreground"
              >
                Your relationship signals have been carefully analyzed.
              </motion.p>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.8 }}
                className="mt-6"
              >
                <div className="w-48 h-1 bg-white/10 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: "100%" }}
                    transition={{ duration: 1.5, ease: "easeInOut" }}
                    className="h-full bg-[#3DD9C5]"
                  />
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Progressive Reveal Content */}
        {revealStage >= 2 && (
          <div className="space-y-12">
            {/* Stage 2: Suspicion Score Reveal */}
            <motion.section
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-center py-8"
              data-testid="suspicion-score-section"
            >
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="text-sm uppercase tracking-widest text-muted-foreground mb-8 font-mono"
              >
                TrustLens Suspicion Score
              </motion.p>

              <SuspicionScoreRing
                score={results.suspicion_score ?? 0}
                animatedScore={animatedSuspicionScore}
                revealed={revealStage >= 2}
              />

              <motion.p
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.4 }}
                className="mt-6 text-2xl font-light"
                style={{
                  fontFamily: "Fraunces, serif",
                  color: getScoreColor(results.suspicion_score ?? 0),
                }}
                data-testid="suspicion-score-label"
              >
                {results.suspicion_label ?? "Low Signal"}
              </motion.p>

              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.8 }}
                className="mt-6 text-sm text-muted-foreground max-w-md mx-auto leading-relaxed"
              >
                This score reflects patterns detected in your answers.
                It does not prove anything, but it highlights signals that may deserve attention.
              </motion.p>
            </motion.section>

            {/* Stage 3: Emotional Stability Reveal */}
            {revealStage >= 3 && (
            <motion.section
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-center py-8"
            >
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="text-sm uppercase tracking-wider text-muted-foreground mb-6"
              >
                Relationship Stability
              </motion.p>
              
              <div className="flex justify-center gap-3 mb-6">
                {[...Array(4)].map((_, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ 
                      opacity: 1, 
                      scale: 1,
                    }}
                    transition={{ 
                      delay: 0.4 + i * 0.3,
                      type: "spring",
                      stiffness: 200,
                    }}
                  >
                    <Heart
                      className={`w-12 h-12 ${
                        i < results.stability_hearts
                          ? "fill-[#FF4D6D] text-[#FF4D6D]"
                          : "fill-none text-white/20"
                      }`}
                    />
                  </motion.div>
                ))}
              </div>
              
              <motion.p
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.6 }}
                className={`text-2xl font-light ${
                  results.stability_hearts >= 3 ? "text-[#6EE7B7]" :
                  results.stability_hearts >= 2 ? "text-[#FCA311]" : "text-[#FF4D6D]"
                }`}
                style={{ fontFamily: 'Fraunces, serif' }}
              >
                {getStabilityLabel(results.stability_hearts)}
              </motion.p>
            </motion.section>
            )}

            {/* Stage 4: Main Diagnosis Block */}
            {revealStage >= 4 && (
              <motion.section
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
              >
                <Card className="glass-card rounded-3xl border-[#3DD9C5]/20 overflow-hidden">
                  <CardContent className="p-0">
                    <div className="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-white/10">
                      {/* Trust Disruption Index */}
                      <div className="p-8 text-center">
                        <p className="text-sm text-muted-foreground mb-4">Trust Disruption Index</p>
                        <div className="flex justify-center mb-4">
                          <TrustGauge value={results.trust_disruption_index} />
                        </div>
                        <TrustIndexLabel value={results.trust_disruption_index} />
                      </div>
                      
                      {/* Confidence Level */}
                      <div className="p-8 text-center flex flex-col justify-center">
                        <p className="text-sm text-muted-foreground mb-4">Confidence Level</p>
                        <div className="flex items-center justify-center gap-3 mb-2">
                          <div className={`w-4 h-4 rounded-full ${
                            results.confidence_level === "high" ? "bg-[#6EE7B7]" :
                            results.confidence_level === "moderate" ? "bg-[#FCA311]" : "bg-white/30"
                          }`} />
                          <span className="text-3xl font-light text-[#E6EDF3] capitalize" style={{ fontFamily: 'Fraunces, serif' }}>
                            {results.confidence_level}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Based on {results.questions_answered} signals analyzed
                        </p>
                      </div>
                      
                      {/* Narrative Consistency */}
                      <div className="p-8 text-center flex flex-col justify-center">
                        <p className="text-sm text-muted-foreground mb-4">Narrative Consistency</p>
                        <div className="text-4xl font-light text-[#E6EDF3] mb-2" style={{ fontFamily: 'Fraunces, serif' }}>
                          {results.narrative_consistency.toFixed(0)}
                          <span className="text-lg text-muted-foreground">%</span>
                        </div>
                        <Progress value={results.narrative_consistency} className="h-1 max-w-[120px] mx-auto" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.section>
            )}

            {/* Stage 5: Dominant Pattern Reveal */}
            {revealStage >= 5 && (
              <motion.section
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
                className="text-center py-8"
              >
                <p className="text-sm uppercase tracking-wider text-muted-foreground mb-6">
                  Behavioral Pattern Analysis
                </p>
                
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.2 }}
                  className="mb-4"
                >
                  <p className="text-sm text-muted-foreground mb-2">Dominant Pattern</p>
                  <p className="text-3xl font-light text-[#FF4D6D]" style={{ fontFamily: 'Fraunces, serif' }}>
                    {results.dominant_pattern}
                  </p>
                </motion.div>
                
                {secondaryPattern && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 }}
                  >
                    <p className="text-sm text-muted-foreground mb-2">Secondary Pattern</p>
                    <p className="text-xl text-[#FCA311]" style={{ fontFamily: 'Fraunces, serif' }}>
                      {secondaryPattern}
                    </p>
                  </motion.div>
                )}
              </motion.section>
            )}

            {/* Stage 6: TrustLens Perspective */}
            {revealStage >= 6 && (
              <motion.section
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
              >
                <Card className="glass-card rounded-3xl border-[#3DD9C5]/30">
                  <CardContent className="p-10">
                    <div className="flex flex-col items-center text-center">
                      <HeartLensIcon size={48} />
                      <h3 className="text-xl font-light text-[#E6EDF3] mt-6 mb-6" style={{ fontFamily: 'Fraunces, serif' }}>
                        TrustLens Perspective
                      </h3>
                      <p className="text-muted-foreground leading-relaxed max-w-2xl text-lg">
                        {results.trustlens_perspective}
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </motion.section>
            )}

            {/* Stage 7: Pattern Comparison Insight */}
            {revealStage >= 7 && results.pattern_statistics && (
              <motion.section
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
              >
                <Card className="glass-card rounded-2xl">
                  <CardHeader className="text-center pb-2">
                    <CardTitle className="text-base text-muted-foreground font-normal">
                      In similar situations analyzed by TrustLens
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-4">
                    <div className="grid grid-cols-3 gap-6 text-center">
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        className="p-4"
                      >
                        <p className="text-4xl font-light text-[#FF4D6D] mb-2" style={{ fontFamily: 'Fraunces, serif' }}>
                          {results.pattern_statistics.confirmed_issues}%
                        </p>
                        <p className="text-sm text-muted-foreground">
                          later confirmed<br />relationship issues
                        </p>
                      </motion.div>
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="p-4"
                      >
                        <p className="text-4xl font-light text-[#FCA311] mb-2" style={{ fontFamily: 'Fraunces, serif' }}>
                          {results.pattern_statistics.relationship_conflict}%
                        </p>
                        <p className="text-sm text-muted-foreground">
                          reported severe<br />conflict (no infidelity)
                        </p>
                      </motion.div>
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="p-4"
                      >
                        <p className="text-4xl font-light text-[#6EE7B7] mb-2" style={{ fontFamily: 'Fraunces, serif' }}>
                          {results.pattern_statistics.resolved_positively}%
                        </p>
                        <p className="text-sm text-muted-foreground">
                          resolved<br />positively
                        </p>
                      </motion.div>
                    </div>
                  </CardContent>
                </Card>
              </motion.section>
            )}

            {/* Stage 8: Context Estimation */}
            {revealStage >= 8 && results.context_estimation && results.context_estimation.length > 0 && (
              <motion.section
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
              >
                <Card className="glass-card rounded-2xl">
                  <CardHeader className="text-center">
                    <CardTitle className="text-base text-muted-foreground font-normal">
                      Likely interaction contexts
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex justify-center gap-6 flex-wrap">
                      {results.context_estimation.map((context, i) => {
                        const IconComponent = context.includes("work") ? Briefcase :
                          context.includes("digital") ? Smartphone : Users;
                        return (
                          <motion.div
                            key={i}
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: i * 0.1 }}
                            className="flex flex-col items-center gap-2 p-4"
                          >
                            <div className="w-14 h-14 rounded-xl bg-[#3DD9C5]/10 flex items-center justify-center">
                              <IconComponent className="w-7 h-7 text-[#3DD9C5]" />
                            </div>
                            <p className="text-sm text-[#E6EDF3] capitalize">
                              {context.replace(/_/g, " ")}
                            </p>
                          </motion.div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
              </motion.section>
            )}

            {/* Stage 9: Clarity Actions */}
            {revealStage >= 9 && (
              <motion.section
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
              >
                <Card className="glass-card rounded-2xl">
                  <CardHeader className="text-center">
                    <CardTitle className="flex items-center justify-center gap-2 text-lg text-[#E6EDF3]">
                      <Lightbulb className="w-5 h-5 text-[#3DD9C5]" />
                      What You Can Do Next
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
                      {results.clarity_actions?.slice(0, 4).map((action, i) => (
                        <motion.div
                          key={i}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: i * 0.1 }}
                          className="flex items-start gap-3 p-4 rounded-xl bg-white/5"
                        >
                          <div className="w-6 h-6 rounded-full bg-[#3DD9C5]/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                            <span className="text-xs font-mono text-[#3DD9C5]">{i + 1}</span>
                          </div>
                          <p className="text-sm text-[#E6EDF3]">{action}</p>
                        </motion.div>
                      ))}
                    </div>

                    <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4 border-t border-white/10">
                      <Button
                        onClick={() => navigate("/coach")}
                        className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-6 py-5 btn-glow"
                        data-testid="coach-btn"
                      >
                        <MessageSquare className="w-5 h-5 mr-2" />
                        Start Conversation Coach
                        <ChevronRight className="w-5 h-5 ml-2" />
                      </Button>
                      <Button
                        onClick={() => navigate("/pulse")}
                        variant="outline"
                        className="border-[#FF4D6D]/50 text-[#FF4D6D] hover:bg-[#FF4D6D]/10 rounded-full px-6 py-5"
                        data-testid="pulse-btn"
                      >
                        <Heart className="w-5 h-5 mr-2" />
                        Track Relationship Pulse
                      </Button>
                      <Button
                        onClick={() => navigate("/mirror")}
                        variant="outline"
                        className="border-white/20 text-white hover:bg-white/5 rounded-full px-6 py-5"
                        data-testid="mirror-btn"
                      >
                        <Users className="w-5 h-5 mr-2" />
                        Mirror Mode
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.section>
            )}

            {/* Stage 10: Closing Support Note */}
            {revealStage >= 10 && (
              <motion.section
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 1 }}
                className="text-center py-12"
              >
                <div className="max-w-xl mx-auto">
                  <Shield className="w-8 h-8 text-[#3DD9C5] mx-auto mb-6" />
                  <p className="text-muted-foreground leading-relaxed mb-2">
                    Uncertainty can be emotionally difficult.
                  </p>
                  <p className="text-muted-foreground leading-relaxed">
                    The purpose of this analysis is not to accuse, but to help you understand what may be happening.
                  </p>
                </div>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  className="mt-10"
                >
                  <Button
                    onClick={() => navigate("/")}
                    variant="ghost"
                    className="text-muted-foreground hover:text-white hover:bg-white/5 rounded-full"
                  >
                    <Home className="w-4 h-4 mr-2" />
                    Return Home
                  </Button>
                </motion.div>
              </motion.section>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default ResultsDashboard;

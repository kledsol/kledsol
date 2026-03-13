import { useState, useEffect, useRef } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { TrustLensLogo, HeartLensIcon } from "@/components/custom/Logo";
import { TrustGauge, TrustIndexLabel } from "@/components/custom/TrustGauge";
import { useAnalysis } from "@/App";
import { getResults, getTimelineHistory, saveTimelineEntry, createSharedReport, createMirrorSession, getMirrorStatus, consentMirror, linkAnalysis, getSignalTrends, contributeCase } from "@/lib/api";
import { toast } from "sonner";
import AuthModal from "@/components/custom/AuthModal";
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
  AlertTriangle,
  TrendingUp,
  Share2,
  Copy,
  Check,
  Link2,
  Lock,
  BarChart3,
  TrendingDown,
  Save,
  Globe,
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

// Analysis sequence steps
const ANALYSIS_STEPS = [
  { text: "Analyzing behavioral signals...", icon: Activity },
  { text: "Comparing with relationship patterns...", icon: Brain },
  { text: "Checking perception consistency...", icon: Target },
  { text: "Final TrustLens Assessment", icon: Shield },
];

const AnalysisSequence = ({ onComplete }) => {
  const [step, setStep] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const stepDuration = 1200;
    const totalSteps = ANALYSIS_STEPS.length;

    const interval = setInterval(() => {
      setStep((s) => {
        if (s >= totalSteps - 1) {
          clearInterval(interval);
          setTimeout(onComplete, 800);
          return s;
        }
        return s + 1;
      });
    }, stepDuration);

    // Progress bar animation
    const progressInterval = setInterval(() => {
      setProgress((p) => Math.min(p + 1.5, 100));
    }, 50);

    return () => {
      clearInterval(interval);
      clearInterval(progressInterval);
    };
  }, [onComplete]);

  const CurrentIcon = ANALYSIS_STEPS[step].icon;

  return (
    <motion.div
      key="analysis-sequence"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="min-h-[60vh] flex flex-col items-center justify-center text-center px-4"
      data-testid="analysis-sequence"
    >
      <motion.div
        key={step}
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
        className="w-16 h-16 rounded-2xl bg-[#3DD9C5]/10 flex items-center justify-center mb-8"
      >
        <CurrentIcon className="w-8 h-8 text-[#3DD9C5]" />
      </motion.div>

      <AnimatePresence mode="wait">
        <motion.p
          key={step}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -12 }}
          transition={{ duration: 0.3 }}
          className="text-xl sm:text-2xl text-[#E6EDF3] font-light mb-8"
          style={{ fontFamily: "Fraunces, serif" }}
        >
          {ANALYSIS_STEPS[step].text}
        </motion.p>
      </AnimatePresence>

      {/* Step indicators */}
      <div className="flex gap-3 mb-8">
        {ANALYSIS_STEPS.map((_, i) => (
          <div
            key={i}
            className={`w-2 h-2 rounded-full transition-all duration-500 ${
              i <= step ? "bg-[#3DD9C5] scale-110" : "bg-white/15"
            }`}
          />
        ))}
      </div>

      {/* Progress bar */}
      <div className="w-56 h-1 bg-white/10 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-[#3DD9C5] rounded-full"
          style={{ width: `${progress}%` }}
        />
      </div>
    </motion.div>
  );
};

// Simple line chart for timeline
const TimelineChart = ({ entries }) => {
  if (!entries || entries.length < 2) return null;

  const maxScore = 100;
  const chartH = 140;
  const chartW = entries.length > 1 ? 100 : 50; // percentage width
  const points = entries.map((e, i) => ({
    x: (i / (entries.length - 1)) * chartW,
    y: chartH - (e.score / maxScore) * chartH,
    ...e,
  }));
  const pathD = points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`)
    .join(" ");

  return (
    <div className="w-full" data-testid="timeline-chart">
      <svg
        viewBox={`-10 -10 ${chartW + 20} ${chartH + 40}`}
        className="w-full h-auto max-h-[180px]"
        preserveAspectRatio="xMidYMid meet"
      >
        {/* Grid lines */}
        {[0, 25, 50, 75, 100].map((v) => (
          <line
            key={v}
            x1="0" x2={chartW}
            y1={chartH - (v / 100) * chartH}
            y2={chartH - (v / 100) * chartH}
            stroke="rgba(255,255,255,0.06)"
            strokeDasharray="2"
          />
        ))}
        {/* Line */}
        <path d={pathD} fill="none" stroke="#3DD9C5" strokeWidth="2" strokeLinejoin="round" />
        {/* Dots and labels */}
        {points.map((p, i) => (
          <g key={i}>
            <circle cx={p.x} cy={p.y} r="4" fill="#3DD9C5" />
            <text x={p.x} y={p.y - 10} textAnchor="middle" fill="#E6EDF3" fontSize="8" fontFamily="monospace">
              {p.score}
            </text>
            <text x={p.x} y={chartH + 16} textAnchor="middle" fill="#8899A6" fontSize="7" fontFamily="monospace">
              {p.date_display}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
};
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
  const [timelineHistory, setTimelineHistory] = useState([]);
  const [shareUrl, setShareUrl] = useState(null);
  const [sharing, setSharing] = useState(false);
  const [copied, setCopied] = useState(false);
  const [mirrorId, setMirrorId] = useState(null);
  const [mirrorInviteUrl, setMirrorInviteUrl] = useState(null);
  const [mirrorCreating, setMirrorCreating] = useState(false);
  const [mirrorConsented, setMirrorConsented] = useState(false);
  const [mirrorCopied, setMirrorCopied] = useState(false);
  const [mirrorStatus, setMirrorStatus] = useState(null);
  // For Partner B returning from analysis
  const [isMirrorPartner, setIsMirrorPartner] = useState(false);
  const [mirrorContext, setMirrorContext] = useState(null);
  // Auth & trend tracking
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem("trustlens_user"));
  const [analysisSaved, setAnalysisSaved] = useState(false);
  const [signalTrends, setSignalTrends] = useState(null);
  const [contributed, setContributed] = useState(false);
  const [contributingOutcome, setContributingOutcome] = useState(null);
  const [contributingLoading, setContributingLoading] = useState(false);
  // Stages: 0=loading, 1=analysis-sequence, 2=suspicion-score, 3=hearts, 4=diagnosis, 5=patterns, 6=signal-strength, 7=perception, 8=perspective, 9=comparison, 10=timeline, 11=actions, 12=complete

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

      // Check if this session belongs to a mirror
      if (data.mirror_id) {
        setMirrorId(data.mirror_id);
        if (data.mirror_role === "b") {
          setIsMirrorPartner(true);
          setMirrorContext({ mirrorId: data.mirror_id, role: "b" });
        } else if (data.mirror_role === "a") {
          // Partner A - check if they already have an invite
          setMirrorInviteUrl(`${window.location.origin}/mirror-invite/${data.mirror_id}`);
          try {
            const ms = await getMirrorStatus(data.mirror_id);
            setMirrorStatus(ms);
            setMirrorConsented(ms.partner_a_consented);
          } catch {}
        }
      }

      // Also check sessionStorage for Partner B context
      try {
        const stored = JSON.parse(sessionStorage.getItem("trustlens_mirror") || "null");
        if (stored && stored.role === "b" && !data.mirror_id) {
          setIsMirrorPartner(true);
          setMirrorContext(stored);
          setMirrorId(stored.mirrorId);
        }
      } catch {}

      // Start the dramatic analysis sequence
      setTimeout(() => setRevealStage(1), 100);
      // Save score to timeline
      try {
        await saveTimelineEntry(data.suspicion_score, data.suspicion_label);
        const history = await getTimelineHistory();
        setTimelineHistory(history.entries || []);
      } catch (_) { /* timeline is optional */ }

      // Load signal trends for logged-in users
      if (localStorage.getItem("trustlens_token")) {
        try {
          const trends = await getSignalTrends(sessionId);
          if (trends.has_previous) {
            setSignalTrends(trends);
          }
        } catch { /* not logged in or no previous */ }
      }
    } catch (e) {
      toast.error("Failed to load results");
      navigate("/");
    }
  };

  const handleAnalysisComplete = () => {
    // After analysis sequence, start progressive reveal
    setRevealStage(2);
    setTimeout(() => setRevealStage(3), 2500);   // Hearts
    setTimeout(() => setRevealStage(4), 4000);   // Diagnosis
    setTimeout(() => setRevealStage(5), 5200);   // Patterns
    setTimeout(() => setRevealStage(6), 6200);   // Signal Strength
    setTimeout(() => setRevealStage(7), 7200);   // Perception
    setTimeout(() => setRevealStage(8), 8200);   // Perspective
    setTimeout(() => setRevealStage(9), 9200);   // Comparison
    setTimeout(() => setRevealStage(10), 10000); // Timeline
    setTimeout(() => setRevealStage(11), 10800); // Actions
    setTimeout(() => setRevealStage(12), 11500); // Complete
  };

  const handleStartOver = () => {
    resetAnalysis();
    navigate("/");
  };

  const handleShare = async () => {
    if (shareUrl) {
      await copyToClipboard(shareUrl);
      return;
    }
    setSharing(true);
    try {
      const { report_id } = await createSharedReport({
        suspicion_score: results.suspicion_score,
        suspicion_label: results.suspicion_label,
        pattern_comparison_pct: results.pattern_comparison_pct,
        pattern_statistics: results.pattern_statistics,
        perception_consistency: results.perception_consistency,
        clarity_actions: results.clarity_actions,
        dominant_pattern: results.dominant_pattern,
        trustlens_perspective: results.trustlens_perspective,
      });
      const url = `${window.location.origin}/report/${report_id}`;
      setShareUrl(url);
      await copyToClipboard(url);
    } catch {
      toast.error("Failed to generate share link");
    } finally {
      setSharing(false);
    }
  };

  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const ta = document.createElement("textarea");
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
    }
    setCopied(true);
    toast.success("Link copied to clipboard");
    setTimeout(() => setCopied(false), 2000);
  };

  const handleCreateMirror = async () => {
    setMirrorCreating(true);
    try {
      const { mirror_id } = await createMirrorSession(sessionId);
      setMirrorId(mirror_id);
      const url = `${window.location.origin}/mirror-invite/${mirror_id}`;
      setMirrorInviteUrl(url);
    } catch {
      toast.error("Failed to create mirror session");
    } finally {
      setMirrorCreating(false);
    }
  };

  const handleMirrorConsent = async () => {
    const mid = mirrorId || mirrorContext?.mirrorId;
    if (!mid) return;
    try {
      const result = await consentMirror(mid, sessionId);
      setMirrorConsented(true);
      toast.success("Consent recorded");
      if (result.report_ready) {
        navigate(`/dual-report/${mid}`);
      }
    } catch {
      toast.error("Failed to record consent");
    }
  };

  const copyMirrorLink = async () => {
    if (!mirrorInviteUrl) return;
    try {
      await navigator.clipboard.writeText(mirrorInviteUrl);
    } catch {
      const ta = document.createElement("textarea");
      ta.value = mirrorInviteUrl;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
    }
    setMirrorCopied(true);
    toast.success("Invite link copied");
    setTimeout(() => setMirrorCopied(false), 2000);
  };

  const handleSaveAnalysis = async () => {
    if (!isLoggedIn) {
      setShowAuthModal(true);
      return;
    }
    try {
      await linkAnalysis(sessionId);
      setAnalysisSaved(true);
      toast.success("Analysis saved to your history");
      // Load trends now
      try {
        const trends = await getSignalTrends(sessionId);
        if (trends.has_previous) setSignalTrends(trends);
      } catch { /* first analysis */ }
    } catch {
      toast.error("Failed to save analysis");
    }
  };

  const handleAuthSuccess = async () => {
    setShowAuthModal(false);
    setIsLoggedIn(true);
    // Automatically save the current analysis
    try {
      await linkAnalysis(sessionId);
      setAnalysisSaved(true);
      toast.success("Account created and analysis saved");
      try {
        const trends = await getSignalTrends(sessionId);
        if (trends.has_previous) setSignalTrends(trends);
      } catch { /* first analysis */ }
    } catch { /* already linked */ }
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
          {revealStage >= 11 && (
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
          {/* Stage 1: Dramatic Analysis Sequence */}
          {revealStage === 1 && (
            <AnalysisSequence onComplete={handleAnalysisComplete} />
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

            {/* Stage 6: Signal Strength Summary */}
            {revealStage >= 6 && results.signal_strength_summary && (
              <motion.section
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
                data-testid="signal-strength-section"
              >
                <Card className="glass-card rounded-2xl">
                  <CardHeader className="text-center pb-2">
                    <CardTitle className="flex items-center justify-center gap-2 text-lg text-[#E6EDF3]">
                      <BarChart3 className="w-5 h-5 text-[#3DD9C5]" />
                      Signal Strength Summary
                    </CardTitle>
                    <p className="text-sm text-muted-foreground mt-1">
                      The behavioral patterns that most influenced your analysis
                    </p>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Strong Signals */}
                    {results.signal_strength_summary.strong?.length > 0 && (
                      <div data-testid="strong-signals">
                        <div className="flex items-center gap-2 mb-3">
                          <div className="h-2 w-2 rounded-full bg-[#FF4D6D]" />
                          <span className="text-xs font-mono tracking-wider text-[#FF4D6D]">STRONG SIGNALS</span>
                        </div>
                        <div className="space-y-2">
                          {results.signal_strength_summary.strong.map((s, i) => {
                            const trend = signalTrends?.trends?.[s.key];
                            return (
                              <motion.div
                                key={s.key}
                                initial={{ opacity: 0, x: -15 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.1 * i }}
                                className="p-4 rounded-xl bg-[#FF4D6D]/5 border border-[#FF4D6D]/15"
                              >
                                <div className="flex items-center justify-between mb-1.5">
                                  <span className="text-sm font-medium text-[#E6EDF3]">{s.name}</span>
                                  <div className="flex items-center gap-2">
                                    <span className="text-xs font-mono text-[#FF4D6D]">{Math.round(s.intensity * 100)}%</span>
                                    {trend && trend.delta !== 0 && (
                                      <span className={`text-[10px] font-mono flex items-center gap-0.5 ${trend.delta > 0 ? "text-[#FF4D6D]" : "text-[#6EE7B7]"}`} data-testid={`trend-${s.key}`}>
                                        {trend.delta > 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                                        {trend.delta > 0 ? "+" : ""}{trend.delta}%
                                      </span>
                                    )}
                                  </div>
                                </div>
                                <div className="h-1.5 bg-white/5 rounded-full overflow-hidden mb-2">
                                  <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${s.intensity * 100}%` }}
                                    transition={{ duration: 0.8, delay: 0.2 + 0.1 * i }}
                                    className="h-full rounded-full bg-[#FF4D6D]"
                                  />
                                </div>
                                <p className="text-xs text-muted-foreground">{s.desc}</p>
                              </motion.div>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Moderate Signals */}
                    {results.signal_strength_summary.moderate?.length > 0 && (
                      <div data-testid="moderate-signals">
                        <div className="flex items-center gap-2 mb-3">
                          <div className="h-2 w-2 rounded-full bg-[#FCA311]" />
                          <span className="text-xs font-mono tracking-wider text-[#FCA311]">MODERATE SIGNALS</span>
                        </div>
                        <div className="space-y-2">
                          {results.signal_strength_summary.moderate.map((s, i) => {
                            const trend = signalTrends?.trends?.[s.key];
                            return (
                              <motion.div
                                key={s.key}
                                initial={{ opacity: 0, x: -15 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.1 * i }}
                                className="p-4 rounded-xl bg-[#FCA311]/5 border border-[#FCA311]/15"
                              >
                                <div className="flex items-center justify-between mb-1.5">
                                  <span className="text-sm font-medium text-[#E6EDF3]">{s.name}</span>
                                  <div className="flex items-center gap-2">
                                    <span className="text-xs font-mono text-[#FCA311]">{Math.round(s.intensity * 100)}%</span>
                                    {trend && trend.delta !== 0 && (
                                      <span className={`text-[10px] font-mono flex items-center gap-0.5 ${trend.delta > 0 ? "text-[#FF4D6D]" : "text-[#6EE7B7]"}`} data-testid={`trend-${s.key}`}>
                                        {trend.delta > 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                                        {trend.delta > 0 ? "+" : ""}{trend.delta}%
                                      </span>
                                    )}
                                  </div>
                                </div>
                                <div className="h-1.5 bg-white/5 rounded-full overflow-hidden mb-2">
                                  <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${s.intensity * 100}%` }}
                                    transition={{ duration: 0.8, delay: 0.2 + 0.1 * i }}
                                    className="h-full rounded-full bg-[#FCA311]"
                                  />
                                </div>
                                <p className="text-xs text-muted-foreground">{s.desc}</p>
                              </motion.div>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Weak Signals */}
                    {results.signal_strength_summary.weak?.length > 0 && (
                      <div data-testid="weak-signals">
                        <div className="flex items-center gap-2 mb-3">
                          <div className="h-2 w-2 rounded-full bg-[#6EE7B7]" />
                          <span className="text-xs font-mono tracking-wider text-[#6EE7B7]">WEAK SIGNALS</span>
                        </div>
                        <div className="space-y-2">
                          {results.signal_strength_summary.weak.map((s, i) => {
                            const trend = signalTrends?.trends?.[s.key];
                            return (
                              <motion.div
                                key={s.key}
                                initial={{ opacity: 0, x: -15 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: 0.1 * i }}
                                className="p-3 rounded-xl bg-white/5 border border-white/10"
                              >
                                <div className="flex items-center justify-between mb-1">
                                  <span className="text-sm text-[#E6EDF3]">{s.name}</span>
                                  <div className="flex items-center gap-2">
                                    <span className="text-xs font-mono text-[#6EE7B7]">{Math.round(s.intensity * 100)}%</span>
                                    {trend && trend.delta !== 0 && (
                                      <span className={`text-[10px] font-mono flex items-center gap-0.5 ${trend.delta > 0 ? "text-[#FF4D6D]" : "text-[#6EE7B7]"}`} data-testid={`trend-${s.key}`}>
                                        {trend.delta > 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                                        {trend.delta > 0 ? "+" : ""}{trend.delta}%
                                      </span>
                                    )}
                                  </div>
                                </div>
                                <div className="h-1 bg-white/5 rounded-full overflow-hidden mb-1.5">
                                  <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${s.intensity * 100}%` }}
                                    transition={{ duration: 0.8, delay: 0.2 + 0.1 * i }}
                                    className="h-full rounded-full bg-[#6EE7B7]"
                                  />
                                </div>
                                <p className="text-xs text-muted-foreground">{s.desc}</p>
                              </motion.div>
                            );
                          })}
                        </div>
                      </div>
                    )}

                    {/* Disclaimer */}
                    <div className="pt-4 border-t border-white/10">
                      <p className="text-xs text-muted-foreground text-center leading-relaxed">
                        These signals reflect patterns observed in your responses. They describe perceptions,
                        not conclusions. Each signal's strength indicates how prominently it appeared across your answers.
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </motion.section>
            )}

            {/* Stage 7: Perception Consistency Check */}
            {revealStage >= 7 && results.perception_consistency && (
              <motion.section
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
                data-testid="perception-consistency-section"
              >
                <Card className="glass-card rounded-2xl border-[#FCA311]/20">
                  <CardContent className="p-8">
                    <div className="flex items-start gap-4">
                      <div className="w-10 h-10 rounded-lg bg-[#FCA311]/10 flex items-center justify-center flex-shrink-0 mt-1">
                        <AlertTriangle className="w-5 h-5 text-[#FCA311]" />
                      </div>
                      <div>
                        <h3 className="text-base font-medium text-[#E6EDF3] mb-3">Perception Consistency Check</h3>
                        <p className="text-sm text-muted-foreground leading-relaxed mb-4">
                          {results.perception_consistency.insight}
                        </p>
                        {results.perception_consistency.has_inconsistencies && results.perception_consistency.inconsistencies.map((item, i) => (
                          <motion.p
                            key={i}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.2 + i * 0.15 }}
                            className="text-sm text-[#FCA311]/80 mb-2 pl-4 border-l-2 border-[#FCA311]/30"
                          >
                            {item}
                          </motion.p>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.section>
            )}

            {/* Stage 8: TrustLens Perspective */}
            {revealStage >= 8 && (
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

            {/* Stage 9: Pattern Comparison (Case Database) */}
            {revealStage >= 9 && results.pattern_statistics && (
              <motion.section
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
                data-testid="pattern-comparison-section"
              >
                <Card className="glass-card rounded-2xl">
                  <CardHeader className="text-center pb-2">
                    <CardTitle className="text-lg text-[#E6EDF3] font-light" style={{ fontFamily: "Fraunces, serif" }}>
                      Pattern Comparison
                    </CardTitle>
                    <p className="text-sm text-muted-foreground mt-2">
                      Your answers were compared with{" "}
                      <span className="text-[#E6EDF3]">{results.case_comparison?.total_cases || 300}</span>{" "}
                      documented relationship cases.
                    </p>
                  </CardHeader>
                  <CardContent className="pt-4">
                    {/* Case-based insights */}
                    {results.case_comparison?.insights?.length > 0 && (
                      <div className="space-y-3 mb-6">
                        {results.case_comparison.insights.map((insight, i) => (
                          <motion.div
                            key={i}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.2 + i * 0.15 }}
                            className="p-4 rounded-xl bg-white/5 text-sm text-[#E6EDF3] leading-relaxed"
                            data-testid={`case-insight-${i}`}
                          >
                            {insight}
                          </motion.div>
                        ))}
                      </div>
                    )}

                    {/* Outcome statistics from case database */}
                    <div className="grid grid-cols-3 gap-6 text-center">
                      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="p-4">
                        <p className="text-4xl font-light text-[#FF4D6D] mb-2" style={{ fontFamily: "Fraunces, serif" }}>
                          {results.pattern_statistics.confirmed_issues}%
                        </p>
                        <p className="text-sm text-muted-foreground">confirmed<br />relationship issues</p>
                      </motion.div>
                      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }} className="p-4">
                        <p className="text-4xl font-light text-[#FCA311] mb-2" style={{ fontFamily: "Fraunces, serif" }}>
                          {results.pattern_statistics.relationship_conflict}%
                        </p>
                        <p className="text-sm text-muted-foreground">unresolved<br />conflict</p>
                      </motion.div>
                      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }} className="p-4">
                        <p className="text-4xl font-light text-[#6EE7B7] mb-2" style={{ fontFamily: "Fraunces, serif" }}>
                          {results.pattern_statistics.resolved_positively}%
                        </p>
                        <p className="text-sm text-muted-foreground">resolved<br />positively</p>
                      </motion.div>
                    </div>

                    {/* Similar cases badge */}
                    {results.case_comparison?.similar_case_count > 0 && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.8 }}
                        className="mt-4 flex flex-wrap items-center justify-center gap-2"
                      >
                        <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#3DD9C5]/10 text-xs text-[#3DD9C5] font-mono">
                          {results.case_comparison.similar_case_count} similar cases found
                        </span>
                        {results.case_comparison.demographic_filtered && results.case_comparison.demographic_label && (
                          <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#FCA311]/10 text-xs text-[#FCA311] font-mono" data-testid="demographic-badge">
                            Filtered: {results.case_comparison.demographic_label}
                          </span>
                        )}
                      </motion.div>
                    )}

                    {/* Disclaimer */}
                    <motion.p
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.9 }}
                      className="text-xs text-muted-foreground text-center mt-6 pt-4 border-t border-white/10 leading-relaxed"
                    >
                      This analysis highlights similarities with known relationship situations.
                      It does not prove or confirm infidelity.
                    </motion.p>
                  </CardContent>
                </Card>
              </motion.section>
            )}

            {/* Stage 10: Relationship Timeline */}
            {revealStage >= 10 && timelineHistory.length >= 1 && (
              <motion.section
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
                data-testid="relationship-timeline-section"
              >
                <Card className="glass-card rounded-2xl">
                  <CardHeader className="text-center">
                    <CardTitle className="flex items-center justify-center gap-2 text-lg text-[#E6EDF3]">
                      <TrendingUp className="w-5 h-5 text-[#3DD9C5]" />
                      Relationship Timeline
                    </CardTitle>
                    <p className="text-sm text-muted-foreground mt-1">
                      Track how your suspicion score evolves over time
                    </p>
                  </CardHeader>
                  <CardContent>
                    {timelineHistory.length >= 2 ? (
                      <TimelineChart entries={timelineHistory} />
                    ) : (
                      <div className="text-center py-6">
                        <div className="flex items-center justify-center gap-6 mb-4">
                          <div className="text-center">
                            <p className="text-3xl font-light text-[#3DD9C5]" style={{ fontFamily: "Fraunces, serif" }}>
                              {timelineHistory[0]?.score ?? results.suspicion_score}
                            </p>
                            <p className="text-xs text-muted-foreground mt-1">{timelineHistory[0]?.date_display ?? "Today"}</p>
                          </div>
                          <div className="flex-1 h-px bg-white/10 max-w-[100px]" />
                          <div className="text-center opacity-30">
                            <p className="text-3xl font-light text-white/40" style={{ fontFamily: "Fraunces, serif" }}>?</p>
                            <p className="text-xs text-muted-foreground mt-1">Next check</p>
                          </div>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Run another analysis later to see your relationship trend
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </motion.section>
            )}

            {/* Stage 11: Clarity Actions */}
            {revealStage >= 11 && (
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
                        Conversation Coach
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
                    </div>
                  </CardContent>
                </Card>
              </motion.section>
            )}

            {/* Mirror Invite Section - Partner A creates, Partner B consents */}
            {revealStage >= 11 && (
              <motion.section
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.2 }}
                data-testid="mirror-invite-section"
              >
                <Card className="glass-card rounded-2xl border-[#3DD9C5]/20">
                  <CardContent className="p-8">
                    <div className="flex flex-col items-center text-center">
                      <div className="relative inline-block mb-6">
                        <div className="w-14 h-14 rounded-full bg-[#3DD9C5]/10 flex items-center justify-center">
                          <Users className="w-7 h-7 text-[#3DD9C5]" />
                        </div>
                      </div>

                      {/* Partner B flow: show consent prompt */}
                      {isMirrorPartner && !mirrorConsented && (
                        <>
                          <h3 className="text-lg font-light text-[#E6EDF3] mb-3" style={{ fontFamily: "Fraunces, serif" }}>
                            You were invited to a Mirror Analysis
                          </h3>
                          <p className="text-sm text-muted-foreground mb-6 max-w-md leading-relaxed">
                            Your partner has also completed a TrustLens analysis. Would you like to compare perspectives?
                            Your results will only be shared if you explicitly consent.
                          </p>
                          <div className="flex flex-col sm:flex-row gap-3">
                            <Button
                              onClick={handleMirrorConsent}
                              className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-6 py-5 btn-glow"
                              data-testid="partner-b-consent-btn"
                            >
                              <Lock className="w-4 h-4 mr-2" />
                              I Consent to Compare Perspectives
                            </Button>
                            <Button
                              variant="outline"
                              onClick={() => navigate(`/dual-report/${mirrorId || mirrorContext?.mirrorId}`)}
                              className="border-white/20 text-white hover:bg-white/5 rounded-full px-6 py-5"
                            >
                              View Status
                            </Button>
                          </div>
                        </>
                      )}

                      {isMirrorPartner && mirrorConsented && (
                        <>
                          <h3 className="text-lg font-light text-[#3DD9C5] mb-3" style={{ fontFamily: "Fraunces, serif" }}>
                            Consent Recorded
                          </h3>
                          <p className="text-sm text-muted-foreground mb-6">
                            The dual perspective report will be available once your partner also consents.
                          </p>
                          <Button
                            onClick={() => navigate(`/dual-report/${mirrorId || mirrorContext?.mirrorId}`)}
                            className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-6 py-5 btn-glow"
                          >
                            View Dual Report
                          </Button>
                        </>
                      )}

                      {/* Partner A flow: create mirror & share link */}
                      {!isMirrorPartner && !mirrorInviteUrl && (
                        <>
                          <h3 className="text-lg font-light text-[#E6EDF3] mb-3" style={{ fontFamily: "Fraunces, serif" }}>
                            Invite Your Partner for a Mirror Analysis
                          </h3>
                          <p className="text-sm text-muted-foreground mb-6 max-w-md leading-relaxed">
                            Generate a private link for your partner to complete their own TrustLens analysis.
                            Once both of you consent, a Dual Perspective Report will compare your perceptions.
                          </p>
                          <Button
                            onClick={handleCreateMirror}
                            disabled={mirrorCreating}
                            className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-8 py-5 btn-glow"
                            data-testid="create-mirror-btn"
                          >
                            {mirrorCreating ? (
                              <>Creating...</>
                            ) : (
                              <>
                                <Users className="w-5 h-5 mr-2" />
                                Generate Partner Invite
                              </>
                            )}
                          </Button>
                        </>
                      )}

                      {/* Partner A: Invite link created */}
                      {!isMirrorPartner && mirrorInviteUrl && (
                        <>
                          <h3 className="text-lg font-light text-[#E6EDF3] mb-3" style={{ fontFamily: "Fraunces, serif" }}>
                            Partner Invite Ready
                          </h3>
                          <p className="text-sm text-muted-foreground mb-4 max-w-md">
                            Share this private link with your partner. They will complete their own analysis independently.
                          </p>

                          <button
                            onClick={copyMirrorLink}
                            className="inline-flex items-center gap-2 px-4 py-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors text-sm text-[#E6EDF3] font-mono max-w-full mb-6"
                            data-testid="mirror-invite-url"
                          >
                            {mirrorCopied ? <Check className="w-4 h-4 text-[#3DD9C5] flex-shrink-0" /> : <Copy className="w-4 h-4 flex-shrink-0" />}
                            <span className="truncate">{mirrorInviteUrl}</span>
                          </button>

                          {/* Partner A consent */}
                          {!mirrorConsented ? (
                            <Button
                              onClick={handleMirrorConsent}
                              className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-6 py-5 btn-glow mb-3"
                              data-testid="partner-a-consent-btn"
                            >
                              <Lock className="w-4 h-4 mr-2" />
                              I Consent to Share My Results
                            </Button>
                          ) : (
                            <div className="flex items-center gap-2 text-[#3DD9C5] text-sm mb-3">
                              <Check className="w-4 h-4" />
                              You have consented
                            </div>
                          )}

                          {mirrorStatus && (
                            <p className="text-xs text-muted-foreground">
                              {mirrorStatus.partner_b_joined
                                ? mirrorStatus.partner_b_complete
                                  ? mirrorStatus.partner_b_consented
                                    ? "Both partners ready!"
                                    : "Partner has completed their analysis. Waiting for their consent."
                                  : "Your partner has started their analysis..."
                                : "Waiting for your partner to join..."}
                            </p>
                          )}

                          {mirrorStatus?.report_ready && (
                            <Button
                              onClick={() => navigate(`/dual-report/${mirrorId}`)}
                              className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-6 py-5 btn-glow mt-4"
                              data-testid="view-dual-report-btn"
                            >
                              View Dual Perspective Report
                              <ChevronRight className="w-5 h-5 ml-2" />
                            </Button>
                          )}
                        </>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </motion.section>
            )}

            {/* Stage 12: Closing Support Note */}
            {revealStage >= 12 && (
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
                  className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4"
                >
                  <Button
                    onClick={handleShare}
                    disabled={sharing}
                    variant="outline"
                    className="border-[#3DD9C5]/40 text-[#3DD9C5] hover:bg-[#3DD9C5]/10 rounded-full px-6 py-5"
                    data-testid="share-report-btn"
                  >
                    {copied ? <Check className="w-4 h-4 mr-2" /> : <Share2 className="w-4 h-4 mr-2" />}
                    {sharing ? "Generating..." : copied ? "Link Copied" : "Share Anonymized Report"}
                  </Button>
                  <Button
                    onClick={() => navigate("/")}
                    variant="ghost"
                    className="text-muted-foreground hover:text-white hover:bg-white/5 rounded-full"
                  >
                    <Home className="w-4 h-4 mr-2" />
                    Return Home
                  </Button>
                </motion.div>

                {shareUrl && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-4"
                  >
                    <button
                      onClick={() => copyToClipboard(shareUrl)}
                      className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors text-xs text-muted-foreground font-mono max-w-full"
                      data-testid="share-url-display"
                    >
                      <Copy className="w-3 h-3 flex-shrink-0" />
                      <span className="truncate">{shareUrl}</span>
                    </button>
                  </motion.div>
                )}
              </motion.section>
            )}

            {/* Soft Save Prompt — appears after all results are shown */}
            {revealStage >= 12 && !analysisSaved && (
              <motion.section
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 }}
                data-testid="save-analysis-prompt"
              >
                <Card className="glass-card rounded-2xl border-[#3DD9C5]/15">
                  <CardContent className="p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-full bg-[#3DD9C5]/10 flex items-center justify-center flex-shrink-0">
                        <Save className="w-5 h-5 text-[#3DD9C5]" />
                      </div>
                      <div>
                        <p className="text-sm text-[#E6EDF3]">
                          Save this analysis to track your relationship signals over time.
                        </p>
                        <p className="text-xs text-muted-foreground mt-0.5">
                          Optional. Your analysis can still be used anonymously.
                        </p>
                      </div>
                    </div>
                    <Button
                      onClick={handleSaveAnalysis}
                      className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-6 py-4 btn-glow whitespace-nowrap"
                      data-testid="save-analysis-btn"
                    >
                      {isLoggedIn ? "Save Analysis" : "Create Account & Save"}
                    </Button>
                  </CardContent>
                </Card>
              </motion.section>
            )}

            {analysisSaved && revealStage >= 12 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center"
              >
                <p className="text-sm text-[#3DD9C5] flex items-center justify-center gap-2">
                  <Check className="w-4 h-4" />
                  Analysis saved to your history.
                  <button
                    onClick={() => navigate("/my-analyses")}
                    className="underline hover:no-underline"
                    data-testid="view-history-link"
                  >
                    View all analyses
                  </button>
                </p>
              </motion.div>
            )}

            {/* Global Pattern Engine — Contribute */}
            {revealStage >= 12 && !contributed && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-card rounded-2xl p-8 text-center"
                data-testid="contribute-section"
              >
                <Globe className="w-8 h-8 text-[#3DD9C5]/60 mx-auto mb-3" />
                <h3 className="text-lg text-[#E6EDF3] mb-2" style={{ fontFamily: "Fraunces, serif" }}>
                  Help Others Gain Clarity
                </h3>
                <p className="text-sm text-muted-foreground mb-6 max-w-md mx-auto">
                  Anonymously contribute your experience to improve TrustLens for everyone. No personal data is shared — only the behavioral patterns and outcome.
                </p>

                {!contributingOutcome ? (
                  <div>
                    <p className="text-xs text-white/40 mb-3 uppercase tracking-wider">What best describes the outcome?</p>
                    <div className="flex flex-wrap justify-center gap-2">
                      {[
                        { value: "confirmed_infidelity", label: "Confirmed infidelity" },
                        { value: "emotional_disengagement", label: "Emotional disengagement" },
                        { value: "misunderstanding", label: "It was a misunderstanding" },
                        { value: "personal_crisis", label: "Partner going through crisis" },
                        { value: "unresolved_conflict", label: "Still unresolved" },
                      ].map((opt) => (
                        <Button
                          key={opt.value}
                          variant="outline"
                          size="sm"
                          onClick={() => setContributingOutcome(opt.value)}
                          className="border-white/15 text-white/70 hover:bg-white/10 hover:text-white rounded-full text-xs px-4"
                          data-testid={`outcome-${opt.value}`}
                        >
                          {opt.label}
                        </Button>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <p className="text-sm text-white/60">
                      Outcome: <span className="text-white/80">{contributingOutcome.replace(/_/g, " ")}</span>
                    </p>
                    <div className="flex justify-center gap-3">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setContributingOutcome(null)}
                        className="border-white/15 text-white/50 hover:bg-white/5 rounded-full"
                      >
                        Change
                      </Button>
                      <Button
                        size="sm"
                        disabled={contributingLoading}
                        onClick={async () => {
                          setContributingLoading(true);
                          try {
                            await contributeCase(sessionId, contributingOutcome);
                            setContributed(true);
                            toast.success("Thank you for contributing anonymously");
                          } catch {
                            toast.error("Contribution failed");
                          } finally {
                            setContributingLoading(false);
                          }
                        }}
                        className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-6"
                        data-testid="confirm-contribute-btn"
                      >
                        {contributingLoading ? "Contributing..." : "Contribute Anonymously"}
                      </Button>
                    </div>
                  </div>
                )}
              </motion.div>
            )}

            {contributed && revealStage >= 12 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center"
              >
                <p className="text-sm text-[#3DD9C5] flex items-center justify-center gap-2">
                  <Check className="w-4 h-4" />
                  Thank you. Your anonymous contribution helps improve pattern analysis for everyone.
                </p>
              </motion.div>
            )}
          </div>
        )}
      </main>

      {/* Auth Modal */}
      <AuthModal
        open={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onSuccess={handleAuthSuccess}
        mode="register"
      />
    </div>
  );
};

export default ResultsDashboard;

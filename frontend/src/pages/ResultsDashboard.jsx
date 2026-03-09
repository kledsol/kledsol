import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { TrustLensLogo, HeartLensIcon } from "@/components/custom/Logo";
import { StabilityHearts, StabilityLabel } from "@/components/custom/StabilityHearts";
import { TrustGauge, TrustIndexLabel } from "@/components/custom/TrustGauge";
import { useAnalysis } from "@/App";
import { getResults } from "@/lib/api";
import { toast } from "sonner";
import {
  Activity,
  Brain,
  Shield,
  Clock,
  Target,
  Lightbulb,
  MessageSquare,
  TrendingUp,
  Users,
  RefreshCw,
  ChevronRight,
  BarChart3,
} from "lucide-react";

const ResultsDashboard = () => {
  const { sessionId, resetAnalysis } = useAnalysis();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [results, setResults] = useState(null);
  const [showReveal, setShowReveal] = useState(true);

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
      // Show reveal animation for 3 seconds
      setTimeout(() => setShowReveal(false), 3000);
    } catch (e) {
      toast.error("Failed to load results");
      navigate("/");
    } finally {
      setLoading(false);
    }
  };

  const handleStartOver = () => {
    resetAnalysis();
    navigate("/");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#14213D] flex items-center justify-center">
        <div className="text-center">
          <HeartLensIcon size={80} animate />
          <p className="mt-6 text-muted-foreground">Generating analysis...</p>
        </div>
      </div>
    );
  }

  if (showReveal) {
    return (
      <div className="min-h-screen bg-[#14213D] flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.7 }}
          className="text-center"
        >
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <HeartLensIcon size={100} animate />
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.8 }}
            className="mt-8"
          >
            <StabilityHearts count={results?.stability_hearts || 0} size="lg" />
          </motion.div>
          <motion.h2
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 1.2 }}
            className="text-3xl font-light text-[#F5F7FA] mt-6"
            style={{ fontFamily: 'Fraunces, serif' }}
          >
            Analysis Complete
          </motion.h2>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 1.6 }}
            className="mt-4"
          >
            <TrustIndexLabel value={results?.trust_disruption_index || 0} />
          </motion.div>
        </motion.div>
      </div>
    );
  }

  if (!results) return null;

  const sortedHypotheses = Object.entries(results.hypotheses || {}).sort(([, a], [, b]) => b - a);
  const sortedSignals = Object.entries(results.signals || {}).sort(([, a], [, b]) => b - a);

  return (
    <div className="min-h-screen bg-[#14213D]">
      <header className="glass border-b border-white/10 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/">
            <TrustLensLogo size="md" />
          </Link>
          <Button
            variant="outline"
            onClick={handleStartOver}
            className="border-white/20 text-white hover:bg-white/5 rounded-full"
            data-testid="start-over-btn"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            New Analysis
          </Button>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        {/* Bento Grid Dashboard */}
        <div className="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-12 gap-6">
          {/* Trust Disruption Index */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="md:col-span-2 lg:col-span-4"
          >
            <Card className="glass-card rounded-2xl h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base text-[#F5F7FA]">
                  <Target className="w-5 h-5 text-[#2EC4B6]" />
                  Trust Disruption Index
                </CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col items-center justify-center">
                <TrustGauge value={results.trust_disruption_index} />
                <div className="mt-4 text-lg">
                  <TrustIndexLabel value={results.trust_disruption_index} />
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Stability Hearts & Confidence */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="md:col-span-2 lg:col-span-4 space-y-6"
          >
            <Card className="glass-card rounded-2xl">
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-base text-[#F5F7FA]">
                  Relationship Stability
                </CardTitle>
              </CardHeader>
              <CardContent className="flex items-center justify-between">
                <StabilityHearts count={results.stability_hearts} size="lg" />
                <StabilityLabel hearts={results.stability_hearts} />
              </CardContent>
            </Card>

            <Card className="glass-card rounded-2xl">
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-base text-[#F5F7FA]">
                  <Shield className="w-5 h-5 text-[#2EC4B6]" />
                  Confidence Level
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full ${
                    results.confidence_level === "high" ? "bg-[#7BD389]" :
                    results.confidence_level === "moderate" ? "bg-[#FCA311]" : "bg-white/30"
                  }`} />
                  <span className="text-xl font-medium text-[#F5F7FA] capitalize">
                    {results.confidence_level}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground mt-2">
                  Based on {results.questions_answered} questions analyzed
                </p>
              </CardContent>
            </Card>
          </motion.div>

          {/* Dominant Pattern & Narrative Consistency */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="md:col-span-4 lg:col-span-4 space-y-6"
          >
            <Card className="glass-card rounded-2xl">
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-base text-[#F5F7FA]">
                  <Brain className="w-5 h-5 text-[#2EC4B6]" />
                  Dominant Pattern
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-xl text-[#FF4D6D]">{results.dominant_pattern}</p>
              </CardContent>
            </Card>

            <Card className="glass-card rounded-2xl">
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-base text-[#F5F7FA]">
                  <MessageSquare className="w-5 h-5 text-[#2EC4B6]" />
                  Narrative Consistency
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-mono text-[#F5F7FA]">
                  {results.narrative_consistency.toFixed(0)}
                  <span className="text-lg text-muted-foreground">%</span>
                </div>
                <Progress value={results.narrative_consistency} className="h-1 mt-2" />
              </CardContent>
            </Card>
          </motion.div>

          {/* Hypothesis Analysis */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="md:col-span-2 lg:col-span-6"
          >
            <Card className="glass-card rounded-2xl">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base text-[#F5F7FA]">
                  <TrendingUp className="w-5 h-5 text-[#2EC4B6]" />
                  Hypothesis Analysis
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {sortedHypotheses.slice(0, 5).map(([key, value]) => (
                  <div key={key}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-[#F5F7FA]">{key.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}</span>
                      <span className="font-mono text-muted-foreground">{(value * 100).toFixed(0)}%</span>
                    </div>
                    <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${value * 100}%` }}
                        transition={{ duration: 0.8, delay: 0.5 }}
                        className="h-full bg-[#2EC4B6] rounded-full"
                      />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>

          {/* Signal Intensity */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="md:col-span-2 lg:col-span-6"
          >
            <Card className="glass-card rounded-2xl">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base text-[#F5F7FA]">
                  <Activity className="w-5 h-5 text-[#2EC4B6]" />
                  Signal Intensity
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {sortedSignals.map(([key, value]) => (
                  <div key={key}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-[#F5F7FA]">{key.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}</span>
                      <span className="font-mono text-muted-foreground">{(value * 100).toFixed(0)}%</span>
                    </div>
                    <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${value * 100}%` }}
                        transition={{ duration: 0.8, delay: 0.6 }}
                        className={`h-full rounded-full ${
                          value > 0.6 ? "bg-[#FF4D6D]" : value > 0.3 ? "bg-[#FCA311]" : "bg-[#7BD389]"
                        }`}
                      />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </motion.div>

          {/* Pattern Statistics */}
          {results.pattern_statistics && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="md:col-span-4 lg:col-span-4"
            >
              <Card className="glass-card rounded-2xl">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base text-[#F5F7FA]">
                    <BarChart3 className="w-5 h-5 text-[#2EC4B6]" />
                    Pattern Comparison
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">
                    In similar behavioral patterns:
                  </p>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-[#F5F7FA]">Confirmed relationship issues</span>
                      <span className="font-mono text-[#FF4D6D]">{results.pattern_statistics.confirmed_issues}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-[#F5F7FA]">Severe conflict (no infidelity)</span>
                      <span className="font-mono text-[#FCA311]">{results.pattern_statistics.relationship_conflict}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-[#F5F7FA]">Resolved positively</span>
                      <span className="font-mono text-[#7BD389]">{results.pattern_statistics.resolved_positively}%</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Timeline */}
          {results.timeline_events && results.timeline_events.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="md:col-span-4 lg:col-span-4"
            >
              <Card className="glass-card rounded-2xl">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base text-[#F5F7FA]">
                    <Clock className="w-5 h-5 text-[#2EC4B6]" />
                    Timeline
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="relative pl-6">
                    <div className="absolute left-2 top-0 bottom-0 w-0.5 bg-white/10" />
                    {results.timeline_events.map((event, i) => (
                      <div key={i} className="relative mb-4 last:mb-0">
                        <div className={`absolute -left-4 w-3 h-3 rounded-full ${
                          event.type === "start" ? "bg-[#2EC4B6]" : "bg-white/30"
                        }`} />
                        <p className="text-sm text-[#F5F7FA]">{event.period}</p>
                        <p className="text-xs text-muted-foreground">{event.event}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* TrustLens Perspective */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="md:col-span-4 lg:col-span-12"
          >
            <Card className="glass-card rounded-2xl border-[#2EC4B6]/30">
              <CardContent className="p-8">
                <div className="flex items-start gap-6">
                  <HeartLensIcon size={48} />
                  <div>
                    <h3 className="text-xl font-light text-[#F5F7FA] mb-3" style={{ fontFamily: 'Fraunces, serif' }}>
                      TrustLens Perspective
                    </h3>
                    <p className="text-muted-foreground leading-relaxed">
                      {results.trustlens_perspective}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Clarity Actions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className="md:col-span-4 lg:col-span-12"
          >
            <Card className="glass-card rounded-2xl">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base text-[#F5F7FA]">
                  <Lightbulb className="w-5 h-5 text-[#2EC4B6]" />
                  Suggested Clarity Actions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {results.clarity_actions?.map((action, i) => (
                    <div
                      key={i}
                      className="flex items-start gap-3 p-4 rounded-xl bg-white/5"
                    >
                      <div className="w-6 h-6 rounded-full bg-[#2EC4B6]/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs font-mono text-[#2EC4B6]">{i + 1}</span>
                      </div>
                      <p className="text-sm text-[#F5F7FA]">{action}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Action Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9 }}
            className="md:col-span-4 lg:col-span-12"
          >
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                onClick={() => navigate("/mirror")}
                size="lg"
                variant="outline"
                className="border-white/20 text-white hover:bg-white/5 rounded-full px-8 py-6"
                data-testid="mirror-btn"
              >
                <Users className="w-5 h-5 mr-2" />
                Try Mirror Mode
              </Button>
              <Button
                onClick={() => navigate("/coach")}
                size="lg"
                className="bg-[#2EC4B6] text-black hover:bg-[#259F94] rounded-full px-8 py-6 btn-glow"
                data-testid="coach-btn"
              >
                <MessageSquare className="w-5 h-5 mr-2" />
                Conversation Coach
                <ChevronRight className="w-5 h-5 ml-2" />
              </Button>
            </div>
          </motion.div>

          {/* Privacy Footer */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
            className="md:col-span-4 lg:col-span-12"
          >
            <div className="flex items-center justify-center gap-2 py-4 text-sm text-muted-foreground">
              <Shield className="w-4 h-4" />
              <span>This analysis is for personal reflection only. No data is stored or shared.</span>
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  );
};

export default ResultsDashboard;

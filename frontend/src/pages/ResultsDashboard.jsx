import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useTheme, useAnalysis } from "@/App";
import { getResults, submitReaction } from "@/lib/api";
import { toast } from "sonner";
import {
  Moon,
  Sun,
  RefreshCw,
  Shield,
  AlertTriangle,
  TrendingUp,
  MessageSquare,
  Clock,
  Target,
  Lightbulb,
  CheckCircle,
  XCircle,
  HelpCircle,
  Activity,
  BarChart3,
  Map,
  Loader2,
} from "lucide-react";

const ResultsDashboard = () => {
  const { theme, toggleTheme } = useTheme();
  const { sessionId, resetAnalysis } = useAnalysis();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [results, setResults] = useState(null);
  const [reactionDialogOpen, setReactionDialogOpen] = useState(false);
  const [reactionData, setReactionData] = useState({
    type: "",
    notes: "",
  });
  const [submittingReaction, setSubmittingReaction] = useState(false);

  useEffect(() => {
    if (!sessionId) {
      toast.error("Session not found. Please start over.");
      navigate("/");
      return;
    }
    fetchResults();
  }, [sessionId]);

  const fetchResults = async () => {
    setLoading(true);
    try {
      const data = await getResults(sessionId);
      setResults(data);
    } catch (error) {
      console.error("Failed to fetch results:", error);
      toast.error("Failed to load results. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitReaction = async () => {
    if (!reactionData.type) {
      toast.error("Please select a reaction type");
      return;
    }

    setSubmittingReaction(true);
    try {
      await submitReaction({
        session_id: sessionId,
        reaction_type: reactionData.type,
        notes: reactionData.notes,
      });
      toast.success("Reaction recorded. Analysis will be updated.");
      setReactionDialogOpen(false);
      setReactionData({ type: "", notes: "" });
      fetchResults();
    } catch (error) {
      console.error("Failed to submit reaction:", error);
      toast.error("Failed to record reaction");
    } finally {
      setSubmittingReaction(false);
    }
  };

  const handleStartOver = () => {
    resetAnalysis();
    navigate("/");
  };

  const getTrustIndexColor = (index) => {
    if (index < 20) return "text-green-400";
    if (index < 40) return "text-green-300";
    if (index < 60) return "text-yellow-400";
    if (index < 80) return "text-orange-400";
    return "text-red-400";
  };

  const getTrustIndexLabel = (index) => {
    if (index < 20) return "Normal Variation";
    if (index < 40) return "Mild Change";
    if (index < 60) return "Noticeable Shift";
    if (index < 80) return "Significant Disruption";
    return "Severe Disruption";
  };

  const formatHypothesisName = (name) => {
    return name
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  const formatSignalName = (name) => {
    return name
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full bg-accent/20 flex items-center justify-center mx-auto mb-4 pulse-glow">
            <BarChart3 className="w-8 h-8 text-accent animate-pulse" />
          </div>
          <p className="text-muted-foreground">Generating analysis...</p>
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <p className="text-muted-foreground mb-4">Failed to load results</p>
          <Button onClick={() => navigate("/")} variant="outline">
            Start Over
          </Button>
        </div>
      </div>
    );
  }

  const sortedHypotheses = Object.entries(results.hypotheses).sort(
    ([, a], [, b]) => b - a
  );
  const sortedSignals = Object.entries(results.signals).sort(
    ([, a], [, b]) => b - a
  );

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 glass border-b border-border/50">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-lg bg-accent/20 flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-accent" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-foreground">
                Analysis Results
              </h1>
              <p className="text-sm text-muted-foreground">
                {results.questions_answered} questions analyzed
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              data-testid="theme-toggle"
            >
              {theme === "dark" ? (
                <Sun className="w-5 h-5" />
              ) : (
                <Moon className="w-5 h-5" />
              )}
            </Button>
            <Button
              variant="outline"
              onClick={handleStartOver}
              data-testid="start-over-btn"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              New Analysis
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Bento Grid Dashboard */}
        <div className="grid grid-cols-1 md:grid-cols-4 lg:grid-cols-12 gap-6">
          {/* Trust Disruption Index - Large Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="md:col-span-4 lg:col-span-4"
          >
            <Card className="bg-card/60 backdrop-blur border-border/50 h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Target className="w-5 h-5 text-accent" />
                  Trust Disruption Index
                </CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col items-center justify-center pt-4">
                {/* Circular Gauge */}
                <div className="relative w-48 h-48 mb-6">
                  <svg
                    className="w-full h-full transform -rotate-90"
                    viewBox="0 0 100 100"
                  >
                    {/* Background circle */}
                    <circle
                      cx="50"
                      cy="50"
                      r="45"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="8"
                      className="text-muted/30"
                    />
                    {/* Progress arc */}
                    <circle
                      cx="50"
                      cy="50"
                      r="45"
                      fill="none"
                      stroke="url(#gaugeGradient)"
                      strokeWidth="8"
                      strokeLinecap="round"
                      strokeDasharray={`${
                        (results.trust_disruption_index / 100) * 283
                      } 283`}
                    />
                    <defs>
                      <linearGradient
                        id="gaugeGradient"
                        x1="0%"
                        y1="0%"
                        x2="100%"
                        y2="0%"
                      >
                        <stop offset="0%" stopColor="#10B981" />
                        <stop offset="50%" stopColor="#F59E0B" />
                        <stop offset="100%" stopColor="#EF4444" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span
                      className={`text-5xl font-bold font-mono ${getTrustIndexColor(
                        results.trust_disruption_index
                      )}`}
                      data-testid="trust-index-value"
                    >
                      {results.trust_disruption_index.toFixed(0)}
                    </span>
                    <span className="text-sm text-muted-foreground">
                      / 100
                    </span>
                  </div>
                </div>
                <p
                  className={`text-lg font-semibold ${getTrustIndexColor(
                    results.trust_disruption_index
                  )}`}
                >
                  {getTrustIndexLabel(results.trust_disruption_index)}
                </p>
              </CardContent>
            </Card>
          </motion.div>

          {/* Confidence & Uncertainty - Stacked Cards */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="md:col-span-2 lg:col-span-4 space-y-6"
          >
            <Card className="bg-card/60 backdrop-blur border-border/50">
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-base">
                  <Shield className="w-5 h-5 text-accent" />
                  Diagnostic Confidence
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-3">
                  <div
                    className={`w-3 h-3 rounded-full ${
                      results.confidence_level === "high"
                        ? "bg-green-400"
                        : results.confidence_level === "moderate"
                        ? "bg-yellow-400"
                        : "bg-muted-foreground"
                    }`}
                  />
                  <span
                    className="text-2xl font-bold capitalize text-foreground"
                    data-testid="confidence-value"
                  >
                    {results.confidence_level}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground mt-2">
                  Based on signal convergence and data completeness
                </p>
              </CardContent>
            </Card>

            <Card className="bg-card/60 backdrop-blur border-border/50">
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-base">
                  <AlertTriangle className="w-5 h-5 text-accent" />
                  Uncertainty Level
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-3">
                  <div
                    className={`w-3 h-3 rounded-full ${
                      results.uncertainty_level === "low"
                        ? "bg-green-400"
                        : results.uncertainty_level === "moderate"
                        ? "bg-yellow-400"
                        : "bg-red-400"
                    }`}
                  />
                  <span
                    className="text-2xl font-bold capitalize text-foreground"
                    data-testid="uncertainty-value"
                  >
                    {results.uncertainty_level}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground mt-2">
                  Multiple hypotheses remain viable
                </p>
              </CardContent>
            </Card>
          </motion.div>

          {/* Narrative Consistency */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.15 }}
            className="md:col-span-2 lg:col-span-4"
          >
            <Card className="bg-card/60 backdrop-blur border-border/50 h-full">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <MessageSquare className="w-5 h-5 text-accent" />
                  Narrative Consistency
                </CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col items-center justify-center">
                <div className="text-5xl font-bold font-mono text-foreground mb-2">
                  {results.narrative_consistency.toFixed(0)}
                  <span className="text-2xl text-muted-foreground">%</span>
                </div>
                <Progress
                  value={results.narrative_consistency}
                  className="h-2 w-full max-w-[200px]"
                />
                <p className="text-sm text-muted-foreground mt-3 text-center">
                  Consistency in your responses and timeline descriptions
                </p>
              </CardContent>
            </Card>
          </motion.div>

          {/* Hypothesis Visualization - Full Width */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="md:col-span-4 lg:col-span-6"
          >
            <Card className="bg-card/60 backdrop-blur border-border/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <TrendingUp className="w-5 h-5 text-accent" />
                  Hypothesis Analysis
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {sortedHypotheses.map(([hypothesis, probability]) => (
                    <div key={hypothesis}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-foreground">
                          {formatHypothesisName(hypothesis)}
                        </span>
                        <span className="font-mono text-muted-foreground">
                          {(probability * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="h-2 bg-muted rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${probability * 100}%` }}
                          transition={{ duration: 0.5, delay: 0.3 }}
                          className="h-full bg-accent rounded-full"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Signal Intensity */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.25 }}
            className="md:col-span-4 lg:col-span-6"
          >
            <Card className="bg-card/60 backdrop-blur border-border/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Activity className="w-5 h-5 text-accent" />
                  Behavioral Signal Intensity
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {sortedSignals.map(([signal, intensity]) => (
                    <div key={signal}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-foreground">
                          {formatSignalName(signal)}
                        </span>
                        <span className="font-mono text-muted-foreground">
                          {(intensity * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="h-2 bg-muted rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${intensity * 100}%` }}
                          transition={{ duration: 0.5, delay: 0.35 }}
                          className={`h-full rounded-full ${
                            intensity > 0.6
                              ? "bg-red-400"
                              : intensity > 0.3
                              ? "bg-yellow-400"
                              : "bg-green-400"
                          }`}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Context Estimation */}
          {results.context_estimation &&
            results.context_estimation.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3 }}
                className="md:col-span-2 lg:col-span-4"
              >
                <Card className="bg-card/60 backdrop-blur border-border/50">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-base">
                      <Map className="w-5 h-5 text-accent" />
                      Probable Interaction Contexts
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {results.context_estimation.map((context, index) => (
                        <li
                          key={index}
                          className="flex items-center gap-2 text-sm"
                        >
                          <div className="w-2 h-2 rounded-full bg-accent" />
                          <span className="text-foreground capitalize">
                            {context.replace(/_/g, " ")}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              </motion.div>
            )}

          {/* Timeline */}
          {results.timeline_events && results.timeline_events.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.35 }}
              className="md:col-span-2 lg:col-span-4"
            >
              <Card className="bg-card/60 backdrop-blur border-border/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Clock className="w-5 h-5 text-accent" />
                    Relationship Timeline
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="relative">
                    <div className="absolute left-3 top-0 bottom-0 w-0.5 bg-border" />
                    <div className="space-y-4">
                      {results.timeline_events.map((event, index) => (
                        <div
                          key={index}
                          className="relative flex items-start gap-4"
                        >
                          <div
                            className={`w-6 h-6 rounded-full flex items-center justify-center z-10 ${
                              event.type === "start"
                                ? "bg-accent"
                                : "bg-muted"
                            }`}
                          >
                            <div
                              className={`w-2 h-2 rounded-full ${
                                event.type === "start"
                                  ? "bg-accent-foreground"
                                  : "bg-muted-foreground"
                              }`}
                            />
                          </div>
                          <div>
                            <p className="text-sm font-medium text-foreground">
                              {event.period}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {event.event}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Pattern Clusters */}
          {results.pattern_clusters && results.pattern_clusters.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="md:col-span-4 lg:col-span-4"
            >
              <Card className="bg-card/60 backdrop-blur border-border/50">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Activity className="w-5 h-5 text-accent" />
                    Detected Pattern Clusters
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {results.pattern_clusters.map((cluster, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 rounded-full text-sm bg-accent/20 text-accent border border-accent/30"
                      >
                        {cluster.replace(/_/g, " ")}
                      </span>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Clarity Actions - Full Width */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.45 }}
            className="md:col-span-4 lg:col-span-12"
          >
            <Card className="bg-card/60 backdrop-blur border-border/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Lightbulb className="w-5 h-5 text-accent" />
                  Recommended Clarity Actions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {results.clarity_actions.map((action, index) => (
                    <div
                      key={index}
                      className="flex items-start gap-3 p-4 rounded-lg bg-background/50 border border-border/50"
                    >
                      <CheckCircle className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                      <span className="text-sm text-foreground">{action}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Reaction Tracking */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="md:col-span-4 lg:col-span-12"
          >
            <Card className="bg-card/60 backdrop-blur border-accent/20">
              <CardContent className="p-6">
                <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-accent/20 flex items-center justify-center">
                      <MessageSquare className="w-6 h-6 text-accent" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-foreground">
                        Update After Real Conversation
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        Track how your partner responded to help refine the
                        analysis
                      </p>
                    </div>
                  </div>
                  <Dialog
                    open={reactionDialogOpen}
                    onOpenChange={setReactionDialogOpen}
                  >
                    <DialogTrigger asChild>
                      <Button
                        className="bg-accent hover:bg-accent/90 text-accent-foreground"
                        data-testid="track-reaction-btn"
                      >
                        Track Reaction
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-md">
                      <DialogHeader>
                        <DialogTitle>Track Partner's Reaction</DialogTitle>
                      </DialogHeader>
                      <div className="space-y-4 py-4">
                        <RadioGroup
                          value={reactionData.type}
                          onValueChange={(value) =>
                            setReactionData((prev) => ({
                              ...prev,
                              type: value,
                            }))
                          }
                        >
                          <div className="flex items-center space-x-3 p-3 rounded-lg border border-border hover:bg-muted/50">
                            <RadioGroupItem
                              value="open_discussion"
                              id="open"
                            />
                            <Label
                              htmlFor="open"
                              className="flex items-center gap-2 cursor-pointer"
                            >
                              <CheckCircle className="w-4 h-4 text-green-400" />
                              Open Discussion
                            </Label>
                          </div>
                          <div className="flex items-center space-x-3 p-3 rounded-lg border border-border hover:bg-muted/50">
                            <RadioGroupItem
                              value="defensive_reaction"
                              id="defensive"
                            />
                            <Label
                              htmlFor="defensive"
                              className="flex items-center gap-2 cursor-pointer"
                            >
                              <XCircle className="w-4 h-4 text-red-400" />
                              Defensive Reaction
                            </Label>
                          </div>
                          <div className="flex items-center space-x-3 p-3 rounded-lg border border-border hover:bg-muted/50">
                            <RadioGroupItem
                              value="vague_explanation"
                              id="vague"
                            />
                            <Label
                              htmlFor="vague"
                              className="flex items-center gap-2 cursor-pointer"
                            >
                              <HelpCircle className="w-4 h-4 text-yellow-400" />
                              Vague Explanation
                            </Label>
                          </div>
                          <div className="flex items-center space-x-3 p-3 rounded-lg border border-border hover:bg-muted/50">
                            <RadioGroupItem
                              value="willingness_to_clarify"
                              id="clarify"
                            />
                            <Label
                              htmlFor="clarify"
                              className="flex items-center gap-2 cursor-pointer"
                            >
                              <CheckCircle className="w-4 h-4 text-accent" />
                              Willingness to Clarify
                            </Label>
                          </div>
                        </RadioGroup>
                        <Separator />
                        <div>
                          <Label className="text-sm text-muted-foreground mb-2 block">
                            Additional Notes (optional)
                          </Label>
                          <Textarea
                            value={reactionData.notes}
                            onChange={(e) =>
                              setReactionData((prev) => ({
                                ...prev,
                                notes: e.target.value,
                              }))
                            }
                            placeholder="Describe the conversation outcome..."
                            className="min-h-[80px]"
                          />
                        </div>
                        <Button
                          onClick={handleSubmitReaction}
                          disabled={submittingReaction || !reactionData.type}
                          className="w-full bg-accent hover:bg-accent/90 text-accent-foreground"
                        >
                          {submittingReaction ? (
                            <>
                              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                              Saving...
                            </>
                          ) : (
                            "Submit Reaction"
                          )}
                        </Button>
                      </div>
                    </DialogContent>
                  </Dialog>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Privacy Notice */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.55 }}
            className="md:col-span-4 lg:col-span-12"
          >
            <div className="flex items-center justify-center gap-2 py-4 text-sm text-muted-foreground">
              <Shield className="w-4 h-4" />
              <span>
                This analysis is for personal reflection only. No data is shared
                or stored permanently.
              </span>
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  );
};

export default ResultsDashboard;

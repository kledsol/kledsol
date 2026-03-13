import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { getMyAnalyses } from "@/lib/api";
import { toast } from "sonner";
import {
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Clock,
  AlertTriangle,
  Shield,
  ChevronRight,
} from "lucide-react";

const ScoreBar = ({ score, label }) => {
  const color = score >= 70 ? "#FF4D6D" : score >= 40 ? "#FCA311" : "#3DD9C5";
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-2 rounded-full bg-white/10 overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
        />
      </div>
      <span className="text-sm font-mono min-w-[3rem] text-right" style={{ color }}>
        {score}/100
      </span>
    </div>
  );
};

const MyAnalyses = () => {
  const navigate = useNavigate();
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedIdx, setSelectedIdx] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("trustlens_token");
    if (!token) {
      navigate("/");
      return;
    }
    (async () => {
      try {
        const data = await getMyAnalyses();
        setAnalyses(data.analyses || []);
      } catch {
        toast.error("Failed to load analyses");
      } finally {
        setLoading(false);
      }
    })();
  }, [navigate]);

  const selected = selectedIdx !== null ? analyses[selectedIdx] : null;
  const previous = selectedIdx !== null && selectedIdx < analyses.length - 1 ? analyses[selectedIdx + 1] : null;

  return (
    <div className="min-h-screen bg-[#0B132B]">
      <header className="glass border-b border-white/10">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Button
            variant="ghost"
            onClick={() => navigate("/")}
            className="text-muted-foreground hover:text-white"
            data-testid="back-home-btn"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Home
          </Button>
          <h1 className="text-lg font-light text-white" style={{ fontFamily: "Fraunces, serif" }}>
            My Analyses
          </h1>
          <div className="w-20" />
        </div>
      </header>

      <main className="container mx-auto px-6 py-12 max-w-5xl">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="w-8 h-8 border-2 border-[#3DD9C5] border-t-transparent rounded-full animate-spin" />
          </div>
        ) : analyses.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-20"
          >
            <BarChart3 className="w-16 h-16 text-white/20 mx-auto mb-6" />
            <h2 className="text-2xl text-white/60 mb-2" style={{ fontFamily: "Fraunces, serif" }}>
              No analyses yet
            </h2>
            <p className="text-muted-foreground mb-8">Complete an analysis and save it to start tracking your relationship signals over time.</p>
            <Button
              onClick={() => navigate("/")}
              className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-8 py-6"
              data-testid="start-first-analysis-btn"
            >
              Start Your First Analysis
            </Button>
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Analysis List */}
            <div className="lg:col-span-1 space-y-3">
              <h2 className="text-sm uppercase tracking-wider text-white/40 mb-4">Analysis History</h2>
              {analyses.map((a, idx) => {
                const isSelected = selectedIdx === idx;
                const scoreColor = a.suspicion_score >= 70 ? "#FF4D6D" : a.suspicion_score >= 40 ? "#FCA311" : "#3DD9C5";
                return (
                  <motion.div
                    key={a.session_id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.05 }}
                  >
                    <button
                      onClick={() => setSelectedIdx(idx)}
                      className={`w-full text-left p-4 rounded-xl border transition-all ${
                        isSelected
                          ? "bg-white/10 border-[#3DD9C5]/40"
                          : "bg-white/[0.03] border-white/[0.06] hover:bg-white/[0.06]"
                      }`}
                      data-testid={`analysis-card-${idx}`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-white/40 flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {new Date(a.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}
                        </span>
                        <span className="text-sm font-mono font-semibold" style={{ color: scoreColor }}>
                          {a.suspicion_score}
                        </span>
                      </div>
                      <p className="text-sm text-white/80 mb-1">{a.suspicion_label}</p>
                      <p className="text-xs text-white/40">{a.analysis_type === "pulse" ? "Quick Pulse" : "Deep Analysis"}</p>
                    </button>
                  </motion.div>
                );
              })}
            </div>

            {/* Detail Panel */}
            <div className="lg:col-span-2">
              {!selected ? (
                <div className="flex items-center justify-center h-full text-white/30">
                  <p>Select an analysis to view details</p>
                </div>
              ) : (
                <motion.div
                  key={selected.session_id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-6"
                >
                  {/* Score Header */}
                  <Card className="bg-white/[0.04] border-white/[0.08] rounded-2xl">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <h3 className="text-xl text-white font-medium" style={{ fontFamily: "Fraunces, serif" }}>
                            {selected.suspicion_label}
                          </h3>
                          <p className="text-sm text-white/40">
                            {new Date(selected.created_at).toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" })}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-3xl font-mono font-bold" style={{
                            color: selected.suspicion_score >= 70 ? "#FF4D6D" : selected.suspicion_score >= 40 ? "#FCA311" : "#3DD9C5"
                          }}>
                            {selected.suspicion_score}
                          </p>
                          <p className="text-xs text-white/30">Suspicion Score</p>
                        </div>
                      </div>
                      <ScoreBar score={selected.suspicion_score} />

                      {/* Comparison with previous */}
                      {previous && (
                        <div className="mt-4 pt-4 border-t border-white/[0.06] flex items-center gap-3">
                          {selected.suspicion_score > previous.suspicion_score ? (
                            <TrendingUp className="w-4 h-4 text-[#FF4D6D]" />
                          ) : selected.suspicion_score < previous.suspicion_score ? (
                            <TrendingDown className="w-4 h-4 text-[#3DD9C5]" />
                          ) : (
                            <BarChart3 className="w-4 h-4 text-white/40" />
                          )}
                          <span className="text-sm text-white/50">
                            {selected.suspicion_score === previous.suspicion_score
                              ? "No change from previous analysis"
                              : `${Math.abs(selected.suspicion_score - previous.suspicion_score)} points ${
                                  selected.suspicion_score > previous.suspicion_score ? "higher" : "lower"
                                } than previous analysis (${previous.suspicion_score}/100)`
                            }
                          </span>
                        </div>
                      )}
                    </CardContent>
                  </Card>

                  {/* Dominant Pattern + Info */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <Card className="bg-white/[0.04] border-white/[0.08] rounded-2xl">
                      <CardContent className="p-5">
                        <p className="text-xs text-white/40 uppercase tracking-wider mb-2">Dominant Pattern</p>
                        <p className="text-white font-medium">{selected.dominant_pattern || "No clear pattern"}</p>
                      </CardContent>
                    </Card>
                    <Card className="bg-white/[0.04] border-white/[0.08] rounded-2xl">
                      <CardContent className="p-5">
                        <p className="text-xs text-white/40 uppercase tracking-wider mb-2">Changes Detected</p>
                        <div className="flex flex-wrap gap-1.5">
                          {(selected.changes_detected || []).length > 0 ? selected.changes_detected.map((c, i) => (
                            <span key={i} className="text-xs bg-white/10 text-white/70 px-2 py-1 rounded-full">
                              {c.replace(/_/g, " ")}
                            </span>
                          )) : (
                            <span className="text-sm text-white/30">None</span>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </div>

                  {/* Top Signals */}
                  {selected.top_signals && selected.top_signals.length > 0 && (
                    <Card className="bg-white/[0.04] border-white/[0.08] rounded-2xl">
                      <CardContent className="p-6">
                        <p className="text-xs text-white/40 uppercase tracking-wider mb-4">Top Signals Detected</p>
                        <div className="space-y-3">
                          {selected.top_signals.map((signal, i) => {
                            const color = signal.value >= 55 ? "#FF4D6D" : signal.value >= 25 ? "#FCA311" : "#6EE7B7";
                            const prevSignal = previous?.top_signals?.find(s => s.key === signal.key);
                            const delta = prevSignal ? signal.value - prevSignal.value : null;
                            return (
                              <div key={i} className="flex items-center gap-3" data-testid={`signal-${i}`}>
                                <span className="text-sm text-white/70 min-w-[140px]">{signal.key}</span>
                                <div className="flex-1 h-1.5 rounded-full bg-white/10 overflow-hidden">
                                  <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${signal.value}%` }}
                                    transition={{ duration: 0.6, delay: i * 0.1 }}
                                    className="h-full rounded-full"
                                    style={{ backgroundColor: color }}
                                  />
                                </div>
                                <span className="text-xs font-mono min-w-[2.5rem] text-right" style={{ color }}>
                                  {signal.value}%
                                </span>
                                {delta !== null && delta !== 0 && (
                                  <span className={`text-xs font-mono ${delta > 0 ? "text-[#FF4D6D]" : "text-[#3DD9C5]"}`}>
                                    {delta > 0 ? `+${delta}` : delta}
                                  </span>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  {/* Score Evolution Chart (simple visual) */}
                  {analyses.length >= 2 && (
                    <Card className="bg-white/[0.04] border-white/[0.08] rounded-2xl">
                      <CardContent className="p-6">
                        <p className="text-xs text-white/40 uppercase tracking-wider mb-4">Score Evolution</p>
                        <div className="flex items-end gap-2 h-32">
                          {[...analyses].reverse().map((a, i) => {
                            const height = Math.max(8, (a.suspicion_score / 100) * 100);
                            const color = a.suspicion_score >= 70 ? "#FF4D6D" : a.suspicion_score >= 40 ? "#FCA311" : "#3DD9C5";
                            const isSelected = a.session_id === selected.session_id;
                            return (
                              <div key={a.session_id} className="flex-1 flex flex-col items-center gap-1">
                                <span className="text-[10px] font-mono" style={{ color }}>{a.suspicion_score}</span>
                                <motion.div
                                  initial={{ height: 0 }}
                                  animate={{ height: `${height}%` }}
                                  transition={{ duration: 0.5, delay: i * 0.08 }}
                                  className={`w-full max-w-[40px] rounded-t-md ${isSelected ? "ring-2 ring-white/30" : ""}`}
                                  style={{ backgroundColor: color }}
                                  data-testid={`score-bar-${i}`}
                                />
                                <span className="text-[9px] text-white/30 truncate max-w-[50px]">
                                  {new Date(a.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                                </span>
                              </div>
                            );
                          })}
                        </div>
                      </CardContent>
                    </Card>
                  )}

                  {/* View Full Results */}
                  <div className="flex justify-center">
                    <Button
                      onClick={() => navigate(`/results?session=${selected.session_id}`)}
                      className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-8 py-6"
                      data-testid="view-full-results-btn"
                    >
                      View Full Results
                      <ChevronRight className="w-5 h-5 ml-2" />
                    </Button>
                  </div>
                </motion.div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default MyAnalyses;

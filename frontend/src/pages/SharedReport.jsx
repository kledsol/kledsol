import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/card";
import { getSharedReport } from "@/lib/api";
import { Shield, AlertTriangle, Lightbulb, Activity } from "lucide-react";

const getScoreColor = (score) => {
  if (score <= 30) return "#6EE7B7";
  if (score <= 60) return "#FCA311";
  if (score <= 80) return "#F97316";
  return "#FF4D6D";
};

const ScoreRing = ({ score }) => {
  const color = getScoreColor(score);
  const r = 70;
  const c = 2 * Math.PI * r;
  const offset = c - (score / 100) * c;

  return (
    <div className="relative w-[180px] h-[180px] mx-auto" data-testid="shared-score-ring">
      <svg viewBox="0 0 160 160" className="w-full h-full -rotate-90">
        <circle cx="80" cy="80" r={r} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="6" />
        <circle
          cx="80" cy="80" r={r} fill="none" stroke={color} strokeWidth="6"
          strokeLinecap="round" strokeDasharray={c} strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 1s ease-out" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-5xl font-light" style={{ fontFamily: "Fraunces, serif", color }} data-testid="shared-score-value">
          {score}
        </span>
        <span className="text-xs text-muted-foreground mt-1">/100</span>
      </div>
    </div>
  );
};

const SharedReport = () => {
  const { reportId } = useParams();
  const [report, setReport] = useState(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    getSharedReport(reportId)
      .then(setReport)
      .catch(() => setError(true));
  }, [reportId]);

  if (error) {
    return (
      <div className="min-h-screen bg-[#0B132B] flex items-center justify-center px-6">
        <div className="text-center">
          <Shield className="w-12 h-12 text-[#3DD9C5] mx-auto mb-4" />
          <h1 className="text-2xl text-[#E6EDF3] mb-2" style={{ fontFamily: "Fraunces, serif" }}>Report Not Found</h1>
          <p className="text-muted-foreground mb-6">This report may have expired or the link is invalid.</p>
          <Link to="/" className="text-[#3DD9C5] hover:underline">Go to TrustLens</Link>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="min-h-screen bg-[#0B132B] flex items-center justify-center">
        <p className="text-muted-foreground">Loading report...</p>
      </div>
    );
  }

  const pc = report.perception_consistency;
  const color = getScoreColor(report.suspicion_score);

  return (
    <div className="min-h-screen bg-[#0B132B]" data-testid="shared-report-page">
      <div className="container mx-auto px-6 py-12 max-w-2xl">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-12">
          <Link to="/">
            <img src="/trustlens-logo.png" alt="TrustLens" className="h-10 mx-auto mb-8" />
          </Link>
          <p className="text-xs uppercase tracking-widest text-muted-foreground font-mono">
            Anonymized Analysis Report
          </p>
        </motion.div>

        <div className="space-y-8">
          {/* Suspicion Score */}
          <motion.section initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="text-center">
            <p className="text-sm uppercase tracking-widest text-muted-foreground mb-6 font-mono">
              TrustLens Suspicion Score
            </p>
            <ScoreRing score={report.suspicion_score} />
            <p className="mt-4 text-xl font-light" style={{ fontFamily: "Fraunces, serif", color }}>
              {report.suspicion_label}
            </p>
            {report.dominant_pattern && report.dominant_pattern !== "Insufficient data" && (
              <p className="mt-2 text-sm text-muted-foreground">
                Dominant pattern: <span className="text-[#E6EDF3]">{report.dominant_pattern}</span>
              </p>
            )}
          </motion.section>

          {/* Pattern Comparison */}
          {report.pattern_statistics && (
            <motion.section initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
              <Card className="glass-card rounded-2xl">
                <CardContent className="p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <Activity className="w-5 h-5 text-[#3DD9C5]" />
                    <h3 className="text-base font-medium text-[#E6EDF3]">Pattern Comparison</h3>
                  </div>
                  <p className="text-sm text-muted-foreground mb-4">
                    Similar behavioral patterns appear in{" "}
                    <span className="text-[#3DD9C5] font-semibold">{report.pattern_comparison_pct}%</span>{" "}
                    of cases where trust was later broken.
                  </p>
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <p className="text-2xl font-light text-[#FF4D6D]" style={{ fontFamily: "Fraunces, serif" }}>
                        {report.pattern_statistics.confirmed_issues}%
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">confirmed issues</p>
                    </div>
                    <div>
                      <p className="text-2xl font-light text-[#FCA311]" style={{ fontFamily: "Fraunces, serif" }}>
                        {report.pattern_statistics.relationship_conflict}%
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">conflict only</p>
                    </div>
                    <div>
                      <p className="text-2xl font-light text-[#6EE7B7]" style={{ fontFamily: "Fraunces, serif" }}>
                        {report.pattern_statistics.resolved_positively}%
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">resolved positively</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.section>
          )}

          {/* Perception Consistency */}
          {pc && (
            <motion.section initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
              <Card className="glass-card rounded-2xl border-[#FCA311]/20">
                <CardContent className="p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <AlertTriangle className="w-5 h-5 text-[#FCA311]" />
                    <h3 className="text-base font-medium text-[#E6EDF3]">Perception Consistency</h3>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3 leading-relaxed">{pc.insight}</p>
                  {pc.has_inconsistencies && pc.inconsistencies?.map((item, i) => (
                    <p key={i} className="text-sm text-[#FCA311]/80 mb-2 pl-4 border-l-2 border-[#FCA311]/30">{item}</p>
                  ))}
                </CardContent>
              </Card>
            </motion.section>
          )}

          {/* Clarity Actions */}
          {report.clarity_actions?.length > 0 && (
            <motion.section initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
              <Card className="glass-card rounded-2xl">
                <CardContent className="p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <Lightbulb className="w-5 h-5 text-[#3DD9C5]" />
                    <h3 className="text-base font-medium text-[#E6EDF3]">Recommended Actions</h3>
                  </div>
                  <div className="space-y-3">
                    {report.clarity_actions.map((action, i) => (
                      <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-white/5">
                        <div className="w-5 h-5 rounded-full bg-[#3DD9C5]/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                          <span className="text-[10px] font-mono text-[#3DD9C5]">{i + 1}</span>
                        </div>
                        <p className="text-sm text-[#E6EDF3]">{action}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.section>
          )}

          {/* TrustLens Perspective */}
          {report.trustlens_perspective && (
            <motion.section initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
              <Card className="glass-card rounded-2xl border-[#3DD9C5]/20">
                <CardContent className="p-6 text-center">
                  <p className="text-sm text-muted-foreground leading-relaxed italic">
                    "{report.trustlens_perspective}"
                  </p>
                </CardContent>
              </Card>
            </motion.section>
          )}

          {/* Footer disclaimer */}
          <motion.footer initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }} className="text-center pt-8 pb-12">
            <p className="text-xs text-muted-foreground leading-relaxed mb-4">
              This report was generated using TrustLens relationship pattern analysis.
            </p>
            <p className="text-xs text-muted-foreground leading-relaxed mb-6">
              It highlights behavioral patterns and similarities with known relationship situations.
              It does not prove or confirm anything.
            </p>
            <Link to="/" className="text-sm text-[#3DD9C5] hover:underline" data-testid="shared-report-cta">
              Try TrustLens
            </Link>
          </motion.footer>
        </div>
      </div>
    </div>
  );
};

export default SharedReport;

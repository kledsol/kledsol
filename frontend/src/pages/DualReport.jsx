import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrustLensLogo, HeartLensIcon } from "@/components/custom/Logo";
import { useAnalysis } from "@/App";
import { getMirrorStatus, getMirrorReport, consentMirror } from "@/lib/api";
import { toast } from "sonner";
import {
  Users,
  Shield,
  Heart,
  ArrowLeft,
  Loader2,
  CheckCircle,
  Clock,
  Lock,
  Home,
  Brain,
} from "lucide-react";

const getScoreColor = (score) => {
  if (score <= 30) return "#6EE7B7";
  if (score <= 60) return "#FCA311";
  if (score <= 80) return "#F97316";
  return "#FF4D6D";
};

const getGapColor = (gap) => {
  if (gap <= 10) return "#6EE7B7";
  if (gap <= 25) return "#FCA311";
  return "#FF4D6D";
};

const getGapLabel = (level) => {
  if (level === "aligned") return "Aligned";
  if (level === "moderate") return "Moderate Gap";
  return "Significant Gap";
};

const ScoreMiniRing = ({ score, label, partnerLabel }) => {
  const color = getScoreColor(score);
  const radius = 55;
  const circumference = 2 * Math.PI * radius;
  const progress = (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <p className="text-xs text-muted-foreground mb-3 font-mono tracking-wider uppercase">{partnerLabel}</p>
      <div className="relative w-[140px] h-[140px]">
        <svg viewBox="0 0 130 130" className="w-full h-full -rotate-90">
          <circle cx="65" cy="65" r={radius} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="6" />
          <circle
            cx="65" cy="65" r={radius}
            fill="none" stroke={color} strokeWidth="6" strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={circumference - progress}
            style={{ transition: "stroke-dashoffset 1s ease-out" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-light" style={{ fontFamily: "Fraunces, serif", color }}>
            {score}
          </span>
          <span className="text-[10px] text-muted-foreground">/100</span>
        </div>
      </div>
      <p className="text-sm mt-2" style={{ color }}>{label}</p>
    </div>
  );
};

const DualReport = () => {
  const { mirrorId } = useParams();
  const navigate = useNavigate();
  const { sessionId } = useAnalysis();
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState(null);
  const [report, setReport] = useState(null);
  const [consenting, setConsenting] = useState(false);
  const [consentGiven, setConsentGiven] = useState(false);

  // Try to get mirror context from sessionStorage
  const mirrorContext = (() => {
    try {
      return JSON.parse(sessionStorage.getItem("trustlens_mirror") || "null");
    } catch { return null; }
  })();

  const mySessionId = sessionId || mirrorContext?.sessionId;

  useEffect(() => {
    fetchData();
  }, [mirrorId]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const statusData = await getMirrorStatus(mirrorId);
      setStatus(statusData);

      if (statusData.report_ready) {
        const reportData = await getMirrorReport(mirrorId);
        setReport(reportData);
      }
    } catch {
      toast.error("Failed to load mirror session");
    } finally {
      setLoading(false);
    }
  };

  const handleConsent = async () => {
    if (!mySessionId) {
      toast.error("No session found. Please complete your analysis first.");
      return;
    }
    setConsenting(true);
    try {
      const result = await consentMirror(mirrorId, mySessionId);
      setConsentGiven(true);
      toast.success("Consent recorded");
      if (result.report_ready) {
        await fetchData();
      } else {
        // Refresh status
        const statusData = await getMirrorStatus(mirrorId);
        setStatus(statusData);
      }
    } catch (e) {
      toast.error("Failed to record consent. Make sure you've completed your analysis.");
    } finally {
      setConsenting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0B132B] flex items-center justify-center">
        <div className="text-center">
          <HeartLensIcon size={60} animate />
          <p className="mt-6 text-muted-foreground">Loading dual perspective...</p>
        </div>
      </div>
    );
  }

  // Waiting states
  if (!status?.report_ready && !report) {
    const myRole = mirrorContext?.role || (status?.partner_a_consented === false ? "a" : "b");
    const iConsented = myRole === "a" ? status?.partner_a_consented : status?.partner_b_consented;

    return (
      <div className="min-h-screen bg-[#0B132B]">
        <header className="glass border-b border-white/10">
          <div className="container mx-auto px-6 py-4">
            <Link to="/"><TrustLensLogo size="md" /></Link>
          </div>
        </header>

        <main className="container mx-auto px-6 py-16 max-w-xl text-center">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <Users className="w-16 h-16 text-[#3DD9C5] mx-auto mb-6" />
            <h1 className="text-3xl font-light text-[#E6EDF3] mb-6" style={{ fontFamily: "Fraunces, serif" }}>
              Dual Perspective Analysis
            </h1>

            {/* Status Cards */}
            <div className="space-y-4 mb-8 text-left">
              <Card className="glass-card rounded-xl">
                <CardContent className="p-5 flex items-center gap-4">
                  {status?.partner_b_joined ? (
                    <CheckCircle className="w-6 h-6 text-[#3DD9C5] flex-shrink-0" />
                  ) : (
                    <Clock className="w-6 h-6 text-[#FCA311] flex-shrink-0" />
                  )}
                  <div>
                    <p className="text-sm text-[#E6EDF3]">
                      {status?.partner_b_joined ? "Your partner has joined" : "Waiting for your partner to join"}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {status?.partner_b_joined
                        ? status?.partner_b_complete ? "Their analysis is complete" : "They are still completing their analysis"
                        : "Share the invite link so they can begin"}
                    </p>
                  </div>
                </CardContent>
              </Card>

              <Card className="glass-card rounded-xl">
                <CardContent className="p-5 flex items-center gap-4">
                  {status?.partner_a_consented && status?.partner_b_consented ? (
                    <CheckCircle className="w-6 h-6 text-[#3DD9C5] flex-shrink-0" />
                  ) : (
                    <Lock className="w-6 h-6 text-muted-foreground flex-shrink-0" />
                  )}
                  <div>
                    <p className="text-sm text-[#E6EDF3]">Consent Status</p>
                    <p className="text-xs text-muted-foreground">
                      Partner A: {status?.partner_a_consented ? "Consented" : "Pending"} | Partner B: {status?.partner_b_consented ? "Consented" : "Pending"}
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Consent Button */}
            {!iConsented && !consentGiven && (
              <div className="mb-8">
                <Card className="glass-card rounded-xl border-[#3DD9C5]/30">
                  <CardContent className="p-6">
                    <Shield className="w-8 h-8 text-[#3DD9C5] mx-auto mb-4" />
                    <p className="text-sm text-[#E6EDF3] mb-2 font-medium">Ready to share your perspective?</p>
                    <p className="text-sm text-muted-foreground mb-6 leading-relaxed">
                      By consenting, you agree to share your analysis results with your partner.
                      The comparison report will only be generated once both partners consent.
                    </p>
                    <Button
                      onClick={handleConsent}
                      disabled={consenting}
                      className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-8 py-5 btn-glow"
                      data-testid="consent-btn"
                    >
                      {consenting ? (
                        <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Processing...</>
                      ) : (
                        <><Shield className="w-4 h-4 mr-2" />I Consent to Share My Results</>
                      )}
                    </Button>
                  </CardContent>
                </Card>
              </div>
            )}

            {(iConsented || consentGiven) && (
              <p className="text-sm text-[#3DD9C5] mb-8 flex items-center justify-center gap-2">
                <CheckCircle className="w-4 h-4" />
                You have consented. Waiting for your partner...
              </p>
            )}

            <Button
              variant="ghost"
              onClick={() => navigate("/")}
              className="text-muted-foreground hover:text-white"
            >
              <Home className="w-4 h-4 mr-2" />
              Return Home
            </Button>

            <p className="text-xs text-muted-foreground mt-6">
              Refresh this page to check for updates.
            </p>
          </motion.div>
        </main>
      </div>
    );
  }

  // Both consented — show the report
  if (!report) return null;

  const gapLevelColor = report.gap_level === "aligned" ? "#6EE7B7" : report.gap_level === "moderate" ? "#FCA311" : "#FF4D6D";

  return (
    <div className="min-h-screen bg-[#0B132B]">
      <header className="glass border-b border-white/10 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/"><TrustLensLogo size="md" /></Link>
          <Button
            variant="ghost"
            onClick={() => navigate("/")}
            className="text-muted-foreground hover:text-white"
          >
            <Home className="w-4 h-4 mr-2" />
            Home
          </Button>
        </div>
      </header>

      <main className="container mx-auto px-6 py-12 max-w-4xl">
        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[#3DD9C5]/10 mb-6">
            <Users className="w-8 h-8 text-[#3DD9C5]" />
          </div>
          <h1 className="text-3xl sm:text-4xl font-light text-[#E6EDF3] mb-3" style={{ fontFamily: "Fraunces, serif" }} data-testid="dual-report-title">
            Dual Perspective Report
          </h1>
          <p className="text-muted-foreground">
            A comparison of how both partners perceive the relationship
          </p>
        </motion.div>

        <div className="space-y-10">
          {/* Suspicion Scores Side by Side */}
          <motion.section
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            data-testid="dual-scores-section"
          >
            <Card className="glass-card rounded-3xl">
              <CardContent className="p-8">
                <p className="text-sm uppercase tracking-widest text-muted-foreground text-center mb-8 font-mono">
                  Suspicion Scores
                </p>
                <div className="flex items-center justify-center gap-8 sm:gap-16">
                  <ScoreMiniRing
                    score={report.partner_a.suspicion_score}
                    label={report.partner_a.suspicion_label}
                    partnerLabel="Partner A"
                  />
                  <div className="flex flex-col items-center gap-2">
                    <div className="w-px h-20 bg-white/10" />
                    <span className="text-xs font-mono text-muted-foreground">VS</span>
                    <div className="w-px h-20 bg-white/10" />
                  </div>
                  <ScoreMiniRing
                    score={report.partner_b.suspicion_score}
                    label={report.partner_b.suspicion_label}
                    partnerLabel="Partner B"
                  />
                </div>
                <p className="text-center text-sm text-muted-foreground mt-6">
                  Score difference: <span className="text-[#E6EDF3] font-mono">
                    {Math.abs(report.partner_a.suspicion_score - report.partner_b.suspicion_score)}
                  </span> points
                </p>
              </CardContent>
            </Card>
          </motion.section>

          {/* Signals Detected */}
          <motion.section
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            data-testid="dual-signals-section"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[
                { data: report.partner_a, label: "Partner A", color: "#3DD9C5" },
                { data: report.partner_b, label: "Partner B", color: "#FF4D6D" },
              ].map(({ data, label, color }) => (
                <Card key={label} className="glass-card rounded-2xl">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-mono tracking-wider" style={{ color }}>
                      {label} — Signals Detected
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {data.signals_detected?.length > 0 ? (
                        data.signals_detected.map((signal, i) => (
                          <div key={i} className="flex items-center gap-2 text-sm text-[#E6EDF3]">
                            <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: color }} />
                            {signal.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}
                          </div>
                        ))
                      ) : (
                        <p className="text-sm text-muted-foreground">No specific signals detected</p>
                      )}
                    </div>
                    {data.dominant_pattern && data.dominant_pattern !== "Insufficient data" && (
                      <p className="text-xs text-muted-foreground mt-3 pt-3 border-t border-white/10">
                        Dominant pattern: <span className="text-[#E6EDF3]">{data.dominant_pattern}</span>
                      </p>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </motion.section>

          {/* Perception Gap Bars */}
          <motion.section
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            data-testid="perception-gap-section"
          >
            <Card className="glass-card rounded-2xl">
              <CardHeader className="text-center">
                <CardTitle className="text-lg text-[#E6EDF3] font-light" style={{ fontFamily: "Fraunces, serif" }}>
                  Perception Gap Analysis
                </CardTitle>
                <div className="flex items-center justify-center gap-2 mt-2">
                  <span className="text-3xl font-light" style={{ fontFamily: "Fraunces, serif", color: gapLevelColor }}>
                    {report.average_gap}%
                  </span>
                  <span className="text-sm" style={{ color: gapLevelColor }}>
                    {getGapLabel(report.gap_level)}
                  </span>
                </div>
              </CardHeader>
              <CardContent className="space-y-5">
                {Object.entries(report.perception_gaps).map(([key, val], i) => (
                  <motion.div
                    key={key}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 + i * 0.1 }}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-[#E6EDF3] capitalize">
                        {key.replace(/_/g, " ")}
                      </span>
                      <span
                        className="text-xs font-mono"
                        style={{ color: getGapColor(val.gap) }}
                      >
                        Gap: {val.gap}%
                      </span>
                    </div>
                    <div className="relative h-8 bg-white/5 rounded-lg overflow-hidden">
                      {/* Partner A bar */}
                      <div
                        className="absolute left-0 top-0 h-4 rounded-t-lg"
                        style={{
                          width: `${Math.max(val.partner_a, 2)}%`,
                          backgroundColor: "#3DD9C5",
                          opacity: 0.7,
                        }}
                      />
                      {/* Partner B bar */}
                      <div
                        className="absolute left-0 top-4 h-4 rounded-b-lg"
                        style={{
                          width: `${Math.max(val.partner_b, 2)}%`,
                          backgroundColor: "#FF4D6D",
                          opacity: 0.7,
                        }}
                      />
                    </div>
                    <div className="flex justify-between text-[10px] text-muted-foreground mt-1">
                      <span><span className="text-[#3DD9C5]">A</span>: {val.partner_a}%</span>
                      <span><span className="text-[#FF4D6D]">B</span>: {val.partner_b}%</span>
                    </div>
                  </motion.div>
                ))}

                {/* Legend */}
                <div className="flex items-center justify-center gap-6 pt-4 border-t border-white/10">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-[#3DD9C5]" />
                    <span className="text-xs text-muted-foreground">Partner A</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-[#FF4D6D]" />
                    <span className="text-xs text-muted-foreground">Partner B</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.section>

          {/* AI Narrative */}
          <motion.section
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            data-testid="dual-narrative-section"
          >
            <Card className="glass-card rounded-3xl border-[#3DD9C5]/30">
              <CardContent className="p-10">
                <div className="flex flex-col items-center text-center">
                  <Brain className="w-10 h-10 text-[#3DD9C5] mb-6" />
                  <h3 className="text-xl font-light text-[#E6EDF3] mb-6" style={{ fontFamily: "Fraunces, serif" }}>
                    TrustLens Perspective
                  </h3>
                  <p className="text-muted-foreground leading-relaxed max-w-2xl text-lg">
                    {report.narrative}
                  </p>
                </div>
              </CardContent>
            </Card>
          </motion.section>

          {/* Privacy Note & Actions */}
          <motion.section
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="text-center py-8"
          >
            <Shield className="w-8 h-8 text-[#3DD9C5] mx-auto mb-6" />
            <p className="text-muted-foreground leading-relaxed mb-2 max-w-lg mx-auto">
              This comparison was generated after both partners explicitly consented to share their analyses.
              No data was shared without permission.
            </p>
            <p className="text-muted-foreground leading-relaxed mb-8 max-w-lg mx-auto text-sm">
              This report highlights perception differences. It does not prove or confirm anything.
              Consider using these insights as a starting point for open conversation.
            </p>

            <Button
              onClick={() => navigate("/")}
              variant="ghost"
              className="text-muted-foreground hover:text-white hover:bg-white/5 rounded-full"
            >
              <Home className="w-4 h-4 mr-2" />
              Return Home
            </Button>
          </motion.section>
        </div>
      </main>
    </div>
  );
};

export default DualReport;

import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { TrustLensLogo, HeartLensIcon } from "@/components/custom/Logo";
import { StabilityHearts } from "@/components/custom/StabilityHearts";
import { useAnalysis } from "@/App";
import { submitMirrorMode } from "@/lib/api";
import { toast } from "sonner";
import { ArrowLeft, Users, Heart, MessageSquare, Shield, ChevronRight, AlertTriangle } from "lucide-react";

const MirrorMode = () => {
  const { sessionId } = useAnalysis();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState("input"); // input | results
  const [results, setResults] = useState(null);

  const [partnerView, setPartnerView] = useState({
    partner_emotional: 5,
    partner_communication: 5,
    partner_trust: 5,
  });

  const handleSubmit = async () => {
    if (!sessionId) {
      toast.error("No active session. Please start an analysis first.");
      navigate("/");
      return;
    }

    setLoading(true);
    try {
      const response = await submitMirrorMode({
        session_id: sessionId,
        ...partnerView,
      });
      setResults(response);
      setStep("results");
    } catch (e) {
      toast.error("Failed to analyze perception gap");
    } finally {
      setLoading(false);
    }
  };

  const questions = [
    {
      key: "partner_emotional",
      icon: Heart,
      label: "Emotional Connection",
      description: "How do you think your partner views your emotional bond?",
      low: "They feel distant",
      high: "They feel very close",
    },
    {
      key: "partner_communication",
      icon: MessageSquare,
      label: "Communication Quality",
      description: "How would your partner rate your communication?",
      low: "Poor",
      high: "Excellent",
    },
    {
      key: "partner_trust",
      icon: Shield,
      label: "Trust Level",
      description: "How much do you think your partner trusts you?",
      low: "Low trust",
      high: "Complete trust",
    },
  ];

  if (step === "results" && results) {
    const { perception_gap, has_significant_mismatch, insight } = results;

    return (
      <div className="min-h-screen bg-[#0B132B]">
        <header className="glass border-b border-white/10">
          <div className="container mx-auto px-6 py-4 flex items-center justify-between">
            <Link to="/">
              <TrustLensLogo size="md" />
            </Link>
          </div>
        </header>

        <main className="container mx-auto px-6 py-12 max-w-3xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="text-center mb-12">
              <HeartLensIcon size={60} />
              <h1 className="text-3xl font-light text-[#E6EDF3] mt-6 mb-4" style={{ fontFamily: 'Fraunces, serif' }}>
                Perception Gap Analysis
              </h1>
              {has_significant_mismatch && (
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#FF4D6D]/20 text-[#FF4D6D]">
                  <AlertTriangle className="w-4 h-4" />
                  <span className="text-sm">Significant mismatch detected</span>
                </div>
              )}
            </div>

            {/* Comparison Visualization */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <Card className="glass-card rounded-2xl">
                <CardHeader>
                  <CardTitle className="text-base text-[#E6EDF3]">Your Perception</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {["emotional", "communication", "trust"].map((key) => (
                    <div key={key} className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground capitalize">{key}</span>
                      <div className="flex items-center gap-1">
                        {[...Array(5)].map((_, i) => (
                          <Heart
                            key={i}
                            className={`w-4 h-4 ${
                              i < perception_gap.user_view[key]
                                ? "fill-[#3DD9C5] text-[#3DD9C5]"
                                : "fill-none text-white/20"
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              <Card className="glass-card rounded-2xl">
                <CardHeader>
                  <CardTitle className="text-base text-[#E6EDF3]">Partner's Perception (Your Estimate)</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {["emotional", "communication", "trust"].map((key) => (
                    <div key={key} className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground capitalize">{key}</span>
                      <div className="flex items-center gap-1">
                        {[...Array(5)].map((_, i) => (
                          <Heart
                            key={i}
                            className={`w-4 h-4 ${
                              i < perception_gap.partner_view[key]
                                ? "fill-[#FF4D6D] text-[#FF4D6D]"
                                : "fill-none text-white/20"
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>

            {/* Gap Analysis */}
            <Card className="glass-card rounded-2xl mb-8">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base text-[#E6EDF3]">
                  <Users className="w-5 h-5 text-[#3DD9C5]" />
                  Gap Analysis
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {["emotional", "communication", "trust"].map((key) => {
                  const gap = perception_gap[key];
                  return (
                    <div key={key}>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-[#E6EDF3] capitalize">{key} gap</span>
                        <span className={`font-mono ${gap > 2 ? "text-[#FF4D6D]" : gap > 1 ? "text-[#FCA311]" : "text-[#6EE7B7]"}`}>
                          {gap} point{gap !== 1 ? "s" : ""}
                        </span>
                      </div>
                      <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${gap > 2 ? "bg-[#FF4D6D]" : gap > 1 ? "bg-[#FCA311]" : "bg-[#6EE7B7]"}`}
                          style={{ width: `${(gap / 5) * 100}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </CardContent>
            </Card>

            {/* Insight */}
            <Card className="glass-card rounded-2xl border-[#3DD9C5]/30 mb-8">
              <CardContent className="p-6">
                <p className="text-muted-foreground leading-relaxed">{insight}</p>
              </CardContent>
            </Card>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                onClick={() => navigate("/results")}
                variant="outline"
                className="border-white/20 text-white hover:bg-white/5 rounded-full px-8 py-6"
              >
                <ArrowLeft className="w-5 h-5 mr-2" />
                Back to Results
              </Button>
              <Button
                onClick={() => navigate("/coach")}
                className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-8 py-6 btn-glow"
              >
                <MessageSquare className="w-5 h-5 mr-2" />
                Conversation Coach
                <ChevronRight className="w-5 h-5 ml-2" />
              </Button>
            </div>
          </motion.div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0B132B]">
      <header className="glass border-b border-white/10">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate("/results")}
              className="text-white hover:bg-white/10"
              data-testid="back-btn"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <TrustLensLogo size="md" />
          </div>
          <span className="text-sm text-muted-foreground font-mono">Mirror Mode</span>
        </div>
      </header>

      <main className="container mx-auto px-6 py-12 max-w-2xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="text-center mb-12">
            <Users className="w-12 h-12 text-[#3DD9C5] mx-auto mb-4" />
            <h1 className="text-3xl font-light text-[#E6EDF3] mb-4" style={{ fontFamily: 'Fraunces, serif' }}>
              Mirror Mode
            </h1>
            <p className="text-muted-foreground max-w-lg mx-auto">
              Imagine how your partner might view your relationship. This helps identify
              potential perception gaps that could benefit from open discussion.
            </p>
          </div>

          <div className="space-y-6">
            {questions.map((q, index) => (
              <motion.div
                key={q.key}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="glass-card rounded-xl">
                  <CardContent className="p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-10 h-10 rounded-lg bg-[#3DD9C5]/10 flex items-center justify-center">
                        <q.icon className="w-5 h-5 text-[#3DD9C5]" />
                      </div>
                      <div>
                        <h3 className="font-medium text-[#E6EDF3]">{q.label}</h3>
                        <p className="text-sm text-muted-foreground">{q.description}</p>
                      </div>
                    </div>
                    <Slider
                      value={[partnerView[q.key]]}
                      onValueChange={(v) => setPartnerView((p) => ({ ...p, [q.key]: v[0] }))}
                      min={1}
                      max={10}
                      step={1}
                      className="my-4"
                      data-testid={`slider-${q.key}`}
                    />
                    <div className="flex justify-between text-sm text-muted-foreground">
                      <span>{q.low}</span>
                      <span className="font-mono text-[#3DD9C5]">{partnerView[q.key]}/10</span>
                      <span>{q.high}</span>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>

          <div className="mt-10 flex justify-center">
            <Button
              onClick={handleSubmit}
              disabled={loading}
              size="lg"
              className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-10 py-6 text-lg btn-glow"
              data-testid="analyze-btn"
            >
              {loading ? "Analyzing..." : "Analyze Perception Gap"}
              <ChevronRight className="w-5 h-5 ml-2" />
            </Button>
          </div>
        </motion.div>
      </main>
    </div>
  );
};

export default MirrorMode;

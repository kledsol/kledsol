import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { TrustLensLogo } from "@/components/custom/Logo";
import { StabilityHearts, StabilityLabel } from "@/components/custom/StabilityHearts";
import { useAnalysis } from "@/App";
import { submitPulse, startAnalysis } from "@/lib/api";
import { toast } from "sonner";
import { ArrowLeft, Heart, MessageSquare, Zap, ChevronRight, Activity } from "lucide-react";

const RelationshipPulse = () => {
  const { sessionId, setSessionId, setAnalysisData } = useAnalysis();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState("questions"); // questions | results
  const [results, setResults] = useState(null);

  const [formData, setFormData] = useState({
    emotional_connection: 3,
    communication_quality: 3,
    perceived_tension: 3,
  });

  const handleSubmit = async () => {
    setLoading(true);
    try {
      let currentSessionId = sessionId;
      if (!currentSessionId) {
        const session = await startAnalysis("pulse");
        currentSessionId = session.session_id;
        setSessionId(currentSessionId);
      }

      const response = await submitPulse({
        session_id: currentSessionId,
        ...formData,
      });

      setResults(response);
      setAnalysisData((prev) => ({
        ...prev,
        trustIndex: response.trust_disruption_index,
        stabilityHearts: response.stability_hearts,
      }));
      setStep("results");
    } catch (error) {
      console.error("Failed to submit pulse:", error);
      toast.error("Failed to analyze. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const questions = [
    {
      key: "emotional_connection",
      icon: Heart,
      label: "Emotional Connection",
      description: "How emotionally connected do you feel to your partner right now?",
      low: "Distant",
      high: "Very Close",
    },
    {
      key: "communication_quality",
      icon: MessageSquare,
      label: "Communication Quality",
      description: "How would you rate your current communication?",
      low: "Poor",
      high: "Excellent",
    },
    {
      key: "perceived_tension",
      icon: Zap,
      label: "Perceived Tension",
      description: "How much tension or strain do you feel in your relationship?",
      low: "None",
      high: "Significant",
    },
  ];

  if (step === "results" && results) {
    return (
      <div className="min-h-screen bg-[#0B132B] relative">
        <header className="glass border-b border-white/10">
          <div className="container mx-auto px-6 py-4 flex items-center justify-between">
            <TrustLensLogo size="md" />
          </div>
        </header>

        <main className="container mx-auto px-6 py-16 max-w-2xl">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7 }}
            className="text-center"
          >
            <div className="mb-8">
              <StabilityHearts count={results.stability_hearts} size="lg" />
            </div>

            <h1
              className="text-4xl font-light text-[#E6EDF3] mb-4"
              style={{ fontFamily: 'Fraunces, serif' }}
            >
              Relationship Pulse
            </h1>

            <div className="text-2xl mb-8">
              <StabilityLabel hearts={results.stability_hearts} />
            </div>

            <Card className="glass-card rounded-2xl mb-8">
              <CardContent className="p-8">
                <p className="text-muted-foreground leading-relaxed">
                  {results.stability_hearts >= 3
                    ? "Your relationship pulse indicates a generally healthy connection. Continue nurturing your bond through open communication and quality time together."
                    : results.stability_hearts >= 2
                    ? "Your relationship is experiencing some strain. This is normal during challenging times. Consider having an open conversation about how you're both feeling."
                    : "Your relationship appears to be under significant stress. This might be a good time to prioritize communication or consider professional support."}
                </p>
              </CardContent>
            </Card>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                onClick={() => navigate("/analysis")}
                size="lg"
                className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-8 py-6 btn-glow"
                data-testid="deep-analysis-btn"
              >
                <Activity className="w-5 h-5 mr-2" />
                Start Deep Analysis
              </Button>
              <Button
                onClick={() => navigate("/")}
                variant="outline"
                size="lg"
                className="border-white/20 text-white hover:bg-white/5 rounded-full px-8 py-6"
              >
                Return Home
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
              onClick={() => navigate("/clarity")}
              className="text-white hover:bg-white/10"
              data-testid="back-btn"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <TrustLensLogo size="md" />
          </div>
          <span className="text-sm text-muted-foreground font-mono">30-Second Check</span>
        </div>
      </header>

      <main className="container mx-auto px-6 py-12 max-w-2xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="text-center mb-12">
            <h1
              className="text-3xl md:text-4xl font-light text-[#E6EDF3] mb-4"
              style={{ fontFamily: 'Fraunces, serif' }}
            >
              Quick Relationship Pulse
            </h1>
            <p className="text-muted-foreground">
              Answer three quick questions to get an instant read on your relationship health.
            </p>
          </div>

          <div className="space-y-8">
            {questions.map((q, index) => (
              <motion.div
                key={q.key}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <Card className="glass-card rounded-2xl">
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
                    <div className="px-2">
                      <Slider
                        value={[formData[q.key]]}
                        onValueChange={(value) =>
                          setFormData((prev) => ({ ...prev, [q.key]: value[0] }))
                        }
                        min={1}
                        max={5}
                        step={1}
                        className="my-4"
                        data-testid={`slider-${q.key}`}
                      />
                      <div className="flex justify-between text-sm text-muted-foreground">
                        <span>{q.low}</span>
                        <span className="font-mono text-[#3DD9C5]">{formData[q.key]}/5</span>
                        <span>{q.high}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="mt-10 flex justify-center"
          >
            <Button
              onClick={handleSubmit}
              disabled={loading}
              size="lg"
              className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-10 py-6 text-lg btn-glow"
              data-testid="submit-pulse-btn"
            >
              {loading ? "Analyzing..." : "Get My Pulse Reading"}
              <ChevronRight className="w-5 h-5 ml-2" />
            </Button>
          </motion.div>
        </motion.div>
      </main>
    </div>
  );
};

export default RelationshipPulse;

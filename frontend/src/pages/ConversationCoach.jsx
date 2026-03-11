import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrustLensLogo, HeartLensIcon } from "@/components/custom/Logo";
import { useAnalysis } from "@/App";
import { getConversationGuidance } from "@/lib/api";
import { toast } from "sonner";
import {
  ArrowLeft,
  MessageSquare,
  Heart,
  AlertTriangle,
  Eye,
  ChevronRight,
  Loader2,
  CheckCircle,
  XCircle,
  Shield,
  Clock,
  Brain,
  Sparkles,
} from "lucide-react";

const tones = [
  { value: "gentle", label: "Gentle & Caring", desc: "Soft approach, focus on feelings" },
  { value: "direct", label: "Direct & Honest", desc: "Clear communication, focus on facts" },
  { value: "curious", label: "Curious & Open", desc: "Ask questions, seek understanding" },
  { value: "supportive", label: "Supportive & Reassuring", desc: "Express commitment, offer support" },
];

const topics = [
  { value: "recent_changes", label: "Recent Changes", desc: "Discuss behavioral changes you've noticed" },
  { value: "feelings", label: "Your Feelings", desc: "Share how you've been feeling lately" },
  { value: "communication", label: "Communication", desc: "Talk about how you communicate" },
  { value: "future", label: "The Future", desc: "Discuss plans and expectations" },
  { value: "trust", label: "Trust & Transparency", desc: "Address trust and openness" },
];

const SectionCard = ({ icon: Icon, title, color = "#3DD9C5", borderColor, children, testId }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5 }}
  >
    <Card className={`glass-card rounded-2xl mb-6 ${borderColor || ""}`} data-testid={testId}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base text-[#E6EDF3]">
          <Icon className="w-5 h-5" style={{ color }} />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  </motion.div>
);

const ConversationCoach = () => {
  const { sessionId } = useAnalysis();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState("input");
  const [guidance, setGuidance] = useState(null);
  const [formData, setFormData] = useState({ tone: "", topic: "" });

  const handleGetGuidance = async () => {
    if (!formData.tone || !formData.topic) {
      toast.error("Please select a tone and topic");
      return;
    }
    if (!sessionId) {
      toast.error("No active session. Please start an analysis first.");
      navigate("/");
      return;
    }
    setLoading(true);
    try {
      const response = await getConversationGuidance({
        session_id: sessionId,
        tone: formData.tone,
        topic: formData.topic,
      });
      setGuidance(response);
      setStep("guidance");
    } catch {
      toast.error("Failed to generate guidance");
    } finally {
      setLoading(false);
    }
  };

  // ======= GUIDANCE VIEW =======
  if (step === "guidance" && guidance) {
    const selectedTone = tones.find((t) => t.value === formData.tone)?.label;
    const selectedTopic = topics.find((t) => t.value === formData.topic)?.label;

    return (
      <div className="min-h-screen bg-[#0B132B]">
        <header className="glass border-b border-white/10">
          <div className="container mx-auto px-6 py-4 flex items-center justify-between">
            <Link to="/"><TrustLensLogo size="md" /></Link>
            <span className="text-sm text-muted-foreground font-mono">Conversation Coach</span>
          </div>
        </header>

        <main className="container mx-auto px-6 py-12 max-w-3xl">
          <AnimatePresence>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
              {/* Header */}
              <div className="text-center mb-10">
                <MessageSquare className="w-12 h-12 text-[#3DD9C5] mx-auto mb-4" />
                <h1 className="text-3xl font-light text-[#E6EDF3] mb-2" style={{ fontFamily: "Fraunces, serif" }} data-testid="guidance-title">
                  Your Conversation Guide
                </h1>
                <p className="text-muted-foreground">
                  {selectedTone} approach for discussing {selectedTopic?.toLowerCase()}
                </p>
              </div>

              {/* Conversation Framing */}
              {guidance.framing && (
                <SectionCard icon={Brain} title="Conversation Framing" testId="framing-section">
                  <div className="space-y-4">
                    <div className="p-4 rounded-xl bg-[#3DD9C5]/5 border border-[#3DD9C5]/10">
                      <p className="text-sm font-medium text-[#3DD9C5] mb-1">Approach</p>
                      <p className="text-[#E6EDF3] leading-relaxed text-sm">{guidance.framing.approach}</p>
                    </div>
                    <div className="p-4 rounded-xl bg-white/5">
                      <p className="text-sm font-medium text-[#E6EDF3] mb-1">Tone Guidance</p>
                      <p className="text-muted-foreground leading-relaxed text-sm">{guidance.framing.tone_guidance}</p>
                    </div>
                    <div className="flex items-start gap-3 p-4 rounded-xl bg-white/5">
                      <Clock className="w-5 h-5 text-[#FCA311] mt-0.5 flex-shrink-0" />
                      <div>
                        <p className="text-sm font-medium text-[#E6EDF3] mb-1">Timing</p>
                        <p className="text-muted-foreground text-sm">{guidance.framing.timing_suggestion}</p>
                      </div>
                    </div>
                  </div>
                </SectionCard>
              )}

              {/* Suggested Opening Lines */}
              <SectionCard icon={Sparkles} title="Suggested Opening Lines" testId="openings-section">
                <div className="space-y-3">
                  {(guidance.openings || [guidance.opening]).map((line, i) => (
                    <div key={i} className="flex items-start gap-3 p-4 rounded-xl bg-white/5">
                      <span className="w-6 h-6 rounded-full bg-[#3DD9C5]/20 flex items-center justify-center flex-shrink-0 text-xs font-mono text-[#3DD9C5]">
                        {i + 1}
                      </span>
                      <p className="text-[#E6EDF3] leading-relaxed italic" data-testid={`opening-${i}`}>"{line}"</p>
                    </div>
                  ))}
                </div>
              </SectionCard>

              {/* Questions to Ask */}
              <SectionCard icon={MessageSquare} title="Questions to Ask" testId="questions-section">
                <div className="space-y-3">
                  {guidance.questions?.map((q, i) => (
                    <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-white/5">
                      <span className="w-6 h-6 rounded-full bg-[#3DD9C5]/20 flex items-center justify-center flex-shrink-0 text-xs font-mono text-[#3DD9C5]">
                        {i + 1}
                      </span>
                      <p className="text-[#E6EDF3] text-sm leading-relaxed" data-testid={`question-${i}`}>{q}</p>
                    </div>
                  ))}
                </div>
              </SectionCard>

              {/* Emotional Preparation */}
              {guidance.emotional_preparation && (
                <SectionCard icon={Heart} title="Emotional Preparation" color="#FF4D6D" testId="emotional-prep-section">
                  <div className="space-y-4">
                    {[
                      { key: "before", label: "Before the Conversation", color: "#3DD9C5" },
                      { key: "during", label: "During the Conversation", color: "#FCA311" },
                      { key: "if_difficult", label: "If Things Get Difficult", color: "#FF4D6D" },
                    ].map(({ key, label, color }) => (
                      guidance.emotional_preparation[key] && (
                        <div key={key} className="p-4 rounded-xl bg-white/5">
                          <p className="text-sm font-medium mb-1.5" style={{ color }}>{label}</p>
                          <p className="text-muted-foreground text-sm leading-relaxed">
                            {guidance.emotional_preparation[key]}
                          </p>
                        </div>
                      )
                    ))}
                  </div>
                </SectionCard>
              )}

              {/* Things to Avoid */}
              <SectionCard icon={AlertTriangle} title="Things to Avoid" color="#FF4D6D" borderColor="border-[#FF4D6D]/20" testId="avoid-section">
                <div className="space-y-2">
                  {guidance.avoid?.map((item, i) => (
                    <div key={i} className="flex items-start gap-2.5">
                      <XCircle className="w-4 h-4 text-[#FF4D6D] mt-0.5 flex-shrink-0" />
                      <span className="text-muted-foreground text-sm">{item}</span>
                    </div>
                  ))}
                </div>
              </SectionCard>

              {/* What to Observe */}
              <SectionCard icon={Eye} title="What to Observe" testId="observe-section">
                <div className="space-y-2">
                  {guidance.observe?.map((item, i) => (
                    <div key={i} className="flex items-start gap-2.5">
                      <CheckCircle className="w-4 h-4 text-[#6EE7B7] mt-0.5 flex-shrink-0" />
                      <span className="text-[#E6EDF3] text-sm">{item}</span>
                    </div>
                  ))}
                </div>
              </SectionCard>

              {/* Disclaimer */}
              <Card className="glass-card rounded-2xl border-[#3DD9C5]/20 mb-8">
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <Shield className="w-8 h-8 text-[#3DD9C5] flex-shrink-0" />
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      Remember: The goal is understanding, not confrontation. Approach the conversation with
                      an open heart and genuine curiosity. Your partner's response may reveal important insights
                      regardless of the outcome. This guide is personalized based on your analysis, but every
                      relationship is unique — trust your instincts.
                    </p>
                  </div>
                </CardContent>
              </Card>

              {/* Actions */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button
                  onClick={() => setStep("input")}
                  variant="outline"
                  className="border-white/20 text-white hover:bg-white/5 rounded-full px-8 py-6"
                  data-testid="adjust-approach-btn"
                >
                  <ArrowLeft className="w-5 h-5 mr-2" />
                  Adjust Approach
                </Button>
                <Button
                  onClick={() => navigate("/results")}
                  className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-8 py-6 btn-glow"
                  data-testid="back-to-results-btn"
                >
                  Back to Results
                  <ChevronRight className="w-5 h-5 ml-2" />
                </Button>
              </div>
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    );
  }

  // ======= INPUT VIEW =======
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
          <span className="text-sm text-muted-foreground font-mono">Conversation Coach</span>
        </div>
      </header>

      <main className="container mx-auto px-6 py-12 max-w-2xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="text-center mb-12">
            <MessageSquare className="w-12 h-12 text-[#3DD9C5] mx-auto mb-4" />
            <h1 className="text-3xl font-light text-[#E6EDF3] mb-4" style={{ fontFamily: "Fraunces, serif" }} data-testid="coach-title">
              Conversation Coach
            </h1>
            <p className="text-muted-foreground max-w-lg mx-auto">
              Prepare for a meaningful conversation with your partner. Choose your approach
              and topic to receive personalized, AI-guided communication strategies.
            </p>
          </div>

          <div className="space-y-8">
            {/* Tone Selection */}
            <div>
              <h3 className="text-sm font-medium text-[#E6EDF3] mb-4">How do you want to approach this?</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {tones.map((tone) => (
                  <button
                    key={tone.value}
                    onClick={() => setFormData((p) => ({ ...p, tone: tone.value }))}
                    className={`p-4 rounded-xl text-left transition-all ${
                      formData.tone === tone.value
                        ? "bg-[#3DD9C5]/10 border-2 border-[#3DD9C5]"
                        : "glass-card hover:border-[#3DD9C5]/30"
                    }`}
                    data-testid={`tone-${tone.value}`}
                  >
                    <h4 className={formData.tone === tone.value ? "text-[#3DD9C5]" : "text-[#E6EDF3]"}>
                      {tone.label}
                    </h4>
                    <p className="text-sm text-muted-foreground">{tone.desc}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Topic Selection */}
            <div>
              <h3 className="text-sm font-medium text-[#E6EDF3] mb-4">What do you want to talk about?</h3>
              <div className="space-y-3">
                {topics.map((topic) => (
                  <button
                    key={topic.value}
                    onClick={() => setFormData((p) => ({ ...p, topic: topic.value }))}
                    className={`w-full p-4 rounded-xl text-left transition-all flex items-center gap-4 ${
                      formData.topic === topic.value
                        ? "bg-[#3DD9C5]/10 border-2 border-[#3DD9C5]"
                        : "glass-card hover:border-[#3DD9C5]/30"
                    }`}
                    data-testid={`topic-${topic.value}`}
                  >
                    <div className={`w-4 h-4 rounded-full border-2 ${
                      formData.topic === topic.value ? "border-[#3DD9C5] bg-[#3DD9C5]" : "border-white/30"
                    }`} />
                    <div>
                      <h4 className={formData.topic === topic.value ? "text-[#3DD9C5]" : "text-[#E6EDF3]"}>
                        {topic.label}
                      </h4>
                      <p className="text-sm text-muted-foreground">{topic.desc}</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-10 flex justify-center">
            <Button
              onClick={handleGetGuidance}
              disabled={loading || !formData.tone || !formData.topic}
              size="lg"
              className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-10 py-6 text-lg btn-glow"
              data-testid="get-guidance-btn"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Generating Your Guide...
                </>
              ) : (
                <>
                  Get Conversation Guide
                  <ChevronRight className="w-5 h-5 ml-2" />
                </>
              )}
            </Button>
          </div>
        </motion.div>
      </main>
    </div>
  );
};

export default ConversationCoach;

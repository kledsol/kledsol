import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
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
} from "lucide-react";

const ConversationCoach = () => {
  const { sessionId } = useAnalysis();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState("input"); // input | guidance
  const [guidance, setGuidance] = useState(null);

  const [formData, setFormData] = useState({
    tone: "",
    topic: "",
  });

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
    } catch (e) {
      toast.error("Failed to generate guidance");
    } finally {
      setLoading(false);
    }
  };

  if (step === "guidance" && guidance) {
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
              <MessageSquare className="w-12 h-12 text-[#3DD9C5] mx-auto mb-4" />
              <h1 className="text-3xl font-light text-[#E6EDF3] mb-2" style={{ fontFamily: 'Fraunces, serif' }}>
                Conversation Guide
              </h1>
              <p className="text-muted-foreground">
                {tones.find(t => t.value === formData.tone)?.label} approach for discussing {topics.find(t => t.value === formData.topic)?.label.toLowerCase()}
              </p>
            </div>

            {/* Opening Statement */}
            <Card className="glass-card rounded-2xl mb-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base text-[#E6EDF3]">
                  <Heart className="w-5 h-5 text-[#3DD9C5]" />
                  Suggested Opening
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-[#E6EDF3] leading-relaxed italic">"{guidance.opening}"</p>
              </CardContent>
            </Card>

            {/* Questions to Ask */}
            <Card className="glass-card rounded-2xl mb-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base text-[#E6EDF3]">
                  <MessageSquare className="w-5 h-5 text-[#3DD9C5]" />
                  Questions to Ask
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {guidance.questions?.map((q, i) => (
                  <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-white/5">
                    <span className="w-6 h-6 rounded-full bg-[#3DD9C5]/20 flex items-center justify-center flex-shrink-0 text-xs font-mono text-[#3DD9C5]">
                      {i + 1}
                    </span>
                    <p className="text-[#E6EDF3]">{q}</p>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Things to Avoid */}
            <Card className="glass-card rounded-2xl mb-6 border-[#FF4D6D]/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base text-[#E6EDF3]">
                  <AlertTriangle className="w-5 h-5 text-[#FF4D6D]" />
                  Things to Avoid
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {guidance.avoid?.map((item, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <XCircle className="w-4 h-4 text-[#FF4D6D]" />
                    <span className="text-muted-foreground">{item}</span>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* What to Observe */}
            <Card className="glass-card rounded-2xl mb-8">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base text-[#E6EDF3]">
                  <Eye className="w-5 h-5 text-[#3DD9C5]" />
                  What to Observe
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {guidance.observe?.map((item, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-[#6EE7B7]" />
                    <span className="text-[#E6EDF3]">{item}</span>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Disclaimer */}
            <Card className="glass-card rounded-2xl border-[#3DD9C5]/20 mb-8">
              <CardContent className="p-6">
                <div className="flex items-start gap-4">
                  <HeartLensIcon size={32} />
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    Remember: The goal is understanding, not confrontation. Approach the conversation with
                    an open heart and genuine curiosity. Your partner's response may reveal important insights
                    regardless of the outcome.
                  </p>
                </div>
              </CardContent>
            </Card>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                onClick={() => setStep("input")}
                variant="outline"
                className="border-white/20 text-white hover:bg-white/5 rounded-full px-8 py-6"
              >
                <ArrowLeft className="w-5 h-5 mr-2" />
                Adjust Approach
              </Button>
              <Button
                onClick={() => navigate("/results")}
                className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-8 py-6 btn-glow"
              >
                Back to Results
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
          <span className="text-sm text-muted-foreground font-mono">Conversation Coach</span>
        </div>
      </header>

      <main className="container mx-auto px-6 py-12 max-w-2xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="text-center mb-12">
            <MessageSquare className="w-12 h-12 text-[#3DD9C5] mx-auto mb-4" />
            <h1 className="text-3xl font-light text-[#E6EDF3] mb-4" style={{ fontFamily: 'Fraunces, serif' }}>
              Conversation Coach
            </h1>
            <p className="text-muted-foreground max-w-lg mx-auto">
              Let us help you prepare for a meaningful conversation with your partner.
              Choose your approach and topic to get personalized guidance.
            </p>
          </div>

          <div className="space-y-8">
            {/* Tone Selection */}
            <div>
              <h3 className="text-sm font-medium text-[#E6EDF3] mb-4">Select Your Tone</h3>
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
              <h3 className="text-sm font-medium text-[#E6EDF3] mb-4">Select Your Topic</h3>
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
                  Preparing Guidance...
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

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { TrustLensLogo, HeartLensIcon } from "@/components/custom/Logo";
import { StabilityHearts } from "@/components/custom/StabilityHearts";
import { useAnalysis } from "@/App";
import {
  startAnalysis,
  submitBaseline,
  submitChanges,
  submitTimeline,
  getNextQuestion,
  submitAnswer,
} from "@/lib/api";
import { toast } from "sonner";
import {
  ArrowLeft,
  ArrowRight,
  Check,
  Brain,
  Clock,
  MessageSquare,
  Heart,
  Smartphone,
  Users,
  CreditCard,
  HeartPulse,
  Loader2,
} from "lucide-react";

const STEPS = [
  { id: "baseline", label: "Baseline", icon: Heart },
  { id: "changes", label: "Changes", icon: Clock },
  { id: "timeline", label: "Timeline", icon: Clock },
  { id: "investigation", label: "Investigation", icon: Brain },
];

const DeepAnalysis = () => {
  const { sessionId, setSessionId, currentStep, setCurrentStep, setAnalysisData } =
    useAnalysis();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [localStep, setLocalStep] = useState(0);

  // Form states
  const [baseline, setBaseline] = useState({
    relationship_duration: "",
    prior_satisfaction: 7,
    communication_habits: "",
    emotional_closeness: 7,
    transparency_level: 7,
  });
  const [selectedChanges, setSelectedChanges] = useState([]);
  const [timeline, setTimeline] = useState({
    when_started: "",
    gradual_or_sudden: "",
    multiple_at_once: false,
  });
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [selectedAnswer, setSelectedAnswer] = useState("");
  const [customAnswer, setCustomAnswer] = useState("");
  const [questionsAnswered, setQuestionsAnswered] = useState(0);
  const [trustIndex, setTrustIndex] = useState(0);
  const [stabilityHearts, setStabilityHearts] = useState(4);
  const [fetchingQuestion, setFetchingQuestion] = useState(false);
  const [questionStage, setQuestionStage] = useState("core"); // core | adaptive | complete
  const [transitionMessage, setTransitionMessage] = useState("");
  const [showTransition, setShowTransition] = useState(false);

  const MIN_QUESTIONS = 5;

  useEffect(() => {
    const initSession = async () => {
      if (!sessionId) {
        try {
          const session = await startAnalysis("deep");
          setSessionId(session.session_id);
        } catch (e) {
          toast.error("Failed to start session");
          navigate("/");
        }
      }
    };
    initSession();
  }, []);

  const changeCategories = [
    { id: "routine_changes", icon: Clock, label: "Routine Changes", desc: "Schedule modifications, late returns" },
    { id: "communication_changes", icon: MessageSquare, label: "Communication", desc: "Shorter conversations, delayed responses" },
    { id: "emotional_distance", icon: Heart, label: "Emotional Distance", desc: "Detachment, reduced affection" },
    { id: "digital_behavior", icon: Smartphone, label: "Digital Behavior", desc: "Phone secrecy, hidden notifications" },
    { id: "social_life", icon: Users, label: "Social Life", desc: "New social circles, frequent outings" },
    { id: "financial_anomalies", icon: CreditCard, label: "Financial", desc: "Unusual expenses, secretive spending" },
    { id: "intimacy_changes", icon: HeartPulse, label: "Intimacy", desc: "Changes in physical connection" },
  ];

  const handleBaselineSubmit = async () => {
    if (!baseline.relationship_duration || !baseline.communication_habits) {
      toast.error("Please complete all required fields");
      return;
    }
    setLoading(true);
    try {
      await submitBaseline({ session_id: sessionId, ...baseline });
      setLocalStep(1);
    } catch (e) {
      toast.error("Failed to save baseline");
    } finally {
      setLoading(false);
    }
  };

  const handleChangesSubmit = async () => {
    if (selectedChanges.length === 0) {
      toast.error("Please select at least one change category");
      return;
    }
    setLoading(true);
    try {
      await submitChanges({ session_id: sessionId, categories: selectedChanges });
      setLocalStep(2);
    } catch (e) {
      toast.error("Failed to save changes");
    } finally {
      setLoading(false);
    }
  };

  const handleTimelineSubmit = async () => {
    if (!timeline.when_started || !timeline.gradual_or_sudden) {
      toast.error("Please complete all fields");
      return;
    }
    setLoading(true);
    try {
      await submitTimeline({ session_id: sessionId, ...timeline });
      setLocalStep(3);
      fetchNextQuestion();
    } catch (e) {
      toast.error("Failed to save timeline");
    } finally {
      setLoading(false);
    }
  };

  const fetchNextQuestion = async () => {
    setFetchingQuestion(true);
    try {
      const q = await getNextQuestion(sessionId);
      
      // Handle stage transition
      if (q.stage === "complete") {
        setQuestionStage("complete");
        setCurrentQuestion(null);
        navigate("/results");
        return;
      }
      
      // Show transition message when switching from core to adaptive
      if (q.stage === "adaptive" && questionStage === "core" && q.transition_message) {
        setTransitionMessage(q.transition_message);
        setShowTransition(true);
        // Auto-dismiss after a moment, but keep showing the question
        setTimeout(() => setShowTransition(false), 6000);
      }
      
      setQuestionStage(q.stage || "core");
      setCurrentQuestion(q);
      setSelectedAnswer("");
      setCustomAnswer("");
    } catch (e) {
      toast.error("Failed to fetch question");
    } finally {
      setFetchingQuestion(false);
    }
  };

  const handleAnswerSubmit = async () => {
    const answer = selectedAnswer || customAnswer;
    if (!answer.trim()) {
      toast.error("Please provide an answer");
      return;
    }
    setLoading(true);
    try {
      const response = await submitAnswer({
        session_id: sessionId,
        question_id: currentQuestion.question_id,
        question_text: currentQuestion.question_text,
        answer: answer,
        category: currentQuestion.category,
      });

      setQuestionsAnswered(response.questions_answered);
      setTrustIndex(response.trust_disruption_index);
      setStabilityHearts(response.stability_hearts);
      setAnalysisData((prev) => ({
        ...prev,
        questionsAnswered: response.questions_answered,
        trustIndex: response.trust_disruption_index,
        stabilityHearts: response.stability_hearts,
      }));

      // Fetch next question — the backend decides when to transition or complete
      fetchNextQuestion();
    } catch (e) {
      toast.error("Failed to submit answer");
    } finally {
      setLoading(false);
    }
  };

  const renderStepIndicator = () => (
    <div className="flex items-center justify-center gap-2 mb-8">
      {STEPS.map((step, i) => (
        <div key={step.id} className="flex items-center">
          <div
            className={`w-10 h-10 rounded-full flex items-center justify-center transition-all ${
              i < localStep
                ? "bg-[#3DD9C5] text-black"
                : i === localStep
                ? "bg-[#3DD9C5]/20 text-[#3DD9C5] border-2 border-[#3DD9C5]"
                : "bg-white/5 text-muted-foreground"
            }`}
          >
            {i < localStep ? <Check className="w-5 h-5" /> : <step.icon className="w-5 h-5" />}
          </div>
          {i < STEPS.length - 1 && (
            <div className={`w-12 h-0.5 mx-1 ${i < localStep ? "bg-[#3DD9C5]" : "bg-white/10"}`} />
          )}
        </div>
      ))}
    </div>
  );

  const renderBaseline = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
    >
      <h2 className="text-2xl md:text-3xl font-light text-[#E6EDF3] mb-8 text-center" style={{ fontFamily: 'Fraunces, serif' }}>
        Relationship Baseline
      </h2>
      <div className="space-y-6">
        <Card className="glass-card rounded-xl">
          <CardContent className="p-6">
            <label className="block text-sm font-medium text-[#E6EDF3] mb-3">
              How long have you been in this relationship?
            </label>
            <Select
              value={baseline.relationship_duration}
              onValueChange={(v) => setBaseline((p) => ({ ...p, relationship_duration: v }))}
            >
              <SelectTrigger data-testid="duration-select">
                <SelectValue placeholder="Select duration" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="less_than_1">Less than 1 year</SelectItem>
                <SelectItem value="1_to_3">1-3 years</SelectItem>
                <SelectItem value="3_to_5">3-5 years</SelectItem>
                <SelectItem value="5_to_10">5-10 years</SelectItem>
                <SelectItem value="more_than_10">More than 10 years</SelectItem>
              </SelectContent>
            </Select>
          </CardContent>
        </Card>

        <Card className="glass-card rounded-xl">
          <CardContent className="p-6">
            <label className="block text-sm font-medium text-[#E6EDF3] mb-3">
              Prior satisfaction level (before recent changes)
            </label>
            <Slider
              value={[baseline.prior_satisfaction]}
              onValueChange={(v) => setBaseline((p) => ({ ...p, prior_satisfaction: v[0] }))}
              min={1}
              max={10}
              step={1}
              data-testid="satisfaction-slider"
            />
            <div className="flex justify-between text-sm text-muted-foreground mt-2">
              <span>Unhappy</span>
              <span className="font-mono text-[#3DD9C5]">{baseline.prior_satisfaction}/10</span>
              <span>Very Happy</span>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-card rounded-xl">
          <CardContent className="p-6">
            <label className="block text-sm font-medium text-[#E6EDF3] mb-3">
              Describe your typical communication habits
            </label>
            <Textarea
              value={baseline.communication_habits}
              onChange={(e) => setBaseline((p) => ({ ...p, communication_habits: e.target.value }))}
              placeholder="How often do you talk? About what? How open are your conversations?"
              className="min-h-[100px] bg-black/20 border-white/10"
              data-testid="communication-textarea"
            />
          </CardContent>
        </Card>

        <Card className="glass-card rounded-xl">
          <CardContent className="p-6">
            <label className="block text-sm font-medium text-[#E6EDF3] mb-3">
              Emotional closeness
            </label>
            <Slider
              value={[baseline.emotional_closeness]}
              onValueChange={(v) => setBaseline((p) => ({ ...p, emotional_closeness: v[0] }))}
              min={1}
              max={10}
              step={1}
            />
            <div className="flex justify-between text-sm text-muted-foreground mt-2">
              <span>Distant</span>
              <span className="font-mono text-[#3DD9C5]">{baseline.emotional_closeness}/10</span>
              <span>Very Close</span>
            </div>
          </CardContent>
        </Card>

        <Card className="glass-card rounded-xl">
          <CardContent className="p-6">
            <label className="block text-sm font-medium text-[#E6EDF3] mb-3">
              Transparency level
            </label>
            <Slider
              value={[baseline.transparency_level]}
              onValueChange={(v) => setBaseline((p) => ({ ...p, transparency_level: v[0] }))}
              min={1}
              max={10}
              step={1}
            />
            <div className="flex justify-between text-sm text-muted-foreground mt-2">
              <span>Private</span>
              <span className="font-mono text-[#3DD9C5]">{baseline.transparency_level}/10</span>
              <span>Fully Open</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="mt-8 flex justify-end">
        <Button
          onClick={handleBaselineSubmit}
          disabled={loading}
          className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-8 py-6 btn-glow"
          data-testid="baseline-continue-btn"
        >
          {loading ? "Saving..." : "Continue"}
          <ArrowRight className="w-5 h-5 ml-2" />
        </Button>
      </div>
    </motion.div>
  );

  const renderChanges = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
    >
      <h2 className="text-2xl md:text-3xl font-light text-[#E6EDF3] mb-4 text-center" style={{ fontFamily: 'Fraunces, serif' }}>
        What Has Changed?
      </h2>
      <p className="text-center text-muted-foreground mb-8">
        Select all areas where you've noticed recent changes
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {changeCategories.map((cat) => {
          const isSelected = selectedChanges.includes(cat.id);
          return (
            <button
              key={cat.id}
              onClick={() =>
                setSelectedChanges((prev) =>
                  isSelected ? prev.filter((c) => c !== cat.id) : [...prev, cat.id]
                )
              }
              className={`p-5 rounded-xl text-left transition-all ${
                isSelected
                  ? "bg-[#3DD9C5]/10 border-2 border-[#3DD9C5]"
                  : "glass-card hover:border-[#3DD9C5]/30"
              }`}
              data-testid={`change-${cat.id}`}
            >
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${isSelected ? "bg-[#3DD9C5]/20" : "bg-white/5"}`}>
                  <cat.icon className={`w-5 h-5 ${isSelected ? "text-[#3DD9C5]" : "text-muted-foreground"}`} />
                </div>
                <div>
                  <h3 className={`font-medium ${isSelected ? "text-[#3DD9C5]" : "text-[#E6EDF3]"}`}>{cat.label}</h3>
                  <p className="text-sm text-muted-foreground">{cat.desc}</p>
                </div>
                {isSelected && <Check className="w-5 h-5 text-[#3DD9C5] ml-auto" />}
              </div>
            </button>
          );
        })}
      </div>

      <p className="text-center text-sm text-muted-foreground mt-6">
        <span className="font-mono text-[#3DD9C5]">{selectedChanges.length}</span> categories selected
      </p>

      <div className="mt-8 flex justify-between">
        <Button variant="ghost" onClick={() => setLocalStep(0)} className="text-white hover:bg-white/5">
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back
        </Button>
        <Button
          onClick={handleChangesSubmit}
          disabled={loading || selectedChanges.length === 0}
          className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-8 py-6 btn-glow"
          data-testid="changes-continue-btn"
        >
          {loading ? "Saving..." : "Continue"}
          <ArrowRight className="w-5 h-5 ml-2" />
        </Button>
      </div>
    </motion.div>
  );

  const renderTimeline = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
    >
      <h2 className="text-2xl md:text-3xl font-light text-[#E6EDF3] mb-8 text-center" style={{ fontFamily: 'Fraunces, serif' }}>
        Timeline Reconstruction
      </h2>

      <div className="space-y-6">
        <Card className="glass-card rounded-xl">
          <CardContent className="p-6">
            <label className="block text-sm font-medium text-[#E6EDF3] mb-4">
              When did you first notice these changes?
            </label>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {[
                { value: "2_weeks", label: "2 weeks" },
                { value: "1_month", label: "1 month" },
                { value: "3_months", label: "3 months" },
                { value: "6_months", label: "6 months" },
                { value: "longer", label: "Longer" },
              ].map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => setTimeline((p) => ({ ...p, when_started: opt.value }))}
                  className={`p-3 rounded-lg text-sm transition-all ${
                    timeline.when_started === opt.value
                      ? "bg-[#3DD9C5] text-black"
                      : "bg-white/5 text-muted-foreground hover:bg-white/10"
                  }`}
                  data-testid={`timeline-${opt.value}`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="glass-card rounded-xl">
          <CardContent className="p-6">
            <label className="block text-sm font-medium text-[#E6EDF3] mb-4">
              Did the changes occur gradually or suddenly?
            </label>
            <div className="grid grid-cols-2 gap-4">
              {[
                { value: "gradual", label: "Gradually", desc: "Changes developed slowly over time" },
                { value: "sudden", label: "Suddenly", desc: "Changes appeared relatively quickly" },
              ].map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => setTimeline((p) => ({ ...p, gradual_or_sudden: opt.value }))}
                  className={`p-4 rounded-lg text-left transition-all ${
                    timeline.gradual_or_sudden === opt.value
                      ? "bg-[#3DD9C5]/10 border-2 border-[#3DD9C5]"
                      : "bg-white/5 border-2 border-transparent hover:border-white/10"
                  }`}
                  data-testid={`timeline-${opt.value}`}
                >
                  <h3 className={timeline.gradual_or_sudden === opt.value ? "text-[#3DD9C5]" : "text-[#E6EDF3]"}>
                    {opt.label}
                  </h3>
                  <p className="text-sm text-muted-foreground">{opt.desc}</p>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card className="glass-card rounded-xl">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium text-[#E6EDF3]">Multiple changes at once?</h3>
                <p className="text-sm text-muted-foreground">Did several changes appear together?</p>
              </div>
              <button
                onClick={() => setTimeline((p) => ({ ...p, multiple_at_once: !p.multiple_at_once }))}
                className={`w-12 h-7 rounded-full transition-all ${
                  timeline.multiple_at_once ? "bg-[#3DD9C5]" : "bg-white/20"
                }`}
                data-testid="multiple-toggle"
              >
                <div
                  className={`w-5 h-5 rounded-full bg-white transition-transform ${
                    timeline.multiple_at_once ? "translate-x-6" : "translate-x-1"
                  }`}
                />
              </button>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="mt-8 flex justify-between">
        <Button variant="ghost" onClick={() => setLocalStep(1)} className="text-white hover:bg-white/5">
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back
        </Button>
        <Button
          onClick={handleTimelineSubmit}
          disabled={loading || !timeline.when_started || !timeline.gradual_or_sudden}
          className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-8 py-6 btn-glow"
          data-testid="timeline-continue-btn"
        >
          {loading ? "Saving..." : "Begin Investigation"}
          <ArrowRight className="w-5 h-5 ml-2" />
        </Button>
      </div>
    </motion.div>
  );

  const renderInvestigation = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
    >
      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <Card className="glass-card rounded-xl">
          <CardContent className="p-4 text-center">
            <p className="text-xs text-muted-foreground mb-1">Questions</p>
            <p className="text-xl font-mono text-[#E6EDF3]">
              {questionsAnswered}
            </p>
          </CardContent>
        </Card>
        <Card className="glass-card rounded-xl">
          <CardContent className="p-4 text-center">
            <p className="text-xs text-muted-foreground mb-1">Stability</p>
            <StabilityHearts count={stabilityHearts} size="sm" />
          </CardContent>
        </Card>
        <Card className="glass-card rounded-xl">
          <CardContent className="p-4 text-center">
            <p className="text-xs text-muted-foreground mb-1">Trust Index</p>
            <p className="text-xl font-mono text-[#3DD9C5]">{trustIndex.toFixed(0)}</p>
          </CardContent>
        </Card>
      </div>

      {/* Stage Label */}
      <div className="flex items-center justify-center gap-2 mb-4">
        <div className={`h-1.5 w-1.5 rounded-full ${questionStage === "core" ? "bg-[#3DD9C5]" : "bg-[#3DD9C5]/30"}`} />
        <span className={`text-xs font-mono tracking-wider ${questionStage === "core" ? "text-[#3DD9C5]" : "text-[#3DD9C5]/40"}`}>
          CORE ANALYSIS
        </span>
        <div className="h-px w-6 bg-white/10" />
        <div className={`h-1.5 w-1.5 rounded-full ${questionStage === "adaptive" ? "bg-amber-400" : "bg-white/10"}`} />
        <span className={`text-xs font-mono tracking-wider ${questionStage === "adaptive" ? "text-amber-400" : "text-white/20"}`}>
          ADAPTIVE INVESTIGATION
        </span>
      </div>

      {/* Transition Banner */}
      <AnimatePresence>
        {showTransition && transitionMessage && (
          <motion.div
            initial={{ opacity: 0, y: -10, height: 0 }}
            animate={{ opacity: 1, y: 0, height: "auto" }}
            exit={{ opacity: 0, y: -10, height: 0 }}
            className="mb-6"
          >
            <div className="rounded-xl border border-amber-400/30 bg-amber-400/5 px-5 py-4 flex items-start gap-3" data-testid="stage-transition-banner">
              <Brain className="w-5 h-5 text-amber-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm text-amber-400 font-medium mb-0.5">Adaptive Investigation</p>
                <p className="text-sm text-[#E6EDF3]/70">{transitionMessage}</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {fetchingQuestion ? (
        <div className="flex flex-col items-center justify-center py-16">
          <HeartLensIcon size={60} animate />
          <p className="mt-4 text-muted-foreground">
            {questionStage === "adaptive" ? "Generating investigation question..." : "Analyzing patterns..."}
          </p>
        </div>
      ) : currentQuestion ? (
        <>
          <Card className="glass-card rounded-xl mb-6">
            <CardContent className="p-8">
              <div className="flex items-start gap-4">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                  currentQuestion.stage === "adaptive" ? "bg-amber-400/10" : "bg-[#3DD9C5]/10"
                }`}>
                  <Brain className={`w-5 h-5 ${currentQuestion.stage === "adaptive" ? "text-amber-400" : "text-[#3DD9C5]"}`} />
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`text-xs font-mono block ${
                      currentQuestion.stage === "adaptive" ? "text-amber-400" : "text-[#3DD9C5]"
                    }`}>
                      {currentQuestion.category?.replace(/_/g, " ").toUpperCase()}
                    </span>
                    {currentQuestion.stage === "adaptive" && (
                      <span className="text-[10px] font-mono bg-amber-400/10 text-amber-400 px-2 py-0.5 rounded-full" data-testid="ai-followup-badge">
                        AI FOLLOW-UP {currentQuestion.followup_number}/{currentQuestion.max_followups}
                      </span>
                    )}
                  </div>
                  <h2 className="text-xl text-[#E6EDF3] leading-relaxed" data-testid="question-text">
                    {currentQuestion.question_text}
                  </h2>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="space-y-3 mb-6">
            {currentQuestion.options && currentQuestion.options.length > 0 ? (
              <>
                {currentQuestion.options.map((opt, i) => (
                  <button
                    key={i}
                    onClick={() => {
                      setSelectedAnswer(opt);
                      setCustomAnswer("");
                    }}
                    className={`w-full p-4 rounded-xl text-left transition-all flex items-center gap-3 ${
                      selectedAnswer === opt
                        ? currentQuestion.stage === "adaptive"
                          ? "bg-amber-400/10 border-2 border-amber-400"
                          : "bg-[#3DD9C5]/10 border-2 border-[#3DD9C5]"
                        : "glass-card hover:border-[#3DD9C5]/30"
                    }`}
                    data-testid={`answer-${i}`}
                  >
                    <div
                      className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                        selectedAnswer === opt
                          ? currentQuestion.stage === "adaptive"
                            ? "border-amber-400 bg-amber-400"
                            : "border-[#3DD9C5] bg-[#3DD9C5]"
                          : "border-white/30"
                      }`}
                    >
                      {selectedAnswer === opt && <Check className="w-3 h-3 text-black" />}
                    </div>
                    <span className={
                      selectedAnswer === opt
                        ? currentQuestion.stage === "adaptive" ? "text-amber-400" : "text-[#3DD9C5]"
                        : "text-[#E6EDF3]"
                    }>
                      {opt}
                    </span>
                  </button>
                ))}
                <div className="mt-4">
                  <p className="text-sm text-muted-foreground mb-2">Or provide your own response:</p>
                  <Textarea
                    value={customAnswer}
                    onChange={(e) => {
                      setCustomAnswer(e.target.value);
                      setSelectedAnswer("");
                    }}
                    placeholder="Type your response..."
                    className="bg-black/20 border-white/10 min-h-[80px]"
                    data-testid="custom-answer"
                  />
                </div>
              </>
            ) : (
              <Textarea
                value={customAnswer}
                onChange={(e) => setCustomAnswer(e.target.value)}
                placeholder="Type your response..."
                className="bg-black/20 border-white/10 min-h-[120px]"
                data-testid="open-answer"
              />
            )}
          </div>

          <div className="flex justify-between items-center">
            {questionsAnswered >= MIN_QUESTIONS && (
              <Button
                variant="outline"
                onClick={() => navigate("/results")}
                className="border-[#3DD9C5]/50 text-[#3DD9C5] hover:bg-[#3DD9C5]/10 rounded-full"
                data-testid="view-results-btn"
              >
                View Results
              </Button>
            )}
            <div className="flex-1" />
            <Button
              onClick={handleAnswerSubmit}
              disabled={loading || (selectedAnswer === "" && customAnswer.trim() === "")}
              className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-8 py-6 btn-glow"
              data-testid="submit-answer-btn"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  Continue
                  <ArrowRight className="w-5 h-5 ml-2" />
                </>
              )}
            </Button>
          </div>

          <div className="mt-8">
            <Progress
              value={
                questionStage === "core" && currentQuestion.total_core
                  ? (questionsAnswered / currentQuestion.total_core) * 100
                  : questionStage === "adaptive" && currentQuestion.max_followups
                  ? 100 // core done
                  : (questionsAnswered / MIN_QUESTIONS) * 100
              }
              className="h-1"
            />
            <p className="text-xs text-muted-foreground mt-2 text-center">
              {questionStage === "core"
                ? `Core analysis: question ${questionsAnswered + 1} of ${currentQuestion.total_core || MIN_QUESTIONS}`
                : questionStage === "adaptive"
                ? `Adaptive follow-up ${currentQuestion.followup_number || 1} of ${currentQuestion.max_followups || MAX_FOLLOWUP_QUESTIONS}`
                : "Analysis in progress..."}
            </p>
          </div>
        </>
      ) : (
        <div className="text-center py-16">
          <p className="text-muted-foreground">Loading questions...</p>
        </div>
      )}
    </motion.div>
  );

  return (
    <div className="min-h-screen bg-[#0B132B]">
      <header className="glass border-b border-white/10">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => (localStep > 0 ? setLocalStep(localStep - 1) : navigate("/clarity"))}
              className="text-white hover:bg-white/10"
              data-testid="back-btn"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <TrustLensLogo size="md" />
          </div>
          <span className="text-sm text-muted-foreground font-mono">
            {STEPS[localStep]?.label}
          </span>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8 max-w-3xl">
        {renderStepIndicator()}
        <AnimatePresence mode="wait">
          {localStep === 0 && renderBaseline()}
          {localStep === 1 && renderChanges()}
          {localStep === 2 && renderTimeline()}
          {localStep === 3 && renderInvestigation()}
        </AnimatePresence>
      </main>
    </div>
  );
};

export default DeepAnalysis;

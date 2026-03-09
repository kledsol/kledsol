import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Textarea } from "@/components/ui/textarea";
import { useTheme, useAnalysis } from "@/App";
import { getNextQuestion, submitAnswer } from "@/lib/api";
import { toast } from "sonner";
import {
  ArrowLeft,
  ArrowRight,
  Moon,
  Sun,
  Brain,
  Loader2,
  Check,
  BarChart3,
} from "lucide-react";

const AdaptiveInvestigation = () => {
  const { theme, toggleTheme } = useTheme();
  const { sessionId, setCurrentStep, setAnalysisData, analysisData } =
    useAnalysis();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [fetchingQuestion, setFetchingQuestion] = useState(true);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [selectedAnswer, setSelectedAnswer] = useState("");
  const [customAnswer, setCustomAnswer] = useState("");
  const [questionsAnswered, setQuestionsAnswered] = useState(0);
  const [trustIndex, setTrustIndex] = useState(0);
  const [confidence, setConfidence] = useState("low");

  const MIN_QUESTIONS = 5;
  const MAX_QUESTIONS = 15;

  useEffect(() => {
    if (!sessionId) {
      toast.error("Session not found. Please start over.");
      navigate("/");
      return;
    }
    fetchNextQuestion();
  }, [sessionId]);

  const fetchNextQuestion = async () => {
    setFetchingQuestion(true);
    try {
      const question = await getNextQuestion(sessionId);
      setCurrentQuestion(question);
      setSelectedAnswer("");
      setCustomAnswer("");
    } catch (error) {
      console.error("Failed to fetch question:", error);
      toast.error("Failed to load question. Please try again.");
    } finally {
      setFetchingQuestion(false);
    }
  };

  const handleSubmitAnswer = async () => {
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
      setConfidence(response.confidence_level);

      setAnalysisData((prev) => ({
        ...prev,
        questionsAnswered: response.questions_answered,
        trustIndex: response.trust_disruption_index,
      }));

      // Check if we should continue or show results
      if (
        response.questions_answered >= MIN_QUESTIONS &&
        (response.confidence_level === "high" ||
          response.questions_answered >= MAX_QUESTIONS)
      ) {
        setCurrentStep("results");
        toast.success("Analysis complete");
        navigate("/results");
      } else {
        await fetchNextQuestion();
      }
    } catch (error) {
      console.error("Failed to submit answer:", error);
      toast.error("Failed to submit answer. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleViewResults = () => {
    if (questionsAnswered >= MIN_QUESTIONS) {
      setCurrentStep("results");
      navigate("/results");
    } else {
      toast.error(
        `Please answer at least ${MIN_QUESTIONS} questions to see results`
      );
    }
  };

  const getCategoryLabel = (category) => {
    const labels = {
      routine_changes: "Daily Routine",
      communication_changes: "Communication",
      emotional_indicators: "Emotional",
      digital_behavior: "Digital Behavior",
      social_behavior: "Social Life",
      financial_signals: "Financial",
    };
    return labels[category] || category;
  };

  const getCategoryColor = (category) => {
    const colors = {
      routine_changes: "bg-blue-500/20 text-blue-400",
      communication_changes: "bg-green-500/20 text-green-400",
      emotional_indicators: "bg-red-500/20 text-red-400",
      digital_behavior: "bg-purple-500/20 text-purple-400",
      social_behavior: "bg-yellow-500/20 text-yellow-400",
      financial_signals: "bg-orange-500/20 text-orange-400",
    };
    return colors[category] || "bg-accent/20 text-accent";
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 glass border-b border-border/50">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate("/timeline")}
              data-testid="back-btn"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-lg font-semibold text-foreground">
                Adaptive Investigation
              </h1>
              <p className="text-sm text-muted-foreground">Step 4 of 4</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
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
          </div>
        </div>
      </header>

      {/* Progress Bar */}
      <div className="h-1 bg-muted">
        <motion.div
          initial={{ width: "75%" }}
          animate={{ width: "100%" }}
          className="h-full bg-accent"
        />
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8 max-w-3xl">
        {/* Stats Bar */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 grid grid-cols-3 gap-4"
        >
          <Card className="bg-card/60 backdrop-blur border-border/50">
            <CardContent className="p-4 text-center">
              <p className="text-sm text-muted-foreground mb-1">Questions</p>
              <p className="text-2xl font-bold font-mono text-foreground">
                {questionsAnswered}
                <span className="text-sm text-muted-foreground">
                  /{MIN_QUESTIONS}
                </span>
              </p>
            </CardContent>
          </Card>
          <Card className="bg-card/60 backdrop-blur border-border/50">
            <CardContent className="p-4 text-center">
              <p className="text-sm text-muted-foreground mb-1">Trust Index</p>
              <p className="text-2xl font-bold font-mono text-accent">
                {trustIndex.toFixed(0)}
              </p>
            </CardContent>
          </Card>
          <Card className="bg-card/60 backdrop-blur border-border/50">
            <CardContent className="p-4 text-center">
              <p className="text-sm text-muted-foreground mb-1">Confidence</p>
              <p
                className={`text-lg font-semibold capitalize ${
                  confidence === "high"
                    ? "text-green-400"
                    : confidence === "moderate"
                    ? "text-yellow-400"
                    : "text-muted-foreground"
                }`}
              >
                {confidence}
              </p>
            </CardContent>
          </Card>
        </motion.div>

        {/* Question Area */}
        <AnimatePresence mode="wait">
          {fetchingQuestion ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center py-16"
            >
              <div className="w-16 h-16 rounded-full bg-accent/20 flex items-center justify-center mb-4 pulse-glow">
                <Brain className="w-8 h-8 text-accent animate-pulse" />
              </div>
              <p className="text-muted-foreground">Analyzing patterns...</p>
            </motion.div>
          ) : currentQuestion ? (
            <motion.div
              key={currentQuestion.question_id}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              {/* Category Badge */}
              <div className="flex items-center gap-2 mb-4">
                <span
                  className={`px-3 py-1 rounded-full text-xs font-medium ${getCategoryColor(
                    currentQuestion.category
                  )}`}
                >
                  {getCategoryLabel(currentQuestion.category)}
                </span>
                <span className="text-xs text-muted-foreground">
                  Question {questionsAnswered + 1}
                </span>
              </div>

              {/* Question Card */}
              <Card className="bg-card/60 backdrop-blur border-border/50 mb-6">
                <CardContent className="p-8">
                  <div className="flex items-start gap-4">
                    <div className="w-10 h-10 rounded-lg bg-accent/20 flex items-center justify-center flex-shrink-0">
                      <Brain className="w-5 h-5 text-accent" />
                    </div>
                    <div>
                      <h2
                        className="text-xl font-semibold text-foreground leading-relaxed"
                        data-testid="question-text"
                      >
                        {currentQuestion.question_text}
                      </h2>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Answer Options */}
              <div className="space-y-3 mb-6">
                {currentQuestion.options &&
                currentQuestion.options.length > 0 ? (
                  <>
                    {currentQuestion.options.map((option, index) => (
                      <motion.button
                        key={index}
                        whileHover={{ scale: 1.01 }}
                        whileTap={{ scale: 0.99 }}
                        onClick={() => setSelectedAnswer(option)}
                        className={`w-full p-4 rounded-xl border text-left transition-all flex items-center gap-3 ${
                          selectedAnswer === option
                            ? "bg-accent/10 border-accent"
                            : "bg-card/40 border-border/50 hover:border-accent/30"
                        }`}
                        data-testid={`answer-option-${index}`}
                      >
                        <div
                          className={`w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-colors ${
                            selectedAnswer === option
                              ? "border-accent bg-accent"
                              : "border-border"
                          }`}
                        >
                          {selectedAnswer === option && (
                            <Check className="w-4 h-4 text-accent-foreground" />
                          )}
                        </div>
                        <span
                          className={
                            selectedAnswer === option
                              ? "text-accent font-medium"
                              : "text-foreground"
                          }
                        >
                          {option}
                        </span>
                      </motion.button>
                    ))}

                    {/* Custom answer option */}
                    <div className="mt-4">
                      <p className="text-sm text-muted-foreground mb-2">
                        Or provide your own response:
                      </p>
                      <Textarea
                        value={customAnswer}
                        onChange={(e) => {
                          setCustomAnswer(e.target.value);
                          setSelectedAnswer("");
                        }}
                        placeholder="Type your response here..."
                        className="min-h-[80px]"
                        data-testid="custom-answer"
                      />
                    </div>
                  </>
                ) : (
                  <Textarea
                    value={customAnswer}
                    onChange={(e) => setCustomAnswer(e.target.value)}
                    placeholder="Type your response here..."
                    className="min-h-[120px]"
                    data-testid="open-answer"
                  />
                )}
              </div>

              {/* Actions */}
              <div className="flex justify-between items-center">
                {questionsAnswered >= MIN_QUESTIONS && (
                  <Button
                    variant="outline"
                    onClick={handleViewResults}
                    className="border-accent/50 text-accent hover:bg-accent/10"
                    data-testid="view-results-btn"
                  >
                    <BarChart3 className="w-4 h-4 mr-2" />
                    View Results
                  </Button>
                )}
                <div className="flex-1" />
                <Button
                  onClick={handleSubmitAnswer}
                  disabled={
                    loading || (selectedAnswer === "" && customAnswer.trim() === "")
                  }
                  className="bg-accent hover:bg-accent/90 text-accent-foreground"
                  data-testid="submit-answer-btn"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      Continue
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </>
                  )}
                </Button>
              </div>
            </motion.div>
          ) : (
            <div className="text-center py-16">
              <p className="text-muted-foreground">
                No more questions available.
              </p>
              <Button
                onClick={handleViewResults}
                className="mt-4 bg-accent hover:bg-accent/90 text-accent-foreground"
              >
                View Results
              </Button>
            </div>
          )}
        </AnimatePresence>

        {/* Progress indicator */}
        <div className="mt-8">
          <div className="flex justify-between text-sm text-muted-foreground mb-2">
            <span>Analysis progress</span>
            <span>
              {Math.min(
                100,
                Math.round((questionsAnswered / MIN_QUESTIONS) * 100)
              )}
              %
            </span>
          </div>
          <Progress
            value={Math.min(
              100,
              (questionsAnswered / MIN_QUESTIONS) * 100
            )}
            className="h-2"
          />
          <p className="text-xs text-muted-foreground mt-2">
            {questionsAnswered < MIN_QUESTIONS
              ? `Answer ${MIN_QUESTIONS - questionsAnswered} more questions for initial analysis`
              : "You can view results now or continue for more accurate analysis"}
          </p>
        </div>
      </main>
    </div>
  );
};

export default AdaptiveInvestigation;

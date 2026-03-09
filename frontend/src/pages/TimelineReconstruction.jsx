import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { useTheme, useAnalysis } from "@/App";
import { submitTimeline } from "@/lib/api";
import { toast } from "sonner";
import {
  ArrowLeft,
  ArrowRight,
  Moon,
  Sun,
  Calendar,
  TrendingUp,
  Layers,
} from "lucide-react";

const TimelineReconstruction = () => {
  const { theme, toggleTheme } = useTheme();
  const { sessionId, setCurrentStep, setAnalysisData } = useAnalysis();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    when_started: "",
    gradual_or_sudden: "",
    multiple_at_once: false,
  });

  const timeframeOptions = [
    { value: "2_weeks", label: "About 2 weeks ago" },
    { value: "1_month", label: "About 1 month ago" },
    { value: "3_months", label: "About 3 months ago" },
    { value: "6_months", label: "About 6 months ago" },
    { value: "longer", label: "Longer than 6 months" },
  ];

  const handleSubmit = async () => {
    if (!formData.when_started || !formData.gradual_or_sudden) {
      toast.error("Please complete all fields");
      return;
    }

    if (!sessionId) {
      toast.error("Session not found. Please start over.");
      navigate("/");
      return;
    }

    setLoading(true);
    try {
      await submitTimeline({
        session_id: sessionId,
        ...formData,
      });
      setAnalysisData((prev) => ({ ...prev, timeline: formData }));
      setCurrentStep("investigation");
      toast.success("Timeline recorded");
      navigate("/investigation");
    } catch (error) {
      console.error("Failed to submit timeline:", error);
      toast.error("Failed to save timeline. Please try again.");
    } finally {
      setLoading(false);
    }
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
              onClick={() => navigate("/changes")}
              data-testid="back-btn"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-lg font-semibold text-foreground">
                Timeline Reconstruction
              </h1>
              <p className="text-sm text-muted-foreground">Step 3 of 4</p>
            </div>
          </div>
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
      </header>

      {/* Progress Bar */}
      <div className="h-1 bg-muted">
        <motion.div
          initial={{ width: "50%" }}
          animate={{ width: "75%" }}
          className="h-full bg-accent"
        />
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-12 max-w-3xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="mb-8 text-center">
            <h2 className="text-2xl sm:text-3xl font-bold text-foreground mb-3">
              When Did Changes Begin?
            </h2>
            <p className="text-muted-foreground">
              Help us understand the timeline of behavioral changes.
            </p>
          </div>

          <div className="space-y-6">
            {/* Timeline Selection */}
            <Card className="bg-card/60 backdrop-blur border-border/50">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base">
                  <Calendar className="w-5 h-5 text-accent" />
                  When did you first notice changes?
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {timeframeOptions.map((option) => (
                    <motion.button
                      key={option.value}
                      whileHover={{ scale: 1.01 }}
                      whileTap={{ scale: 0.99 }}
                      onClick={() =>
                        setFormData((prev) => ({
                          ...prev,
                          when_started: option.value,
                        }))
                      }
                      className={`w-full p-4 rounded-lg border text-left transition-all ${
                        formData.when_started === option.value
                          ? "bg-accent/10 border-accent"
                          : "bg-background/50 border-border hover:border-accent/30"
                      }`}
                      data-testid={`timeline-${option.value}`}
                    >
                      <span
                        className={
                          formData.when_started === option.value
                            ? "text-accent font-medium"
                            : "text-foreground"
                        }
                      >
                        {option.label}
                      </span>
                    </motion.button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Gradual vs Sudden */}
            <Card className="bg-card/60 backdrop-blur border-border/50">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base">
                  <TrendingUp className="w-5 h-5 text-accent" />
                  How did the changes occur?
                </CardTitle>
              </CardHeader>
              <CardContent>
                <RadioGroup
                  value={formData.gradual_or_sudden}
                  onValueChange={(value) =>
                    setFormData((prev) => ({
                      ...prev,
                      gradual_or_sudden: value,
                    }))
                  }
                  className="space-y-4"
                >
                  <div
                    className={`flex items-center space-x-4 p-4 rounded-lg border transition-all ${
                      formData.gradual_or_sudden === "gradual"
                        ? "bg-accent/10 border-accent"
                        : "bg-background/50 border-border"
                    }`}
                  >
                    <RadioGroupItem
                      value="gradual"
                      id="gradual"
                      data-testid="gradual-radio"
                    />
                    <Label
                      htmlFor="gradual"
                      className="flex-1 cursor-pointer"
                    >
                      <span className="font-medium text-foreground">
                        Gradual changes
                      </span>
                      <p className="text-sm text-muted-foreground">
                        Changes developed slowly over time
                      </p>
                    </Label>
                  </div>
                  <div
                    className={`flex items-center space-x-4 p-4 rounded-lg border transition-all ${
                      formData.gradual_or_sudden === "sudden"
                        ? "bg-accent/10 border-accent"
                        : "bg-background/50 border-border"
                    }`}
                  >
                    <RadioGroupItem
                      value="sudden"
                      id="sudden"
                      data-testid="sudden-radio"
                    />
                    <Label
                      htmlFor="sudden"
                      className="flex-1 cursor-pointer"
                    >
                      <span className="font-medium text-foreground">
                        Sudden changes
                      </span>
                      <p className="text-sm text-muted-foreground">
                        Changes appeared relatively quickly
                      </p>
                    </Label>
                  </div>
                </RadioGroup>
              </CardContent>
            </Card>

            {/* Multiple at Once */}
            <Card className="bg-card/60 backdrop-blur border-border/50">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base">
                  <Layers className="w-5 h-5 text-accent" />
                  Did multiple changes happen simultaneously?
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-foreground">
                      Multiple changes at the same time
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Several behavioral changes appeared together
                    </p>
                  </div>
                  <Switch
                    checked={formData.multiple_at_once}
                    onCheckedChange={(checked) =>
                      setFormData((prev) => ({
                        ...prev,
                        multiple_at_once: checked,
                      }))
                    }
                    data-testid="multiple-switch"
                  />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Visual Timeline Preview */}
          {formData.when_started && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8 p-6 rounded-xl bg-card/40 border border-border/50"
            >
              <h3 className="text-sm font-medium text-muted-foreground mb-4">
                Timeline Preview
              </h3>
              <div className="relative">
                <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-border" />
                <div className="space-y-4">
                  <div className="relative flex items-center gap-4">
                    <div className="w-8 h-8 rounded-full bg-accent flex items-center justify-center z-10">
                      <div className="w-3 h-3 rounded-full bg-accent-foreground" />
                    </div>
                    <div>
                      <p className="font-medium text-foreground">
                        Changes began
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {
                          timeframeOptions.find(
                            (o) => o.value === formData.when_started
                          )?.label
                        }
                      </p>
                    </div>
                  </div>
                  {formData.gradual_or_sudden && (
                    <div className="relative flex items-center gap-4">
                      <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center z-10">
                        <div className="w-2 h-2 rounded-full bg-muted-foreground" />
                      </div>
                      <div>
                        <p className="font-medium text-foreground">
                          Pattern type
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {formData.gradual_or_sudden === "gradual"
                            ? "Gradual development"
                            : "Sudden onset"}
                        </p>
                      </div>
                    </div>
                  )}
                  <div className="relative flex items-center gap-4">
                    <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center z-10">
                      <div className="w-2 h-2 rounded-full bg-muted-foreground" />
                    </div>
                    <div>
                      <p className="font-medium text-foreground">Present</p>
                      <p className="text-sm text-muted-foreground">
                        Analysis in progress
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Actions */}
          <div className="mt-8 flex justify-between">
            <Button
              variant="ghost"
              onClick={() => navigate("/changes")}
              data-testid="back-to-changes"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={
                loading ||
                !formData.when_started ||
                !formData.gradual_or_sudden
              }
              className="bg-accent hover:bg-accent/90 text-accent-foreground"
              data-testid="continue-btn"
            >
              {loading ? (
                "Saving..."
              ) : (
                <>
                  Begin Investigation
                  <ArrowRight className="w-4 h-4 ml-2" />
                </>
              )}
            </Button>
          </div>
        </motion.div>
      </main>
    </div>
  );
};

export default TimelineReconstruction;

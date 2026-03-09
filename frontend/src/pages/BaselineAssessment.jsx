import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useTheme, useAnalysis } from "@/App";
import { submitBaseline } from "@/lib/api";
import { toast } from "sonner";
import {
  ArrowLeft,
  ArrowRight,
  Heart,
  Clock,
  MessageSquare,
  Moon,
  Sun,
} from "lucide-react";

const BaselineAssessment = () => {
  const { theme, toggleTheme } = useTheme();
  const { sessionId, setCurrentStep, setAnalysisData } = useAnalysis();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    relationship_duration: "",
    perceived_quality: 7,
    communication_frequency: "",
    emotional_connection: 7,
    transparency_level: 7,
    shared_routines: "",
  });

  const handleSubmit = async () => {
    if (
      !formData.relationship_duration ||
      !formData.communication_frequency ||
      !formData.shared_routines
    ) {
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
      await submitBaseline({
        session_id: sessionId,
        ...formData,
      });
      setAnalysisData((prev) => ({ ...prev, baseline: formData }));
      setCurrentStep("changes");
      toast.success("Baseline recorded");
      navigate("/changes");
    } catch (error) {
      console.error("Failed to submit baseline:", error);
      toast.error("Failed to save baseline. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const durationOptions = [
    { value: "less_than_1_year", label: "Less than 1 year" },
    { value: "1_to_3_years", label: "1-3 years" },
    { value: "3_to_5_years", label: "3-5 years" },
    { value: "5_to_10_years", label: "5-10 years" },
    { value: "more_than_10_years", label: "More than 10 years" },
  ];

  const communicationOptions = [
    { value: "multiple_daily", label: "Multiple times daily" },
    { value: "once_daily", label: "Once daily" },
    { value: "few_times_week", label: "A few times per week" },
    { value: "weekly", label: "Weekly" },
    { value: "less_than_weekly", label: "Less than weekly" },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 glass border-b border-border/50">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate("/")}
              data-testid="back-btn"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-lg font-semibold text-foreground">
                Relationship Baseline
              </h1>
              <p className="text-sm text-muted-foreground">Step 1 of 4</p>
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
          initial={{ width: 0 }}
          animate={{ width: "25%" }}
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
              Establish Normal Patterns
            </h2>
            <p className="text-muted-foreground">
              Help us understand what your relationship looked like before
              recent changes.
            </p>
          </div>

          <div className="space-y-6">
            {/* Duration */}
            <Card className="bg-card/60 backdrop-blur border-border/50">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base">
                  <Clock className="w-5 h-5 text-accent" />
                  Relationship Duration
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Select
                  value={formData.relationship_duration}
                  onValueChange={(value) =>
                    setFormData((prev) => ({
                      ...prev,
                      relationship_duration: value,
                    }))
                  }
                >
                  <SelectTrigger data-testid="duration-select">
                    <SelectValue placeholder="Select duration" />
                  </SelectTrigger>
                  <SelectContent>
                    {durationOptions.map((opt) => (
                      <SelectItem key={opt.value} value={opt.value}>
                        {opt.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>

            {/* Perceived Quality */}
            <Card className="bg-card/60 backdrop-blur border-border/50">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base">
                  <Heart className="w-5 h-5 text-accent" />
                  Perceived Relationship Quality
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <Slider
                    value={[formData.perceived_quality]}
                    onValueChange={(value) =>
                      setFormData((prev) => ({
                        ...prev,
                        perceived_quality: value[0],
                      }))
                    }
                    min={1}
                    max={10}
                    step={1}
                    data-testid="quality-slider"
                  />
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>Poor</span>
                    <span className="font-mono text-accent">
                      {formData.perceived_quality}/10
                    </span>
                    <span>Excellent</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Communication Frequency */}
            <Card className="bg-card/60 backdrop-blur border-border/50">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base">
                  <MessageSquare className="w-5 h-5 text-accent" />
                  Communication Frequency
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Select
                  value={formData.communication_frequency}
                  onValueChange={(value) =>
                    setFormData((prev) => ({
                      ...prev,
                      communication_frequency: value,
                    }))
                  }
                >
                  <SelectTrigger data-testid="communication-select">
                    <SelectValue placeholder="How often do you communicate?" />
                  </SelectTrigger>
                  <SelectContent>
                    {communicationOptions.map((opt) => (
                      <SelectItem key={opt.value} value={opt.value}>
                        {opt.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>

            {/* Emotional Connection */}
            <Card className="bg-card/60 backdrop-blur border-border/50">
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Emotional Connection</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <Slider
                    value={[formData.emotional_connection]}
                    onValueChange={(value) =>
                      setFormData((prev) => ({
                        ...prev,
                        emotional_connection: value[0],
                      }))
                    }
                    min={1}
                    max={10}
                    step={1}
                    data-testid="emotional-slider"
                  />
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>Distant</span>
                    <span className="font-mono text-accent">
                      {formData.emotional_connection}/10
                    </span>
                    <span>Very Close</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Transparency Level */}
            <Card className="bg-card/60 backdrop-blur border-border/50">
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Transparency Level</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <Slider
                    value={[formData.transparency_level]}
                    onValueChange={(value) =>
                      setFormData((prev) => ({
                        ...prev,
                        transparency_level: value[0],
                      }))
                    }
                    min={1}
                    max={10}
                    step={1}
                    data-testid="transparency-slider"
                  />
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>Very Private</span>
                    <span className="font-mono text-accent">
                      {formData.transparency_level}/10
                    </span>
                    <span>Fully Open</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Shared Routines */}
            <Card className="bg-card/60 backdrop-blur border-border/50">
              <CardHeader className="pb-3">
                <CardTitle className="text-base">
                  Describe Your Shared Routines
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Textarea
                  value={formData.shared_routines}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      shared_routines: e.target.value,
                    }))
                  }
                  placeholder="Describe typical activities you do together (meals, evenings, weekends, etc.)"
                  className="min-h-[100px]"
                  data-testid="routines-textarea"
                />
              </CardContent>
            </Card>
          </div>

          {/* Actions */}
          <div className="mt-8 flex justify-end">
            <Button
              onClick={handleSubmit}
              disabled={loading}
              className="bg-accent hover:bg-accent/90 text-accent-foreground"
              data-testid="continue-btn"
            >
              {loading ? (
                "Saving..."
              ) : (
                <>
                  Continue
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

export default BaselineAssessment;

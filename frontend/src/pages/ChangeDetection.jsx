import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { useTheme, useAnalysis } from "@/App";
import { submitChanges } from "@/lib/api";
import { toast } from "sonner";
import {
  ArrowLeft,
  ArrowRight,
  Moon,
  Sun,
  Clock,
  MessageSquare,
  Heart,
  Smartphone,
  Users,
  HeartPulse,
  CreditCard,
  MoreHorizontal,
  Check,
} from "lucide-react";

const ChangeDetection = () => {
  const { theme, toggleTheme } = useTheme();
  const { sessionId, setCurrentStep, setAnalysisData } = useAnalysis();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [selectedCategories, setSelectedCategories] = useState([]);

  const categories = [
    {
      id: "daily_routine",
      icon: Clock,
      title: "Daily Routine",
      description: "Schedule modifications, late returns, new activities",
    },
    {
      id: "communication_patterns",
      icon: MessageSquare,
      title: "Communication Patterns",
      description: "Shorter conversations, delayed responses",
    },
    {
      id: "emotional_connection",
      icon: Heart,
      title: "Emotional Connection",
      description: "Detachment, irritability, reduced affection",
    },
    {
      id: "digital_behavior",
      icon: Smartphone,
      title: "Phone & Digital Behavior",
      description: "Phone secrecy, hidden notifications",
    },
    {
      id: "social_life",
      icon: Users,
      title: "Social Life",
      description: "New social circles, frequent outings",
    },
    {
      id: "intimacy",
      icon: HeartPulse,
      title: "Intimacy",
      description: "Changes in physical or emotional intimacy",
    },
    {
      id: "financial_habits",
      icon: CreditCard,
      title: "Financial Habits",
      description: "Unusual expenses, secretive spending",
    },
    {
      id: "other_changes",
      icon: MoreHorizontal,
      title: "Other Changes",
      description: "Other behavioral changes not listed",
    },
  ];

  const toggleCategory = (id) => {
    setSelectedCategories((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
    );
  };

  const handleSubmit = async () => {
    if (selectedCategories.length === 0) {
      toast.error("Please select at least one category");
      return;
    }

    if (!sessionId) {
      toast.error("Session not found. Please start over.");
      navigate("/");
      return;
    }

    setLoading(true);
    try {
      await submitChanges({
        session_id: sessionId,
        categories: selectedCategories,
      });
      setAnalysisData((prev) => ({ ...prev, changes: selectedCategories }));
      setCurrentStep("timeline");
      toast.success("Changes recorded");
      navigate("/timeline");
    } catch (error) {
      console.error("Failed to submit changes:", error);
      toast.error("Failed to save changes. Please try again.");
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
              onClick={() => navigate("/baseline")}
              data-testid="back-btn"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-lg font-semibold text-foreground">
                Change Detection
              </h1>
              <p className="text-sm text-muted-foreground">Step 2 of 4</p>
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
          initial={{ width: "25%" }}
          animate={{ width: "50%" }}
          className="h-full bg-accent"
        />
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-12 max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="mb-8 text-center">
            <h2 className="text-2xl sm:text-3xl font-bold text-foreground mb-3">
              What Has Changed?
            </h2>
            <p className="text-muted-foreground">
              Select the categories where you've noticed recent changes in your
              partner's behavior.
            </p>
          </div>

          {/* Category Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {categories.map((category, index) => {
              const isSelected = selectedCategories.includes(category.id);
              return (
                <motion.button
                  key={category.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                  onClick={() => toggleCategory(category.id)}
                  className={`relative p-6 rounded-xl border text-left transition-all group ${
                    isSelected
                      ? "bg-accent/10 border-accent"
                      : "bg-card/60 border-border/50 hover:border-accent/30"
                  }`}
                  data-testid={`category-${category.id}`}
                >
                  {/* Selection indicator */}
                  {isSelected && (
                    <div className="absolute top-3 right-3 w-6 h-6 rounded-full bg-accent flex items-center justify-center">
                      <Check className="w-4 h-4 text-accent-foreground" />
                    </div>
                  )}

                  <div
                    className={`w-10 h-10 rounded-lg flex items-center justify-center mb-4 transition-colors ${
                      isSelected
                        ? "bg-accent/20"
                        : "bg-muted group-hover:bg-accent/10"
                    }`}
                  >
                    <category.icon
                      className={`w-5 h-5 ${
                        isSelected ? "text-accent" : "text-muted-foreground"
                      }`}
                    />
                  </div>
                  <h3
                    className={`font-semibold mb-1 ${
                      isSelected ? "text-accent" : "text-foreground"
                    }`}
                  >
                    {category.title}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {category.description}
                  </p>
                </motion.button>
              );
            })}
          </div>

          {/* Selected Count */}
          <div className="text-center mb-8">
            <p className="text-sm text-muted-foreground">
              <span className="font-mono text-accent">
                {selectedCategories.length}
              </span>{" "}
              categories selected
            </p>
          </div>

          {/* Actions */}
          <div className="flex justify-between">
            <Button
              variant="ghost"
              onClick={() => navigate("/baseline")}
              data-testid="back-to-baseline"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={loading || selectedCategories.length === 0}
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

export default ChangeDetection;

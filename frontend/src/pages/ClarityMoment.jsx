import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { TrustLensLogo, HeartLensIcon } from "@/components/custom/Logo";
import { useAnalysis } from "@/App";
import { Heart, Activity, ArrowLeft, Check } from "lucide-react";

const ClarityMoment = () => {
  const { analysisType, setAnalysisData } = useAnalysis();
  const navigate = useNavigate();
  const [step, setStep] = useState("engagement"); // engagement | clarity
  const [selectedReason, setSelectedReason] = useState(null);

  const engagementOptions = [
    { id: "changed", label: "Something changed recently" },
    { id: "behavior", label: "I noticed unusual behavior" },
    { id: "feeling", label: "I just have a feeling something is wrong" },
  ];

  const handleReasonSelect = (reason) => {
    setSelectedReason(reason);
    // Store the reason in analysis data
    setAnalysisData((prev) => ({ ...prev, engagementReason: reason }));
    // Move to clarity step after a brief moment
    setTimeout(() => setStep("clarity"), 300);
  };

  const handleProceed = (type) => {
    if (type === "pulse") {
      navigate("/pulse");
    } else {
      navigate("/analysis");
    }
  };

  return (
    <div className="min-h-screen bg-[#0B132B] relative overflow-hidden flex items-center justify-center">
      {/* Return to Home Button */}
      <motion.div
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
        className="absolute top-6 left-6 z-20"
      >
        <Button
          variant="ghost"
          onClick={() => navigate("/")}
          className="text-muted-foreground hover:text-white hover:bg-white/10 rounded-full px-4 py-2"
          data-testid="return-home-btn"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Return to Home
        </Button>
      </motion.div>

      {/* Background */}
      <div
        className="absolute inset-0 bg-cover bg-center opacity-20"
        style={{
          backgroundImage:
            "url(https://images.unsplash.com/photo-1765710029742-d92e3156a8f5?crop=entropy&cs=srgb&fm=jpg&q=85)",
        }}
      />
      <div className="absolute inset-0 bg-gradient-to-b from-[#0B132B]/80 via-[#0B132B]/90 to-[#0B132B]" />

      {/* Content */}
      <div className="relative z-10 container mx-auto px-6 text-center max-w-2xl">
        <AnimatePresence mode="wait">
          {step === "engagement" ? (
            <motion.div
              key="engagement"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
            >
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
                className="mb-8"
              >
                <HeartLensIcon size={80} animate />
              </motion.div>

              <motion.h1
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7, delay: 0.2 }}
                className="text-3xl md:text-4xl font-light text-[#E6EDF3] mb-10 leading-tight"
                style={{ fontFamily: 'Fraunces, serif' }}
              >
                What made you start wondering about this?
              </motion.h1>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7, delay: 0.3 }}
                className="space-y-4"
              >
                {engagementOptions.map((option, index) => (
                  <motion.button
                    key={option.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.5, delay: 0.4 + index * 0.1 }}
                    onClick={() => handleReasonSelect(option.id)}
                    className={`w-full p-5 rounded-xl text-left transition-all flex items-center gap-4 ${
                      selectedReason === option.id
                        ? "bg-[#3DD9C5]/10 border-2 border-[#3DD9C5]"
                        : "glass-card hover:border-[#3DD9C5]/30"
                    }`}
                    data-testid={`reason-${option.id}`}
                  >
                    <div
                      className={`w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all ${
                        selectedReason === option.id
                          ? "border-[#3DD9C5] bg-[#3DD9C5]"
                          : "border-white/30"
                      }`}
                    >
                      {selectedReason === option.id && (
                        <Check className="w-4 h-4 text-black" />
                      )}
                    </div>
                    <span
                      className={`text-lg ${
                        selectedReason === option.id
                          ? "text-[#3DD9C5]"
                          : "text-[#E6EDF3]"
                      }`}
                    >
                      {option.label}
                    </span>
                  </motion.button>
                ))}
              </motion.div>

              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.7, delay: 0.7 }}
                className="mt-10 text-sm text-muted-foreground/60"
              >
                Your response helps us personalize your analysis.
              </motion.p>
            </motion.div>
          ) : (
            <motion.div
              key="clarity"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
            >
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
                className="mb-8"
              >
                <HeartLensIcon size={80} animate />
              </motion.div>

              <motion.h1
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7, delay: 0.2 }}
                className="text-4xl md:text-5xl font-light text-[#E6EDF3] mb-6 leading-tight"
                style={{ fontFamily: 'Fraunces, serif' }}
              >
                A Moment of Clarity
              </motion.h1>

              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7, delay: 0.3 }}
                className="text-lg text-muted-foreground mb-12 leading-relaxed"
              >
                Sometimes uncertainty is harder than the truth. TrustLens can help you
                understand relationship signals through calm, empathetic analysis.
                Take a breath, and choose how you'd like to proceed.
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7, delay: 0.4 }}
                className="flex flex-col sm:flex-row gap-4 justify-center"
              >
                <Button
                  onClick={() => handleProceed("pulse")}
                  size="lg"
                  variant="outline"
                  className="border-[#FF4D6D]/50 text-[#FF4D6D] hover:bg-[#FF4D6D]/10 rounded-full px-8 py-6 text-lg group"
                  data-testid="pulse-btn"
                >
                  <Heart className="w-5 h-5 mr-2 group-hover:heart-pulse" />
                  Check Relationship Pulse
                </Button>
                <Button
                  onClick={() => handleProceed("deep")}
                  size="lg"
                  className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-8 py-6 text-lg btn-glow"
                  data-testid="deep-analysis-btn"
                >
                  <Activity className="w-5 h-5 mr-2" />
                  Start Deep Analysis
                </Button>
              </motion.div>

              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.7, delay: 0.6 }}
                className="mt-12 text-sm text-muted-foreground/60"
              >
                Your privacy is protected. All analysis is anonymous and confidential.
              </motion.p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default ClarityMoment;

import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { TrustLensLogo, HeartLensIcon } from "@/components/custom/Logo";
import { useAnalysis } from "@/App";
import { Heart, Activity } from "lucide-react";

const ClarityMoment = () => {
  const { analysisType } = useAnalysis();
  const navigate = useNavigate();

  const handleProceed = (type) => {
    if (type === "pulse") {
      navigate("/pulse");
    } else {
      navigate("/analysis");
    }
  };

  return (
    <div className="min-h-screen bg-[#14213D] relative overflow-hidden flex items-center justify-center">
      {/* Background */}
      <div
        className="absolute inset-0 bg-cover bg-center opacity-20"
        style={{
          backgroundImage:
            "url(https://images.unsplash.com/photo-1765710029742-d92e3156a8f5?crop=entropy&cs=srgb&fm=jpg&q=85)",
        }}
      />
      <div className="absolute inset-0 bg-gradient-to-b from-[#14213D]/80 via-[#14213D]/90 to-[#14213D]" />

      {/* Content */}
      <div className="relative z-10 container mx-auto px-6 text-center max-w-2xl">
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
          className="text-4xl md:text-5xl font-light text-[#F5F7FA] mb-6 leading-tight"
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
            className="bg-[#2EC4B6] text-black hover:bg-[#259F94] rounded-full px-8 py-6 text-lg btn-glow"
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
      </div>
    </div>
  );
};

export default ClarityMoment;

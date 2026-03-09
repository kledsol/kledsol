import { motion } from "framer-motion";

export const TrustGauge = ({ value = 0 }) => {
  const getColor = (val) => {
    if (val < 25) return "#7BD389";
    if (val < 50) return "#2EC4B6";
    if (val < 75) return "#FCA311";
    return "#FF4D6D";
  };

  const color = getColor(value);
  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (value / 100) * circumference;

  return (
    <div className="relative w-48 h-48">
      <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
        {/* Background circle */}
        <circle
          cx="50"
          cy="50"
          r="45"
          fill="none"
          stroke="rgba(255,255,255,0.1)"
          strokeWidth="8"
        />
        {/* Progress arc */}
        <motion.circle
          cx="50"
          cy="50"
          r="45"
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1.5, ease: "easeOut" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <motion.span
          className="text-5xl font-light"
          style={{ color, fontFamily: 'Fraunces, serif' }}
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          {value.toFixed(0)}
        </motion.span>
        <span className="text-sm text-muted-foreground">/ 100</span>
      </div>
    </div>
  );
};

export const TrustIndexLabel = ({ value }) => {
  if (value < 20) return <span className="text-[#7BD389]">Minimal Disruption</span>;
  if (value < 40) return <span className="text-[#2EC4B6]">Mild Changes</span>;
  if (value < 60) return <span className="text-[#FCA311]">Noticeable Shift</span>;
  if (value < 80) return <span className="text-[#FF4D6D]">Significant Disruption</span>;
  return <span className="text-[#FF4D6D]">Critical Level</span>;
};

import { Heart } from "lucide-react";

export const StabilityHearts = ({ count = 4, size = "md" }) => {
  const sizes = {
    sm: "w-4 h-4",
    md: "w-6 h-6",
    lg: "w-8 h-8",
  };

  return (
    <div className="flex gap-1">
      {[...Array(4)].map((_, i) => (
        <Heart
          key={i}
          className={`${sizes[size]} ${
            i < count
              ? "fill-[#FF4D6D] text-[#FF4D6D]"
              : "fill-none text-white/20"
          } ${i < count ? "heart-pulse" : ""}`}
          style={{ animationDelay: `${i * 0.15}s` }}
        />
      ))}
    </div>
  );
};

export const StabilityLabel = ({ hearts }) => {
  if (hearts >= 4) return <span className="text-[#6EE7B7]">Stable</span>;
  if (hearts >= 3) return <span className="text-[#6EE7B7]">Mostly Stable</span>;
  if (hearts >= 2) return <span className="text-[#FCA311]">Moderate Strain</span>;
  if (hearts >= 1) return <span className="text-[#FF4D6D]">Significant Stress</span>;
  return <span className="text-[#FF4D6D]">Critical</span>;
};

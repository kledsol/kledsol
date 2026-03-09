import { Eye } from "lucide-react";

export const TrustLensLogo = ({ size = "md", animate = false }) => {
  const sizes = {
    sm: { text: "text-xl", lens: "w-5 h-5" },
    md: { text: "text-2xl", lens: "w-6 h-6" },
    lg: { text: "text-4xl", lens: "w-10 h-10" },
    xl: { text: "text-5xl", lens: "w-12 h-12" },
  };

  return (
    <div className="flex items-center gap-1">
      <span className={`font-light text-[#F5F7FA] tracking-tight ${sizes[size].text}`} style={{ fontFamily: 'Fraunces, serif' }}>
        Trust
      </span>
      <div className={`relative ${sizes[size].lens} ${animate ? 'lens-animate' : ''}`}>
        {/* Concentric circles lens */}
        <svg viewBox="0 0 40 40" className="w-full h-full">
          <circle cx="20" cy="20" r="18" fill="none" stroke="#2EC4B6" strokeWidth="1.5" opacity="0.3" />
          <circle cx="20" cy="20" r="13" fill="none" stroke="#2EC4B6" strokeWidth="1.5" opacity="0.5" />
          <circle cx="20" cy="20" r="8" fill="none" stroke="#2EC4B6" strokeWidth="1.5" opacity="0.7" />
          <circle cx="20" cy="20" r="3" fill="#2EC4B6" />
        </svg>
      </div>
      <span className={`font-light text-[#F5F7FA] tracking-tight ${sizes[size].text}`} style={{ fontFamily: 'Fraunces, serif' }}>
        ens
      </span>
    </div>
  );
};

export const HeartLensIcon = ({ size = 24, animate = false }) => {
  return (
    <div className={`relative ${animate ? 'lens-animate' : ''}`} style={{ width: size, height: size }}>
      <svg viewBox="0 0 40 40" className="w-full h-full">
        {/* Heart shape */}
        <path
          d="M20 35 C10 25 5 18 5 13 C5 8 9 4 14 4 C17 4 19 6 20 8 C21 6 23 4 26 4 C31 4 35 8 35 13 C35 18 30 25 20 35Z"
          fill="none"
          stroke="#FF4D6D"
          strokeWidth="1.5"
          opacity="0.8"
        />
        {/* Lens in center */}
        <circle cx="20" cy="17" r="6" fill="none" stroke="#2EC4B6" strokeWidth="1" opacity="0.5" />
        <circle cx="20" cy="17" r="3" fill="none" stroke="#2EC4B6" strokeWidth="1" opacity="0.7" />
        <circle cx="20" cy="17" r="1.5" fill="#2EC4B6" />
      </svg>
    </div>
  );
};

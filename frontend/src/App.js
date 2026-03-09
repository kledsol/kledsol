import { useState, useEffect, createContext, useContext } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import WelcomePage from "@/pages/WelcomePage";
import BaselineAssessment from "@/pages/BaselineAssessment";
import ChangeDetection from "@/pages/ChangeDetection";
import TimelineReconstruction from "@/pages/TimelineReconstruction";
import AdaptiveInvestigation from "@/pages/AdaptiveInvestigation";
import ResultsDashboard from "@/pages/ResultsDashboard";

// Theme Context
const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
};

const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("trustlens-theme") || "dark";
    }
    return "dark";
  });

  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove("light", "dark");
    root.classList.add(theme);
    localStorage.setItem("trustlens-theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// Analysis Context for session management
const AnalysisContext = createContext();

export const useAnalysis = () => {
  const context = useContext(AnalysisContext);
  if (!context) {
    throw new Error("useAnalysis must be used within an AnalysisProvider");
  }
  return context;
};

const AnalysisProvider = ({ children }) => {
  const [sessionId, setSessionId] = useState(null);
  const [currentStep, setCurrentStep] = useState("welcome");
  const [analysisData, setAnalysisData] = useState({
    baseline: null,
    changes: [],
    timeline: null,
    questionsAnswered: 0,
    trustIndex: 0,
  });

  const resetAnalysis = () => {
    setSessionId(null);
    setCurrentStep("welcome");
    setAnalysisData({
      baseline: null,
      changes: [],
      timeline: null,
      questionsAnswered: 0,
      trustIndex: 0,
    });
  };

  return (
    <AnalysisContext.Provider
      value={{
        sessionId,
        setSessionId,
        currentStep,
        setCurrentStep,
        analysisData,
        setAnalysisData,
        resetAnalysis,
      }}
    >
      {children}
    </AnalysisContext.Provider>
  );
};

function App() {
  return (
    <ThemeProvider>
      <AnalysisProvider>
        <div className="App min-h-screen bg-background">
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<WelcomePage />} />
              <Route path="/baseline" element={<BaselineAssessment />} />
              <Route path="/changes" element={<ChangeDetection />} />
              <Route path="/timeline" element={<TimelineReconstruction />} />
              <Route path="/investigation" element={<AdaptiveInvestigation />} />
              <Route path="/results" element={<ResultsDashboard />} />
            </Routes>
          </BrowserRouter>
          <Toaster position="top-right" />
        </div>
      </AnalysisProvider>
    </ThemeProvider>
  );
}

export default App;

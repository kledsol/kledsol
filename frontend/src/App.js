import { useState, createContext, useContext } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import LandingPage from "@/pages/LandingPage";
import ClarityMoment from "@/pages/ClarityMoment";
import RelationshipPulse from "@/pages/RelationshipPulse";
import DeepAnalysis from "@/pages/DeepAnalysis";
import ResultsDashboard from "@/pages/ResultsDashboard";
import MirrorMode from "@/pages/MirrorMode";
import ConversationCoach from "@/pages/ConversationCoach";

// Analysis Context
const AnalysisContext = createContext();

export const useAnalysis = () => {
  const context = useContext(AnalysisContext);
  if (!context) throw new Error("useAnalysis must be used within AnalysisProvider");
  return context;
};

const AnalysisProvider = ({ children }) => {
  const [sessionId, setSessionId] = useState(null);
  const [analysisType, setAnalysisType] = useState("pulse");
  const [currentStep, setCurrentStep] = useState(0);
  const [analysisData, setAnalysisData] = useState({
    baseline: null,
    changes: [],
    timeline: null,
    questionsAnswered: 0,
    trustIndex: 0,
    stabilityHearts: 4,
  });

  const resetAnalysis = () => {
    setSessionId(null);
    setAnalysisType("pulse");
    setCurrentStep(0);
    setAnalysisData({
      baseline: null,
      changes: [],
      timeline: null,
      questionsAnswered: 0,
      trustIndex: 0,
      stabilityHearts: 4,
    });
  };

  return (
    <AnalysisContext.Provider
      value={{
        sessionId,
        setSessionId,
        analysisType,
        setAnalysisType,
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
    <AnalysisProvider>
      <div className="App min-h-screen bg-[#0B132B]">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/clarity" element={<ClarityMoment />} />
            <Route path="/pulse" element={<RelationshipPulse />} />
            <Route path="/analysis" element={<DeepAnalysis />} />
            <Route path="/results" element={<ResultsDashboard />} />
            <Route path="/mirror" element={<MirrorMode />} />
            <Route path="/coach" element={<ConversationCoach />} />
          </Routes>
        </BrowserRouter>
        <Toaster position="top-right" />
      </div>
    </AnalysisProvider>
  );
}

export default App;

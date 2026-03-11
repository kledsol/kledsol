import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { TrustLensLogo } from "@/components/custom/Logo";
import { useAnalysis } from "@/App";
import { getMyAnalyses, getMe, authLogout } from "@/lib/api";
import { toast } from "sonner";
import AuthModal from "@/components/custom/AuthModal";
import {
  ArrowLeft,
  Clock,
  BarChart3,
  ChevronRight,
  LogOut,
  User,
  Shield,
} from "lucide-react";

const MyAnalyses = () => {
  const navigate = useNavigate();
  const { setSessionId } = useAnalysis();
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);
  const [showAuth, setShowAuth] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const stored = localStorage.getItem("trustlens_user");
      if (!stored) {
        setShowAuth(true);
        setLoading(false);
        return;
      }
      const me = await getMe();
      setUser(me);
      const data = await getMyAnalyses();
      setAnalyses(data.analyses || []);
    } catch {
      setShowAuth(true);
    } finally {
      setLoading(false);
    }
  };

  const handleAuthSuccess = async () => {
    setShowAuth(false);
    setLoading(true);
    try {
      const me = await getMe();
      setUser(me);
      const data = await getMyAnalyses();
      setAnalyses(data.analyses || []);
    } catch {
      toast.error("Failed to load analyses");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    authLogout();
    setUser(null);
    setAnalyses([]);
    localStorage.removeItem("trustlens_user");
    navigate("/");
  };

  const handleViewResults = (sessionId) => {
    setSessionId(sessionId);
    navigate("/results");
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "Unknown";
    try {
      return new Date(dateStr).toLocaleDateString("en-US", {
        month: "short", day: "numeric", year: "numeric", hour: "2-digit", minute: "2-digit",
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="min-h-screen bg-[#0B132B]">
      <header className="glass border-b border-white/10">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate("/")} className="text-white hover:bg-white/10">
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <Link to="/"><TrustLensLogo size="md" /></Link>
          </div>
          {user && (
            <div className="flex items-center gap-4">
              <span className="text-sm text-muted-foreground">{user.email}</span>
              <Button variant="ghost" size="sm" onClick={handleLogout} className="text-muted-foreground hover:text-white">
                <LogOut className="w-4 h-4 mr-1" /> Logout
              </Button>
            </div>
          )}
        </div>
      </header>

      <main className="container mx-auto px-6 py-12 max-w-3xl">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="text-center mb-10">
            <User className="w-10 h-10 text-[#3DD9C5] mx-auto mb-4" />
            <h1
              className="text-3xl font-light text-[#E6EDF3] mb-2"
              style={{ fontFamily: "Fraunces, serif" }}
              data-testid="my-analyses-title"
            >
              My Analyses
            </h1>
            <p className="text-muted-foreground">
              Track how your relationship signals evolve over time
            </p>
          </div>

          {loading ? (
            <div className="text-center py-16">
              <BarChart3 className="w-10 h-10 text-[#3DD9C5] animate-pulse mx-auto mb-4" />
              <p className="text-muted-foreground">Loading your history...</p>
            </div>
          ) : analyses.length === 0 ? (
            <Card className="glass-card rounded-2xl">
              <CardContent className="p-10 text-center">
                <Shield className="w-10 h-10 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg text-[#E6EDF3] mb-2">No saved analyses yet</h3>
                <p className="text-sm text-muted-foreground mb-6">
                  Complete an analysis and save it to start tracking your relationship signals.
                </p>
                <Button
                  onClick={() => navigate("/")}
                  className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-8 py-5 btn-glow"
                >
                  Start an Analysis
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4" data-testid="analyses-list">
              {analyses.map((a, i) => (
                <motion.div
                  key={a.session_id}
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.08 }}
                >
                  <Card
                    className="glass-card rounded-xl hover:border-[#3DD9C5]/30 transition-colors cursor-pointer"
                    onClick={() => handleViewResults(a.session_id)}
                    data-testid={`analysis-${i}`}
                  >
                    <CardContent className="p-5 flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-[#3DD9C5]/10 flex items-center justify-center">
                          <BarChart3 className="w-5 h-5 text-[#3DD9C5]" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-[#E6EDF3] capitalize">
                            {a.analysis_type === "deep" ? "Deep Analysis" : "Relationship Pulse"}
                          </p>
                          <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1">
                            <span className="flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {formatDate(a.created_at)}
                            </span>
                            {a.signal_count > 0 && (
                              <span>{a.signal_count} signals detected</span>
                            )}
                          </div>
                          {a.changes_detected?.length > 0 && (
                            <div className="flex gap-1.5 mt-2 flex-wrap">
                              {a.changes_detected.slice(0, 4).map((c) => (
                                <span key={c} className="text-[10px] bg-white/5 text-muted-foreground px-2 py-0.5 rounded-full">
                                  {c.replace(/_/g, " ")}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                      <ChevronRight className="w-5 h-5 text-muted-foreground" />
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      </main>

      <AuthModal
        open={showAuth}
        onClose={() => { setShowAuth(false); navigate("/"); }}
        onSuccess={handleAuthSuccess}
        mode="login"
      />
    </div>
  );
};

export default MyAnalyses;

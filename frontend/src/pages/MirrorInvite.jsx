import { useState, useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { TrustLensLogo, HeartLensIcon } from "@/components/custom/Logo";
import { useAnalysis } from "@/App";
import { joinMirrorSession, getMirrorStatus } from "@/lib/api";
import { toast } from "sonner";
import { Users, Shield, ArrowRight, Heart, Loader2, CheckCircle } from "lucide-react";

const MirrorInvite = () => {
  const { mirrorId } = useParams();
  const navigate = useNavigate();
  const { setSessionId } = useAnalysis();
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [joining, setJoining] = useState(false);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const data = await getMirrorStatus(mirrorId);
        setStatus(data);
      } catch {
        toast.error("This invitation link is invalid or has expired.");
      } finally {
        setLoading(false);
      }
    };
    fetchStatus();
  }, [mirrorId]);

  const handleJoin = async () => {
    setJoining(true);
    try {
      const data = await joinMirrorSession(mirrorId);
      setSessionId(data.session_id);
      // Store mirror context for after-analysis flow
      sessionStorage.setItem("trustlens_mirror", JSON.stringify({
        mirrorId,
        sessionId: data.session_id,
        role: "b",
      }));
      navigate("/analysis");
    } catch {
      toast.error("Failed to join. Please try again.");
    } finally {
      setJoining(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0B132B] flex items-center justify-center">
        <HeartLensIcon size={60} animate />
      </div>
    );
  }

  // Partner already joined and completed
  if (status?.partner_b_joined && status?.partner_b_complete) {
    return (
      <div className="min-h-screen bg-[#0B132B]">
        <header className="glass border-b border-white/10">
          <div className="container mx-auto px-6 py-4">
            <Link to="/"><TrustLensLogo size="md" /></Link>
          </div>
        </header>
        <main className="container mx-auto px-6 py-16 max-w-xl text-center">
          <CheckCircle className="w-16 h-16 text-[#3DD9C5] mx-auto mb-6" />
          <h1 className="text-3xl font-light text-[#E6EDF3] mb-4" style={{ fontFamily: "Fraunces, serif" }}>
            Analysis Already Completed
          </h1>
          <p className="text-muted-foreground mb-8">
            You have already completed your mirror analysis. If you've consented to share, you can view the comparison report.
          </p>
          <Button
            onClick={() => navigate(`/dual-report/${mirrorId}`)}
            className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-8 py-6 btn-glow"
          >
            View Dual Report
          </Button>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0B132B]">
      <header className="glass border-b border-white/10">
        <div className="container mx-auto px-6 py-4">
          <Link to="/"><TrustLensLogo size="md" /></Link>
        </div>
      </header>

      <main className="container mx-auto px-6 py-16 max-w-2xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <div className="relative inline-block mb-8">
            <div className="w-20 h-20 rounded-full bg-[#3DD9C5]/10 flex items-center justify-center mx-auto">
              <Users className="w-10 h-10 text-[#3DD9C5]" />
            </div>
            <div className="absolute -bottom-1 -right-1 w-8 h-8 rounded-full bg-[#0B132B] flex items-center justify-center">
              <Heart className="w-4 h-4 text-[#FF4D6D] fill-[#FF4D6D]" />
            </div>
          </div>

          <h1
            className="text-3xl sm:text-4xl font-light text-[#E6EDF3] mb-4"
            style={{ fontFamily: "Fraunces, serif" }}
            data-testid="mirror-invite-title"
          >
            Your partner invited you to a Mirror Analysis
          </h1>

          <p className="text-lg text-muted-foreground mb-10 max-w-lg mx-auto leading-relaxed">
            This is a private TrustLens analysis where both partners independently share
            their perspective on the relationship. The goal is to understand, not to accuse.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-4 mb-10"
        >
          {[
            {
              icon: Shield,
              title: "Your answers are private",
              desc: "Nothing you share will be visible to your partner unless you explicitly consent.",
            },
            {
              icon: Users,
              title: "Compare perspectives, not blame",
              desc: "Both analyses are compared only after both partners agree. The report highlights perception differences to help you understand each other better.",
            },
            {
              icon: Heart,
              title: "You are in control",
              desc: "You can complete the analysis and decide later whether to share your results. There is no obligation.",
            },
          ].map((item, i) => (
            <Card key={i} className="glass-card rounded-xl">
              <CardContent className="p-5 flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-[#3DD9C5]/10 flex items-center justify-center flex-shrink-0">
                  <item.icon className="w-5 h-5 text-[#3DD9C5]" />
                </div>
                <div>
                  <h3 className="text-sm font-medium text-[#E6EDF3] mb-1">{item.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{item.desc}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="text-center"
        >
          <Button
            onClick={handleJoin}
            disabled={joining}
            size="lg"
            className="bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full px-10 py-6 text-lg btn-glow"
            data-testid="begin-mirror-analysis-btn"
          >
            {joining ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Preparing...
              </>
            ) : (
              <>
                Begin My Analysis
                <ArrowRight className="w-5 h-5 ml-2" />
              </>
            )}
          </Button>
          <p className="text-xs text-muted-foreground mt-4">
            Anonymous. No account required. Your data stays private.
          </p>
        </motion.div>
      </main>
    </div>
  );
};

export default MirrorInvite;

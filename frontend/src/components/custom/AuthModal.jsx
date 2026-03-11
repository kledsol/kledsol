import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { authRegister, authLogin } from "@/lib/api";
import { toast } from "sonner";
import { X, Mail, Lock, Loader2, Shield } from "lucide-react";

const AuthModal = ({ open, onClose, onSuccess, mode: initialMode = "register" }) => {
  const [mode, setMode] = useState(initialMode);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  if (!open) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      toast.error("Please fill in both fields");
      return;
    }
    if (password.length < 6) {
      toast.error("Password must be at least 6 characters");
      return;
    }
    setLoading(true);
    try {
      const fn = mode === "register" ? authRegister : authLogin;
      const data = await fn(email.trim(), password);
      localStorage.setItem("trustlens_user", JSON.stringify({
        user_id: data.user_id,
        email: data.email,
      }));
      toast.success(mode === "register" ? "Account created" : "Logged in");
      onSuccess?.(data);
    } catch (err) {
      const msg = err.response?.data?.detail || "Something went wrong";
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4"
        onClick={(e) => e.target === e.currentTarget && onClose?.()}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
        >
          <Card className="glass-card rounded-2xl w-full max-w-md border-[#3DD9C5]/20" data-testid="auth-modal">
            <CardContent className="p-8">
              <div className="flex items-center justify-between mb-6">
                <h2
                  className="text-xl font-light text-[#E6EDF3]"
                  style={{ fontFamily: "Fraunces, serif" }}
                >
                  {mode === "register" ? "Create Account" : "Welcome Back"}
                </h2>
                <button
                  onClick={onClose}
                  className="text-muted-foreground hover:text-white transition-colors"
                  data-testid="close-auth-modal"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <p className="text-sm text-muted-foreground mb-6 leading-relaxed">
                {mode === "register"
                  ? "Save your analysis and track how your relationship signals evolve over time."
                  : "Log in to access your saved analyses and signal trends."}
              </p>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="relative">
                  <Mail className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
                  <Input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-10 bg-black/20 border-white/10 h-11"
                    data-testid="auth-email"
                  />
                </div>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
                  <Input
                    type="password"
                    placeholder="Password (min 6 characters)"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="pl-10 bg-black/20 border-white/10 h-11"
                    data-testid="auth-password"
                  />
                </div>
                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-[#3DD9C5] text-black hover:bg-[#28A89A] rounded-full py-5 btn-glow"
                  data-testid="auth-submit"
                >
                  {loading ? (
                    <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Processing...</>
                  ) : mode === "register" ? (
                    "Create Account"
                  ) : (
                    "Log In"
                  )}
                </Button>
              </form>

              <div className="mt-5 text-center">
                <button
                  onClick={() => setMode(mode === "register" ? "login" : "register")}
                  className="text-sm text-[#3DD9C5] hover:underline"
                  data-testid="auth-toggle"
                >
                  {mode === "register" ? "Already have an account? Log in" : "No account? Create one"}
                </button>
              </div>

              <div className="flex items-center gap-2 mt-5 justify-center">
                <Shield className="w-3.5 h-3.5 text-muted-foreground" />
                <p className="text-xs text-muted-foreground">
                  Optional. Your analysis can still be used anonymously.
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default AuthModal;

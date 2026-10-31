import { API_CONFIG } from "@/config/api.config";
import { Button } from "@/components/ui/button";

type OAuthProvider = "google" | "facebook";

const providers: { id: OAuthProvider; label: string }[] = [
  { id: "google", label: "Google" },
  { id: "facebook", label: "Facebook" },
];

export function OAuthButtons() {
  const startSignIn = (provider: OAuthProvider) => {
    window.location.assign(
      `${API_CONFIG.baseUrl}/api/v1/auth/oauth/${provider}`,
    );
  };

  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {providers.map((provider) => (
        <Button
          key={provider.id}
          type="button"
          variant="outline"
          onClick={() => startSignIn(provider.id)}
        >
          Continue with {provider.label}
        </Button>
      ))}
    </div>
  );
}

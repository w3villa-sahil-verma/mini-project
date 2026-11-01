import { API_CONFIG } from "@/config/api.config";
import { Button } from "@/components/ui/button";
import { IconBrandFacebook, IconBrandGoogle } from "./oauth-provider-icons";

type OAuthProvider = "google" | "facebook";

const providers: {
  id: OAuthProvider;
  label: string;
  Icon: typeof IconBrandGoogle;
}[] = [
  { id: "google", label: "Google", Icon: IconBrandGoogle },
  { id: "facebook", label: "Facebook", Icon: IconBrandFacebook },
];

export function OAuthButtons() {
  const startSignIn = (provider: OAuthProvider) => {
    window.location.assign(
      `${API_CONFIG.baseUrl}/api/v1/auth/oauth/${provider}`,
    );
  };

  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {providers.map(({ id, label, Icon }) => (
        <Button
          key={id}
          type="button"
          variant="outline"
          onClick={() => startSignIn(id)}
        >
          <Icon className="size-4" aria-hidden="true" />
          Continue with {label}
        </Button>
      ))}
    </div>
  );
}

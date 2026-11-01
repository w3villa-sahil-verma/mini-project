import type { SVGProps } from "react";

type ProviderIconProps = SVGProps<SVGSVGElement>;

export function IconBrandGoogle(props: ProviderIconProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 48 48"
      role="img"
      {...props}
    >
      <path
        fill="#4285F4"
        d="M48 24.55c0-1.57-.14-3.09-.4-4.55H24v9.02h13.47a11.5 11.5 0 0 1-5 7.55l7.98 6.19C45.1 38.3 48 31.97 48 24.55Z"
      />
      <path
        fill="#34A853"
        d="M24 49c6.48 0 11.93-2.15 15.9-5.8l-7.98-6.18c-2.16 1.45-4.92 2.3-7.92 2.3-6.08 0-11.24-4.1-13.08-9.62l-8.25 6.36C6.58 43.74 14.65 49 24 49Z"
        transform="translate(0 -1)"
      />
      <path
        fill="#FBBC05"
        d="M10.92 29.7a14.8 14.8 0 0 1 0-9.4l-8.25-6.36a24.05 24.05 0 0 0 0 22.12l8.25-6.36Z"
      />
      <path
        fill="#EA4335"
        d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.65 0 6.58 5.26 2.67 13.94l8.25 6.36C12.76 13.6 17.92 9.5 24 9.5Z"
      />
    </svg>
  );
}

export function IconBrandFacebook(props: ProviderIconProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 48 48"
      role="img"
      {...props}
    >
      <path
        fill="#1877F2"
        d="M48 24c0 12-8.8 22-20.3 23.7V30.9h5.6l1-6.9h-6.6v-4.5c0-1.9.9-3.7 3.8-3.7h3.1v-5.9s-2.8-.5-5.4-.5c-5.5 0-9.1 3.3-9.1 9.4V24H14v6.9h6.1v16.8C8.7 45.9 0 36 0 24 0 10.7 10.7 0 24 0s24 10.7 24 24Z"
      />
      <path
        fill="#fff"
        d="M33.3 30.9 34.3 24h-6.6v-4.5c0-1.9.9-3.7 3.8-3.7h3.1V10s-2.8-.5-5.4-.5c-5.5 0-9.1 3.3-9.1 9.4V24H14v6.9h6.1v16.8a24.3 24.3 0 0 0 7.6 0V30.9h5.6Z"
      />
    </svg>
  );
}

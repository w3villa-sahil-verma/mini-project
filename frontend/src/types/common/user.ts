export const USER_ROLE = {
    ADMIN : "ADMIN",
    USER : "USER"
} as const;

export type USER_ROLE = (typeof USER_ROLE)[keyof typeof USER_ROLE];

export type User = {
  user_id: string;
  role: USER_ROLE;
};

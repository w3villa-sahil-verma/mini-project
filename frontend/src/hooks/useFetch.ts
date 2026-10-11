import { API_CONFIG } from "@/config/api.config";
import { logger } from "@/utils/logger";
import React from "react";

type HandleRequestData<T> = (payload: T) => void;
type HandleRequestError = (error: Error) => void;

export type FetchConfig = {
  baseUrl?: string;
  headers?: HeadersInit;
};

const defaultConfig: FetchConfig = {
  baseUrl: "",
  headers: {
    "Content-Type": "application/json",
  },
};

function buildUrl(input: RequestInfo, baseUrl?: string): RequestInfo {
  if (!baseUrl || typeof input !== "string") {
    return input;
  }

  return `${baseUrl}${input}`;
}

function buildInit(
  init?: RequestInit,
  config?: FetchConfig,
): RequestInit {
  return {
    ...init,
    headers: {
      ...config?.headers,
      ...init?.headers,
    },
  };
}

export async function handleFetch<T>(
  input: RequestInfo,
  onData?: HandleRequestData<T>,
  onError?: HandleRequestError,
  init?: RequestInit,
  config: FetchConfig = {...defaultConfig, ...API_CONFIG},
) {
  try {
    logger.debug("Invoke fetch");

    const url = buildUrl(input, config.baseUrl);
    const requestInit = buildInit(init, config);

    const res = await fetch(url, requestInit);

    if (!res.ok) {
      throw new Error(`Request failed with status ${res.status}`);
    }

    const payload: T = await res.json();
    onData?.(payload);
  } catch (error) {
    if (error instanceof Error) {
      logger.error(error);
      onError?.(error);
    }
  }
}

export function useFetch<T>(
  input: RequestInfo,
  onData?: HandleRequestData<T>,
  onError?: HandleRequestError,
  init?: RequestInit,
  dependencies?: React.DependencyList,
  config: FetchConfig = defaultConfig,
) {
  React.useEffect(() => {
    handleFetch(input, onData, onError, init, config);
  }, dependencies);
}
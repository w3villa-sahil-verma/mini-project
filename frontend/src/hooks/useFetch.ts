import { API_CONFIG } from "@/config/api.config";
import { logger } from "@/utils/logger";
import React, { useState } from "react";

type HandleRequestData<T> = (payload: T) => void;
type HandleRequestError = (error: Error) => void;

export type FetchConfig = {
  baseUrl?: string;
  headers?: HeadersInit;
} & RequestInit;

export class HttpError extends Error {
  readonly status: number;

  constructor(status: number) {
    super(`Request failed with status ${status}`);
    this.name = "HttpError";
    this.status = status;
  }
}

const defaultConfig: FetchConfig = {
  baseUrl: "",
};

function buildUrl(input: RequestInfo, baseUrl?: string): RequestInfo {
  if (!baseUrl || typeof input !== "string") {
    return input;
  }

  return `${baseUrl}${input}`;
}

function buildInit(init?: RequestInit, config?: FetchConfig): RequestInit {
  return {
    ...config,
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
  config: FetchConfig = { ...defaultConfig, ...API_CONFIG },
) {
  try {
    const url = buildUrl(input, config.baseUrl);
    const requestInit = buildInit(init, config);

    const res = await fetch(url, requestInit);

    if (!res.ok) {
      throw new HttpError(res.status);
    }

    const payload: T = await res.json();
    onData?.(payload);
  } catch (error) {
    if (error instanceof Error) {
      if (!(error instanceof HttpError && error.status === 401)) {
        logger.error(error);
      }
      onError?.(error);
    }
  }
}

export function useFetch<T>(
  input: RequestInfo,
  onData?: HandleRequestData<T>,
  onError?: HandleRequestError,
  dependencies?: React.DependencyList,
  init?: RequestInit,
  config: FetchConfig = {...defaultConfig, ...API_CONFIG},
) {
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    (async () => {
      setLoading(true);
      await handleFetch(input, onData, onError, init, config);
      setLoading(false)
    })();
  }, dependencies);

  return [loading];
}

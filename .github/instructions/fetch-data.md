---
title : Fetching data at frontend side.
description : utility and hook use to fetch data at frontend side. in react
---

# Utility

`path : "@/hooks/useFetch.ts"`

```ts
import { API_CONFIG } from "@/config/api.config";
import { logger } from "@/utils/logger";
import React from "react";

type HandleRequestData<T> = (payload: T) => void;
type HandleRequestError = (error: Error) => void;

export type FetchConfig = {
  baseUrl?: string;
  headers?: HeadersInit;
} & RequestInit;

const defaultConfig: FetchConfig = {
  baseUrl: "",
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
  config: FetchConfig = {...defaultConfig, ...API_CONFIG},
) {
  try {
    const url = buildUrl(input, config.baseUrl);
    const requestInit = buildInit(init, config);

    logger.debug(requestInit)

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
```


## use handleFetch

- use it inside normal handler where hooks are not able to use.

### Example

```ts
  const handleSubmit = async (e: React.SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();

    setLoading(true);
    await handleFetch<CommonResponse<any>>(
      `/api/v1/auth/standard/register`,
      (resp) => {
        logger.debug("Data received:", resp);
        toast.success(resp.message)
        navigate("/user/dashboard")
      },
      (error) => {
        logger.error("Error occurred:", error);
        toast.error(error.message)
      },
      {
        method: "POST",
        body: JSON.stringify(requestPayload),
      },
    );
    setLoading(false);
  };
```
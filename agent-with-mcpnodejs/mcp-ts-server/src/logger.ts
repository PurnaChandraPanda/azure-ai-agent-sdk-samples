// src/logger.ts

export type LogLevel = "debug" | "info" | "warn" | "error";

const LOG_LEVEL_ORDER: Record<LogLevel, number> = {
  debug: 10,
  info: 20,
  warn: 30,
  error: 40
};

const configuredLevel = (process.env.LOG_LEVEL ?? "info").toLowerCase() as LogLevel;

function shouldLog(level: LogLevel): boolean {
  const activeLevel = LOG_LEVEL_ORDER[configuredLevel] ?? LOG_LEVEL_ORDER.info;
  return LOG_LEVEL_ORDER[level] >= activeLevel;
}

function maskSensitiveData(data: unknown): unknown {
  const sensitiveKeys = new Set([
    "authorization",
    "apiKey",
    "api_key",
    "password",
    "token",
    "accessToken",
    "refreshToken",
    "secret"
  ]);

  function mask(value: unknown): unknown {
    if (Array.isArray(value)) {
      return value.map(mask);
    }

    if (value && typeof value === "object") {
      const obj = value as Record<string, unknown>;
      const masked: Record<string, unknown> = {};

      for (const [key, val] of Object.entries(obj)) {
        if (sensitiveKeys.has(key)) {
          masked[key] = "***MASKED***";
        } else {
          masked[key] = mask(val);
        }
      }

      return masked;
    }

    return value;
  }

  return mask(data);
}

function writeLog(level: LogLevel, message: string, data?: unknown): void {
  if (!shouldLog(level)) {
    return;
  }

  const logEntry = {
    timestamp: new Date().toISOString(),
    level,
    message,
    ...(data !== undefined ? { data: maskSensitiveData(data) } : {})
  };

  const line = JSON.stringify(logEntry);

  if (level === "error") {
    console.error(line);
  } else if (level === "warn") {
    console.warn(line);
  } else {
    console.log(line);
  }
}

export function logDebug(message: string, data?: unknown): void {
  writeLog("debug", message, data);
}

export function logInfo(message: string, data?: unknown): void {
  writeLog("info", message, data);
}

export function logWarn(message: string, data?: unknown): void {
  writeLog("warn", message, data);
}

export function logError(message: string, error?: unknown, data?: unknown): void {
  const errorPayload =
    error instanceof Error
      ? {
          name: error.name,
          message: error.message,
          stack: error.stack
        }
      : error;

  writeLog("error", message, {
    error: errorPayload,
    ...(data !== undefined ? { context: data } : {})
  });
}

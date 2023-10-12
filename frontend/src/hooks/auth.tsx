import axios, { AxiosError } from "axios";
import { api, apiNoRetry } from "constants/backend";
import React, { useEffect } from "react";
import { Navigate, useNavigate, useSearchParams } from "react-router-dom";

const REFRESH_TOKEN_KEY = "__DPSH_REFRESH_TOKEN";
const SESSION_TOKEN_KEY = "__DPSH_SESSION_TOKEN";

type TokenType = "refresh" | "session";

const getLocalStorageValueKey = (tokenType: TokenType) => {
  switch (tokenType) {
    case "refresh":
      return REFRESH_TOKEN_KEY;
    case "session":
      return SESSION_TOKEN_KEY;
    default:
      throw new Error("Invalid token type");
  }
};

interface RequiresLoginProps {
  children: React.ReactNode;
}

export const getToken = (tokenType: TokenType): string | null => {
  return localStorage.getItem(getLocalStorageValueKey(tokenType));
};

export const setToken = (token: string, tokenType: TokenType) => {
  localStorage.setItem(getLocalStorageValueKey(tokenType), token);
};

export const deleteToken = (tokenType: TokenType) => {
  localStorage.removeItem(getLocalStorageValueKey(tokenType));
};

export const deleteTokens = () => {
  deleteToken("refresh");
  deleteToken("session");
};

// Add the token to the Authorization header for every request, and invalidate
// the token if the server returns a 401.
api.interceptors.request.use(
  (config) => {
    const token = getToken("session");
    if (token !== null) {
      config.headers.Authorization = `Bearer ${token}`;
      config.headers["Access-Control-Allow-Origin"] = "*";
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

interface RefreshTokenResponse {
  token: string;
  token_type: string;
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = getToken("refresh");
      if (refreshToken === null) {
        return Promise.reject(error);
      }

      let sessionToken;
      try {
        // Gets a new token using the refresh token.
        const response = await apiNoRetry.post<RefreshTokenResponse>(
          "/users/refresh",
          {},
          {
            headers: {
              Authorization: `Bearer ${refreshToken}`,
              "Access-Control-Allow-Origin": "*",
            },
          },
        );
        sessionToken = response.data.token;
      } catch (refreshError) {
        if (axios.isAxiosError(refreshError)) {
          const axiosRefreshError = refreshError as AxiosError;
          if (axiosRefreshError.response?.status === 401) {
            deleteToken("session");
            const navigate = useNavigate();
            navigate("/login");
          }
        }
        return Promise.reject(refreshError);
      }

      // Retries the original request with the new token.
      setToken(sessionToken, "session");
      originalRequest.headers.Authorization = `Bearer ${sessionToken}`;
      return await api(originalRequest);
    }
    return Promise.reject(error);
  },
);

export const RequiresLogin = ({ children }: RequiresLoginProps) => {
  if (getToken("refresh") === null) {
    // const redirect = window.location.pathname;
    // Using HashRouter, so we need to include the hash in the redirect
    const redirect = window.location.hash.substring(1);
    return <Navigate to={`/login?redirect=${redirect}`} />;
  }
  return <>{children}</>;
};

interface OneTimePasswordWrapperProps {
  children: React.ReactNode;
}

interface UserLoginResponse {
  token: string;
  token_type: string;
}

export const OneTimePasswordWrapper = ({
  children,
}: OneTimePasswordWrapperProps) => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      const payload = searchParams.get("otp");
      if (payload !== null) {
        try {
          const response = await apiNoRetry.post<UserLoginResponse>(
            "/users/otp",
            {
              payload,
            },
          );
          setToken(response.data.token, "refresh");
          navigate("/");
        } catch (error) {
        } finally {
          searchParams.delete("otp");
        }
      }
    })();
  }, [searchParams, navigate]);

  return <>{children}</>;
};

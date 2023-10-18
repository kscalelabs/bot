import axios, { AxiosError, AxiosInstance } from "axios";
import { BACKEND_URL } from "constants/backend";
import React, { createContext, useCallback, useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

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

const getLocalStorageToken = (tokenType: TokenType): string | null => {
  return localStorage.getItem(getLocalStorageValueKey(tokenType));
};

const setLocalStorageToken = (token: string, tokenType: TokenType) => {
  localStorage.setItem(getLocalStorageValueKey(tokenType), token);
};

const deleteLocalStorageToken = (tokenType: TokenType) => {
  localStorage.removeItem(getLocalStorageValueKey(tokenType));
};

interface AuthenticationContextProps {
  sessionToken: string | null;
  setSessionToken: (token: string) => void;
  refreshToken: string | null;
  setRefreshToken: (token: string) => void;
  logout: () => void;
  isAuthenticated: boolean;
  api: AxiosInstance;
}

interface RefreshTokenResponse {
  token: string;
  token_type: string;
}

const AuthenticationContext = createContext<
  AuthenticationContextProps | undefined
>(undefined);

interface AuthenticationProviderProps {
  children: React.ReactNode;
}

export const refreshSessionToken = async (
  api: AxiosInstance,
  refreshToken: string
) => {
  const response = await api.post<RefreshTokenResponse>(
    "/users/refresh",
    {},
    {
      headers: {
        Authorization: `Bearer ${refreshToken}`,
        "Access-Control-Allow-Origin": "*",
      },
    }
  );
  return response.data.token;
};

export const AuthenticationProvider = (props: AuthenticationProviderProps) => {
  const { children } = props;

  const [sessionToken, setSessionToken] = useState<string | null>(
    getLocalStorageToken("session")
  );
  const [refreshToken, setRefreshToken] = useState<string | null>(
    getLocalStorageToken("refresh")
  );

  const isAuthenticated = sessionToken !== null;

  const api = axios.create({
    withCredentials: true,
    baseURL: BACKEND_URL,
  });

  useEffect(() => {
    if (sessionToken === null) {
      deleteLocalStorageToken("session");
    } else {
      setLocalStorageToken(sessionToken, "session");
    }
  }, [sessionToken]);

  useEffect(() => {
    if (refreshToken === null) {
      deleteLocalStorageToken("refresh");
    } else {
      setLocalStorageToken(refreshToken, "refresh");
    }
  }, [refreshToken]);

  useEffect(() => {
    if (refreshToken !== null && sessionToken === null) {
      (async () => {
        const localSessionToken = await refreshSessionToken(api, refreshToken);
        setSessionToken(localSessionToken);
      })();
    }
  }, [refreshToken, sessionToken, api]);

  const logout = useCallback(() => {
    setSessionToken(null);
    setRefreshToken(null);
  }, []);

  api.interceptors.request.use(
    (config) => {
      if (sessionToken !== null) {
        config.headers.Authorization = `Bearer ${sessionToken}`;
        config.headers["Access-Control-Allow-Origin"] = "*";
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  api.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;
      if (error.response.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;
        if (refreshToken === null) {
          return Promise.reject(error);
        }

        try {
          // Gets a new session token and try the request again.
          const localSessionToken = await refreshSessionToken(
            api,
            refreshToken
          );
          setSessionToken(localSessionToken);
          originalRequest.headers.Authorization = `Bearer ${localSessionToken}`;
          return await api(originalRequest);
        } catch (refreshError) {
          if (axios.isAxiosError(refreshError)) {
            const axiosError = refreshError as AxiosError;
            if (axiosError?.response?.status === 401) {
              logout();
            }
          }
          return Promise.reject(refreshError);
        }
      }

      return Promise.reject(error);
    }
  );

  return (
    <AuthenticationContext.Provider
      value={{
        sessionToken,
        setSessionToken,
        refreshToken,
        setRefreshToken,
        logout,
        isAuthenticated,
        api,
      }}
    >
      {children}
    </AuthenticationContext.Provider>
  );
};

export const useAuthentication = (): AuthenticationContextProps => {
  const context = React.useContext(AuthenticationContext);
  if (!context) {
    throw new Error(
      "useAuthentication must be used within a AuthenticationProvider"
    );
  }
  return context;
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
  const { setRefreshToken, api } = useAuthentication();

  useEffect(() => {
    (async () => {
      const payload = searchParams.get("otp");
      if (payload !== null) {
        try {
          const response = await api.post<UserLoginResponse>("/users/otp", {
            payload,
          });
          setRefreshToken(response.data.token);
          navigate("/");
        } catch (error) {
        } finally {
          searchParams.delete("otp");
        }
      }
    })();
  }, [searchParams, navigate, setRefreshToken, api]);

  return <>{children}</>;
};

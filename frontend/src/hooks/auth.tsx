import { api } from "constants/backend";
import React, { useEffect } from "react";
import { Navigate, useNavigate, useSearchParams } from "react-router-dom";

const TOKEN_VALUE_KEY = "__DPSH_TOKEN_VALUE";
const TOKEN_TYPE_KEY = "__DPSH_TOKEN_TYPE";

interface RequiresLoginProps {
  children: React.ReactNode;
}

export const getToken = (): [string, string] | null => {
  const tokenValue = localStorage.getItem(TOKEN_VALUE_KEY);
  if (tokenValue === null) return null;
  const tokenType = localStorage.getItem(TOKEN_TYPE_KEY);
  if (tokenType === null) return null;
  return [tokenValue, tokenType];
};

export const setToken = (token: [string, string]) => {
  const [tokenValue, tokenType] = token;
  localStorage.setItem(TOKEN_VALUE_KEY, tokenValue);
  localStorage.setItem(TOKEN_TYPE_KEY, tokenType);
};

export const deleteToken = () => {
  localStorage.removeItem(TOKEN_VALUE_KEY);
  localStorage.removeItem(TOKEN_TYPE_KEY);
};

api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token !== null) {
      const [tokenValue, tokenType] = token;
      config.headers.Authorization = `${tokenType} ${tokenValue}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response.status === 401) {
      const navigate = useNavigate();
      deleteToken();
      navigate("/login");
    }
    return Promise.reject(error);
  }
);

export const RequiresLogin = ({ children }: RequiresLoginProps) => {
  if (getToken() === null) {
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

  useEffect(() => {
    (async () => {
      const payload = searchParams.get("otp");
      if (payload !== null) {
        try {
          const response = await api.post<UserLoginResponse>("/users/otp", {
            payload,
          });
          setToken([response.data.token, response.data.token_type]);
        } catch (error) {
        } finally {
          searchParams.delete("otp");
        }
      }
    })();
  }, [searchParams]);

  return <>{children}</>;
};

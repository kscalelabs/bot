import React, { createContext, useContext, useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

const TOKEN_VALUE_KEY = "__DPSH_TOKEN_VALUE";
const TOKEN_TYPE_KEY = "__DPSH_TOKEN_TYPE";

interface TokenContextProps {
  token: [string, string] | null;
  setToken: (token: [string, string] | null) => void;
}

const TokenContext = createContext<TokenContextProps | null>(null);

interface TokenProviderProps {
  children: React.ReactNode;
}

export const TokenProvider = ({ children }: TokenProviderProps) => {
  const tokenValue = localStorage.getItem(TOKEN_VALUE_KEY);
  const tokenType = localStorage.getItem(TOKEN_TYPE_KEY);
  const [token, setToken] = useState<[string, string] | null>(
    tokenValue && tokenType ? [tokenValue, tokenType] : null
  );

  useEffect(() => {
    if (token) {
      const [tokenValue, tokenType] = token;
      localStorage.setItem(TOKEN_VALUE_KEY, tokenValue);
      localStorage.setItem(TOKEN_TYPE_KEY, tokenType);
    } else {
      localStorage.removeItem(TOKEN_VALUE_KEY);
      localStorage.removeItem(TOKEN_TYPE_KEY);
    }
  }, [token]);

  return (
    <TokenContext.Provider value={{ token, setToken }}>
      {children}
    </TokenContext.Provider>
  );
};

export const useToken = () => {
  const context = useContext(TokenContext);
  if (!context) {
    throw new Error("useToken must be used within a TokenProvider");
  }
  return context;
};

interface RequiresLoginProps {
  children: React.ReactNode;
}

export const RequiresLogin = ({ children }: RequiresLoginProps) => {
  const { token } = useToken();
  if (token === null) {
    // const redirect = window.location.pathname;
    // Using HashRouter, so we need to include the hash in the redirect
    const redirect = window.location.hash.substring(1);
    return <Navigate to={`/login?redirect=${redirect}`} />;
  }
  return <>{children}</>;
};

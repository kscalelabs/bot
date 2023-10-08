import React, { createContext, useContext, useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

const TOKEN_KEY = "token";

interface TokenContextProps {
  token: string | null;
  setToken: (token: string | null) => void;
}

const TokenContext = createContext<TokenContextProps | null>(null);

interface TokenProviderProps {
  children: React.ReactNode;
}

export const TokenProvider = ({ children }: TokenProviderProps) => {
  const [token, setToken] = useState<string | null>(
    localStorage.getItem(TOKEN_KEY)
  );

  useEffect(() => {
    if (token === null) {
      localStorage.removeItem(TOKEN_KEY);
    } else {
      localStorage.setItem(TOKEN_KEY, token);
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

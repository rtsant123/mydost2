import React, { useEffect } from 'react';
import { SessionProvider } from 'next-auth/react';
import '@/styles/globals.css';

function MyApp({ Component, pageProps: { session, ...pageProps } }) {
  useEffect(() => {
    // Check for dark mode preference
    if (
      localStorage.getItem('darkMode') === 'true' ||
      (!localStorage.getItem('darkMode') &&
        window.matchMedia('(prefers-color-scheme: dark)').matches)
    ) {
      document.documentElement.classList.add('dark');
    }
  }, []);

  return (
    <SessionProvider session={session}>
      <Component {...pageProps} />
    </SessionProvider>
  );
}

export default MyApp;

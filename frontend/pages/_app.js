import React, { useEffect } from 'react';
import '@/styles/globals.css';

function MyApp({ Component, pageProps }) {
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

  return <Component {...pageProps} />;
}

export default MyApp;

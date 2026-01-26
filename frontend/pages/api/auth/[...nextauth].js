import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://mydost2-production.up.railway.app";

export const authOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    }),
  ],
  callbacks: {
    async signIn({ user, account, profile }) {
      try {
        // Check if user exists in backend
        const response = await axios.post(`${API_URL}/auth/google-signin`, {
          email: user.email,
          name: user.name,
          image: user.image,
          google_id: account.providerAccountId,
        });

        // Attach user ID and preferences to session
        user.id = response.data.user_id;
        user.has_preferences = response.data.has_preferences;
        user.preferences = response.data.preferences;
        
        return true;
      } catch (error) {
        console.error("Sign in error:", error);
        return false;
      }
    },
    async session({ session, token }) {
      // Add user ID and preferences to session
      session.user.id = token.id;
      session.user.has_preferences = token.has_preferences;
      session.user.preferences = token.preferences;
      return session;
    },
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.has_preferences = user.has_preferences;
        token.preferences = user.preferences;
      }
      return token;
    },
  },
  pages: {
    signIn: "/auth/signin",
    newUser: "/preferences", // Redirect to preferences on first sign up
  },
  session: {
    strategy: "jwt",
  },
  secret: process.env.NEXTAUTH_SECRET,
};

export default NextAuth(authOptions);

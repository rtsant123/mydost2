import { signIn } from "next-auth/react";
import { Chrome } from "lucide-react";

export default function SignIn() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-xl max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Welcome to MyDost
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Your friendly AI assistant
          </p>
        </div>

        <button
          onClick={() => signIn("google", { callbackUrl: "/" })}
          className="w-full flex items-center justify-center gap-3 bg-white dark:bg-gray-700 border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 px-6 py-3 rounded-lg font-medium hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
        >
          <Chrome className="w-5 h-5" />
          Sign in with Google
        </button>

        <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-6">
          By signing in, you agree to our Terms of Service
        </p>
      </div>
    </div>
  );
}

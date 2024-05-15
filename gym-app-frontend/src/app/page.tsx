import Layout from "./components/Layout";
import { AuthProvider } from "./components/AuthContext";

export default function Home() {
  return (
    <Layout>
      <AuthProvider>
        <div>
          <h2 className="text-2xl mb-10 text-center">Welcome to the Gym App</h2>
        </div>
      </AuthProvider>
    </Layout>
  );
}

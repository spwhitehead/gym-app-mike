import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./styles/globals.css";
import Header from "../../components/Header";
import Footer from "../../components/Footer";

const RootLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <html lang="en">
    <body>
      <Header />
      <main className="container mx-auto p-4">{children}</main>
      <Footer />
    </body>
  </html>
);

export default RootLayout;

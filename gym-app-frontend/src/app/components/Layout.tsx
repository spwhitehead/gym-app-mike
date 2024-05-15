import "@/app/styles/globals.css";
export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <main className="container mx-auto p-4">{children}</main>
    </>
  );
}

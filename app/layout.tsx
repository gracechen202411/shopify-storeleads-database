import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "豆豆 & 唯一专属数据库 - 励志成为谷歌 Top Sales",
  description: "豆豆 & 唯一的销售宝库 - 挖掘全球 Shopify 店铺，冲向销售巅峰！",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}

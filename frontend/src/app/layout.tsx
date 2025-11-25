import type { Metadata } from 'next';
import { Noto_Sans_SC } from 'next/font/google';
import '../styles/globals.scss';
import Providers from '@/components/Providers';

const noto = Noto_Sans_SC({
  subsets: ['latin'],
  weight: ['400'],
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'Chat App',
  description: 'AI Chat with Gemini',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
        <body className={noto.className}>
          <Providers>{children}</Providers>
        </body>
      </html>
  );
}
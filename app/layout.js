import './styles/globals.css';
import { Roboto } from 'next/font/google'; 

const roboto = Roboto({
  weight: ['400', '500', '700'],
  subsets: ['latin'],
});

export default function RootLayout({ children }) {
  return (
    <html lang="ru">
      <head>
        <meta charSet="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Подбор подарков</title>
      </head>
      <body className={roboto.className}>
        <div className="min-h-screen bg-gray-100">
          <header className="bg-orange-500 text-white py-4">
            <div className="container mx-auto text-center">
              <h1 className="text-3xl font-bold">DNS-Shop Gift Picker</h1>
            </div>
          </header>
          <main className="container mx-auto p-6">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}

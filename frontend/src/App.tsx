import { useState, useEffect } from "react";
import { Toaster } from "react-hot-toast";
import ChatInterface from "./components/ChatInterface";
import ThemeToggleButton from "./components/ThemeToggleButton";
import "./App.scss";
import { useChat } from "./context/ChatContext";

function App() {
  const { messages } = useChat();
  const [theme, setTheme] = useState<"light" | "dark">(
    window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"
  ); // Get system theme

  // Toggle theme function
  const toggleTheme = (): void => {
    setTheme((prevTheme) => (prevTheme === "dark" ? "light" : "dark"));
  };

  // Apply theme class to body
  useEffect(() => {
    document.body.className = theme + "-mode";
  }, [theme]);

  return (
    <div className="App">
      <Toaster
        position="bottom-right"
        containerStyle={{
          bottom: 100,
        }}
        toastOptions={{
          className: "toast-with-progress",
          style: {
            background: theme === "dark" ? "#333" : "#fff",
            color: theme === "dark" ? "#fff" : "#333",
            borderRadius: "10px",
            overflow: "hidden", // Needed for progress bar
          },
          error: {
            duration: 5000, // 5 seconds
            iconTheme: {
              primary: "#ff4b4b",
              secondary: "#fff",
            },
          },
        }}
      />
      <ThemeToggleButton theme={theme} toggleTheme={toggleTheme} />
      <div className={`header ${messages.length === 0 ? "empty-header" : ""}`}>
        <h1><span style={{ verticalAlign: "middle" }}>🏝️</span> 다음 여행지는 어디인가요?</h1>
      </div>
      <ChatInterface />
    </div>
  );
}

export default App;

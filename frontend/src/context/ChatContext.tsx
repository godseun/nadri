import { createContext, useContext, useState, useRef, useEffect } from "react";
import toast from "react-hot-toast";

interface Message {
  id: number;
  text: string[];
  sender: "user" | "bot";
  error?: boolean;
}

interface ChatContextType {
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  input: string;
  setInput: React.Dispatch<React.SetStateAction<string>>;
  isTyping: boolean;
  setIsTyping: React.Dispatch<React.SetStateAction<boolean>>;
  inputRef: React.RefObject<HTMLTextAreaElement | null>;
  messagesEndRef: React.RefObject<HTMLDivElement | null>;
  messagesContainerRef: React.RefObject<HTMLDivElement | null>;
  showScrollButton: boolean;
  setShowScrollButton: React.Dispatch<React.SetStateAction<boolean>>;
  handleScroll: () => void;
  scrollToBottom: () => void;
  sendMessage: (messageText: string) => Promise<void>;
  stopStreaming: () => void;
  resendMessage: (messageId: number) => Promise<void>;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const [showScrollButton, setShowScrollButton] = useState<boolean>(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleScroll = () => {
    if (messagesContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } =
        messagesContainerRef.current;
      if (scrollHeight - scrollTop > clientHeight + 100) {
        setShowScrollButton(true);
      } else {
        setShowScrollButton(false);
      }
    }
  };

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  const stopStreaming = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsTyping(false);
    }
  };

  const sendMessage = async (messageText: string) => {
    if (messageText.trim() === "" || isTyping) return;

    const userMessage: Message = {
      id: Date.now(),
      text: [messageText],
      sender: "user",
      error: false,
    };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInput("");
    setIsTyping(true);

    if (inputRef.current) {
      inputRef.current.style.height = "auto";
    }

    await fetchBotResponse(messageText, userMessage.id);
  };

  const resendMessage = async (messageId: number) => {
    const messageToResend = messages.find((msg) => msg.id === messageId);
    if (!messageToResend || isTyping) return;

    // Set error to false before resending
    setMessages((prev) =>
      prev.map((msg) => (msg.id === messageId ? { ...msg, error: false } : msg))
    );
    setIsTyping(true);

    await fetchBotResponse(messageToResend.text[0], messageId);
  };

  const fetchBotResponse = async (prompt: string, messageId: number) => {
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;
    const apiUrl = process.env.REACT_APP_API_URL;

    if (!apiUrl) {
      console.error("REACT_APP_API_URL is not defined");
      setIsTyping(false);
      return;
    }

    try {
      const response = await fetch(`${apiUrl}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
        signal,
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      if (!response.body) {
        setIsTyping(false);
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      let botMessageAdded = false;

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.substring(6);
            if (data.trim() === "[DONE]") break;

            try {
              const jsonData = JSON.parse(data);
              if (jsonData.type === "error") {
                toast.error(jsonData.message);
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === messageId ? { ...msg, error: true } : msg
                  )
                );
                // Stop processing further messages in this stream
                return;
              }
            } catch (e) {
              // Not a JSON error message, treat as normal text
              if (!botMessageAdded) {
                setMessages((prevMessages) => [
                  ...prevMessages,
                  { id: Date.now(), text: [data], sender: "bot" },
                ]);
                botMessageAdded = true;
              } else {
                setMessages((prevMessages) => {
                  const updatedMessages = [...prevMessages];
                  const lastBotMessageIndex = updatedMessages.length - 1;
                  if (
                    updatedMessages[lastBotMessageIndex] &&
                    updatedMessages[lastBotMessageIndex].sender === "bot"
                  ) {
                    updatedMessages[lastBotMessageIndex] = {
                      ...updatedMessages[lastBotMessageIndex],
                      text: [
                        ...updatedMessages[lastBotMessageIndex].text,
                        data,
                      ],
                    };
                  }
                  return updatedMessages;
                });
              }
            }
          }
        }
      }
    } catch (error) {
      if ((error as Error).name !== "AbortError") {
        toast.error("서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.");
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === messageId ? { ...msg, error: true } : msg
          )
        );
      }
    } finally {
      setIsTyping(false);
      abortControllerRef.current = null;
    }
  };

  const value = {
    messages,
    setMessages,
    input,
    setInput,
    isTyping,
    setIsTyping,
    inputRef,
    messagesEndRef,
    messagesContainerRef,
    showScrollButton,
    setShowScrollButton,
    handleScroll,
    scrollToBottom,
    sendMessage,
    stopStreaming,
    resendMessage,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
};
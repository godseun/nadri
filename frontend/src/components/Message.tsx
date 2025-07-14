import React from "react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { solarizedlight } from "react-syntax-highlighter/dist/esm/styles/prism";
import { Components } from "react-markdown";
import rehypeRaw from "rehype-raw";
import { useChat } from "../context/ChatContext";
import RetryIcon from "./icons/RetryIcon";

interface MessageProps {
  msg: { id: number; text: string[]; sender: string; error?: boolean };
}

const Message: React.FC<MessageProps> = ({ msg }) => {
  const { resendMessage } = useChat();

  const components: Components = {
    code({
      inline,
      className,
      children,
      ...props
    }: {
      inline?: boolean;
      className?: string;
      children?: React.ReactNode;
      [key: string]: any;
    }) {
      const match = /language-(\w+)/.exec(className || "");
      return !inline && match ? (
        <SyntaxHighlighter
          style={solarizedlight}
          language={match[1]}
          PreTag="div"
          {...props}
        >
          {String(children).replace(/\n$/, "")}
        </SyntaxHighlighter>
      ) : (
        <code className={className} {...props}>
          {children}
        </code>
      );
    },
  };

  return (
    <div className={`message ${msg.sender}`}>
      <div className="text">
        {msg.text.map((line, index) => (
          <ReactMarkdown
            key={`line-${index}`}
            components={components}
            rehypePlugins={[rehypeRaw]}
          >
            {line}
          </ReactMarkdown>
        ))}
      </div>
      {msg.sender === "user" && msg.error && (
        <div className="retry-container">
          <button onClick={() => resendMessage(msg.id)} className="retry-button">
            <RetryIcon />
          </button>
        </div>
      )}
    </div>
  );
};

export default Message;

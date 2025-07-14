import React, { useEffect } from "react";
import SendIcon from "./icons/SendIcon";
import StopIcon from "./icons/StopIcon";

interface MessageInputProps {
  input: string;
  setInput: (input: string) => void;
  sendMessage: (messageText: string) => Promise<void>;
  stopStreaming: () => void;
  inputRef: React.RefObject<HTMLTextAreaElement | null>;
  messagesLength: number;
  isTyping: boolean;
}

const MessageInput: React.FC<MessageInputProps> = ({
  input,
  setInput,
  sendMessage,
  stopStreaming,
  inputRef,
  messagesLength,
  isTyping,
}) => {
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = "auto";
      inputRef.current.style.height = `${inputRef.current.scrollHeight}px`;
    }
  }, [input]);

  return (
    <div
      className={`input-container ${messagesLength === 0 ? "centered-on-empty" : ""
        }`}
    >
      <textarea
        value={input}
        onChange={(e) => {
          setInput(e.target.value);
          e.target.style.height = "auto";
          if (e.target.scrollHeight > e.target.clientHeight) {
            e.target.style.height = e.target.scrollHeight + "px";
          }
        }}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            if (e.nativeEvent.isComposing) {
              return;
            }
            e.preventDefault();
            sendMessage(input);
          }
        }}
        placeholder={isTyping ? "응답을 기다리는 중..." : "무엇이든 물어보세요."}
        ref={inputRef}
        rows={1}
        disabled={isTyping}
      />
      {isTyping ? (
        <button onClick={stopStreaming} className="stop-button">
          <StopIcon />
        </button>
      ) : (
        input.trim().length > 0 && (
          <button onClick={() => sendMessage(input)} className="send-button">
            <SendIcon />
          </button>
        )
      )}
    </div>
  );
};

export default MessageInput;
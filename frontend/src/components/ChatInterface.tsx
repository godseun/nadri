import React from 'react';
import { useChat } from "../context/ChatContext";
import MessageInput from "./MessageInput";
import ScrollToBottomButton from "./ScrollToBottomButton";
import Message from "./Message";

const ChatInterface: React.FC = () => {
  const { messages, input, setInput, isTyping, messagesContainerRef, handleScroll, messagesEndRef, showScrollButton, scrollToBottom, sendMessage, stopStreaming, inputRef } = useChat();
  return (
    <>
      <div
        className={`chat-container ${
          messages.length === 0 ? 'empty-chat' : ''
        }`}
      >
        {messages.length > 0 && (
          <div
            className="messages"
            ref={messagesContainerRef}
            onScroll={handleScroll}
          >
            {messages.map((msg, index) => (
              <Message key={index} msg={msg} />
            ))}
            {isTyping && (
              <div className="message typing">
                <div className="text typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
        {showScrollButton && <ScrollToBottomButton scrollToBottom={scrollToBottom} />}
        <MessageInput
          input={input}
          setInput={setInput}
          sendMessage={sendMessage}
          stopStreaming={stopStreaming}
          inputRef={inputRef}
          messagesLength={messages.length}
          isTyping={isTyping}
        />
      </div>
    </>
  );
};

export default ChatInterface;
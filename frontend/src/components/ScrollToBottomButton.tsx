import React from 'react';
import ArrowDownIcon from './icons/ArrowDownIcon';

interface ScrollToBottomButtonProps {
  scrollToBottom: () => void;
}

const ScrollToBottomButton: React.FC<ScrollToBottomButtonProps> = ({ scrollToBottom }) => {
  return (
    <button onClick={scrollToBottom} className="scroll-to-bottom-button">
      <ArrowDownIcon />
    </button>
  );
};

export default ScrollToBottomButton;
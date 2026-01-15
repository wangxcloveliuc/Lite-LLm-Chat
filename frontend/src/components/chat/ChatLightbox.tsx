type ChatLightboxProps = {
  selectedImageUrl: string | null;
  onClose: () => void;
};

const ChatLightbox = ({ selectedImageUrl, onClose }: ChatLightboxProps) => {
  if (!selectedImageUrl) return null;

  return (
    <div className="lightbox-overlay" onClick={onClose}>
      <button className="lightbox-close" onClick={(e) => { e.stopPropagation(); onClose(); }}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M18 6L6 18M6 6l12 12" />
        </svg>
      </button>
      <div className="lightbox-content" onClick={(e) => e.stopPropagation()}>
        <img
          src={selectedImageUrl}
          alt="Full size"
          loading="lazy"
        />
      </div>
    </div>
  );
};

export default ChatLightbox;

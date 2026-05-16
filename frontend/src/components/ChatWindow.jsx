import { useEffect, useMemo, useRef, useState } from 'react';

export default function ChatWindow({ me, contact, messages, onSend, onDelete }) {
  const [text, setText] = useState('');
  const listRef = useRef(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  const grouped = useMemo(() => {
    const result = [];
    let lastDate = '';
    messages.forEach((m) => {
      const day = new Date(m.created_at).toDateString();
      if (day !== lastDate) {
        result.push({ type: 'separator', value: day });
        lastDate = day;
      }
      result.push({ type: 'message', value: m });
    });
    return result;
  }, [messages]);

  if (!contact) return <main className="chat-window empty glass">Select a chat to start messaging</main>;

  return (
    <main className="chat-window glass">
      <header>
        <h2>{contact.display_name}</h2>
        <span className="presence">online</span>
      </header>
      <section className="messages" ref={listRef}>
        {grouped.map((item, index) =>
          item.type === 'separator' ? (
            <div key={`sep-${index}`} className="date-separator">{item.value}</div>
          ) : (
            <article key={item.value.id} className={item.value.sender_user_id === me.userId ? 'bubble mine' : 'bubble'}>
              <p>{item.value.body}</p>
              <small>
                {new Date(item.value.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                {item.value.sender_user_id === me.userId ? (item.value.seen_at ? ' ✓✓' : ' ✓') : ''}
              </small>
              {item.value.sender_user_id === me.userId && <button onClick={() => onDelete(item.value.id)}>Delete</button>}
            </article>
          )
        )}
      </section>
      <footer>
        <button title="emoji">😊</button>
        <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Type a message" />
        <button title="attachment">📎</button>
        <button title="voice note">🎤</button>
        <button
          onClick={() => {
            if (text.trim()) onSend(text.trim());
            setText('');
          }}
        >
          Send
        </button>
      </footer>
    </main>
  );
}

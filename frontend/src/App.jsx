import { useEffect, useMemo, useState } from 'react';
import Login from './components/Login';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import ProfileModal from './components/ProfileModal';
import { api } from './services/api';
import { connectSocket } from './services/socket';

export default function App() {
  const [session, setSession] = useState(() => {
    const raw = localStorage.getItem('sync-session');
    return raw ? JSON.parse(raw) : null;
  });
  const [contacts, setContacts] = useState([]);
  const [active, setActive] = useState(null);
  const [messages, setMessages] = useState([]);
  const [search, setSearch] = useState('');
  const [dark, setDark] = useState(true);
  const [showProfile, setShowProfile] = useState(false);

  useEffect(() => {
    document.body.className = dark ? 'theme-dark' : 'theme-light';
  }, [dark]);

  useEffect(() => {
    if (!session) return;
    localStorage.setItem('sync-session', JSON.stringify(session));
  }, [session]);

  useEffect(() => {
    if (!session?.sessionToken) return;
    api('/api/contacts', {}, session.sessionToken).then(setContacts).catch(() => setSession(null));
    const socket = connectSocket(session.userId);
    socket.emit('presence:join', { userId: session.userId });
    socket.on('message:new', (msg) => {
      if (!active || [msg.sender_user_id, msg.receiver_user_id].includes(active.user_id)) setMessages((prev) => [...prev, msg]);
      new Audio('https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg').play().catch(() => {});
    });
    return () => socket.disconnect();
  }, [session, active]);

  useEffect(() => {
    if (!active || !session) return;
    api(`/api/messages/${active.user_id}`, {}, session.sessionToken).then(setMessages);
  }, [active, session]);

  const sortedContacts = useMemo(() => [...contacts], [contacts]);

  if (!session) return <div className="auth-page"><Login onLogin={setSession} /></div>;

  return (
    <div className="layout">
      <Sidebar contacts={sortedContacts} activeContactId={active?.user_id} onSelect={setActive} search={search} onSearch={setSearch} />
      <ChatWindow
        me={session}
        contact={active}
        messages={messages}
        onSend={async (body) => {
          if (!active) return;
          const msg = await api('/api/messages', {
            method: 'POST',
            body: JSON.stringify({ receiverUserId: active.user_id, body }),
          }, session.sessionToken);
          setMessages((prev) => [...prev, msg]);
        }}
        onDelete={async (id) => {
          await api(`/api/messages/${id}`, { method: 'DELETE' }, session.sessionToken);
          setMessages((prev) => prev.filter((m) => m.id !== id));
        }}
      />
      <aside className="controls glass">
        <button onClick={() => setDark((v) => !v)}>{dark ? 'Light Mode' : 'Dark Mode'}</button>
        <button onClick={() => setShowProfile(true)}>Profile</button>
        <button
          onClick={async () => {
            await api('/api/auth/logout', {
              method: 'POST',
              body: JSON.stringify({ sessionToken: session.sessionToken }),
            });
            localStorage.removeItem('sync-session');
            setSession(null);
          }}
        >
          Logout
        </button>
      </aside>
      {showProfile && (
        <ProfileModal
          me={session}
          onClose={() => setShowProfile(false)}
          onSave={async (payload) => {
            const me = await api('/api/profile', { method: 'PATCH', body: JSON.stringify(payload) }, session.sessionToken);
            setSession((prev) => ({ ...prev, ...me }));
            setShowProfile(false);
          }}
        />
      )}
    </div>
  );
}

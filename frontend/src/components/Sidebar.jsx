import { useMemo } from 'react';

export default function Sidebar({ contacts, activeContactId, onSelect, search, onSearch }) {
  const filtered = useMemo(
    () => contacts.filter((c) => `${c.display_name} ${c.phone}`.toLowerCase().includes(search.toLowerCase())),
    [contacts, search]
  );

  return (
    <aside className="sidebar glass">
      <input value={search} onChange={(e) => onSearch(e.target.value)} placeholder="Search contacts" />
      <div className="contacts-list">
        {filtered.map((c) => (
          <button key={c.id} className={activeContactId === c.user_id ? 'contact active' : 'contact'} onClick={() => onSelect(c)}>
            <span className="avatar">{(c.display_name || '?').slice(0, 1).toUpperCase()}</span>
            <span>
              <strong>{c.display_name}</strong>
              <small>{c.phone}</small>
            </span>
          </button>
        ))}
      </div>
    </aside>
  );
}

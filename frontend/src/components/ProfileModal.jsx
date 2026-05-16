export default function ProfileModal({ me, onClose, onSave }) {
  const submit = (event) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    onSave({
      displayName: form.get('displayName'),
      avatarUrl: form.get('avatarUrl'),
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <form className="modal glass" onClick={(e) => e.stopPropagation()} onSubmit={submit}>
        <h3>Profile</h3>
        <input name="displayName" defaultValue={me.display_name || ''} />
        <input name="avatarUrl" defaultValue={me.avatar_url || ''} placeholder="Avatar URL" />
        <button type="submit">Save</button>
      </form>
    </div>
  );
}

import { useState } from 'react';
import { api } from '../services/api';
import { requestOtp, setupRecaptcha } from '../services/firebase';

export default function Login({ onLogin }) {
  const [phone, setPhone] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [otp, setOtp] = useState('');
  const [confirmation, setConfirmation] = useState(null);

  const sendOtp = async () => {
    const verifier = setupRecaptcha('recaptcha-container');
    const result = await requestOtp(phone, verifier);
    setConfirmation(result);
  };

  const verifyOtp = async () => {
    const credential = await confirmation.confirm(otp);
    const data = await api('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        phone,
        firebaseUid: credential.user.uid,
        displayName,
      }),
    });
    onLogin({ ...data, phone, displayName });
  };

  return (
    <div className="login-card glass">
      <h1>Sync Chat</h1>
      <p>Premium real-time messaging</p>
      <input placeholder="+91XXXXXXXXXX" value={phone} onChange={(e) => setPhone(e.target.value)} />
      <input placeholder="Display name" value={displayName} onChange={(e) => setDisplayName(e.target.value)} />
      {!confirmation ? (
        <button onClick={sendOtp}>Send OTP</button>
      ) : (
        <>
          <input placeholder="Enter OTP" value={otp} onChange={(e) => setOtp(e.target.value)} />
          <button onClick={verifyOtp}>Verify & Login</button>
        </>
      )}
      <div id="recaptcha-container" />
    </div>
  );
}

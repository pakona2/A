import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Phone, Video, Search, MoreHorizontal, Grid3X3, Clock3, Users, Settings, Bell, Plus, ArrowUpRight, ArrowDownLeft, X, Delete, Mic, Volume2 } from 'lucide-react';
import './styles.css';

const demoContacts = [
  { name: 'Maya Chen', handle: '@maya.chen', initials: 'MC', color: 'coral', status: 'On a call' },
  { name: 'Jordan Bell', handle: '@jordan.b', initials: 'JB', color: 'mint', status: 'Available' },
  { name: 'Samira Okafor', handle: '@samira.o', initials: 'SO', color: 'violet', status: 'Available' },
  { name: 'Leo Park', handle: '@leo.park', initials: 'LP', color: 'gold', status: 'Away' },
];
const demoRecent = [
  { name: 'Maya Chen', time: 'Today, 10:42 AM', type: 'outgoing', duration: '14 min', initials: 'MC', color: 'coral' },
  { name: 'Jordan Bell', time: 'Yesterday, 6:18 PM', type: 'incoming', duration: '8 min', initials: 'JB', color: 'mint' },
  { name: 'Samira Okafor', time: 'Yesterday, 2:05 PM', type: 'missed', duration: 'No answer', initials: 'SO', color: 'violet' },
];
const keys = [['1', ''], ['2', 'ABC'], ['3', 'DEF'], ['4', 'GHI'], ['5', 'JKL'], ['6', 'MNO'], ['7', 'PQRS'], ['8', 'TUV'], ['9', 'WXYZ'], ['*', ''], ['0', '+'], ['#', '']];
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

function Avatar({ person, size = '' }) { return <div className={`avatar ${person.color} ${size}`}>{person.initials}</div>; }
function App() {
  const [activeTab, setActiveTab] = useState('Home');
  const [query, setQuery] = useState('');
  const [dialOpen, setDialOpen] = useState(false);
  const [number, setNumber] = useState('');
  const [calling, setCalling] = useState(null);
  const [contacts, setContacts] = useState(demoContacts);
  const [recent, setRecent] = useState(demoRecent);
  useEffect(() => {
    Promise.all([fetch(`${API_BASE}/contacts`), fetch(`${API_BASE}/calls`)]).then(async ([contactsResponse, callsResponse]) => {
      if (!contactsResponse.ok || !callsResponse.ok) return;
      const contactsData = await contactsResponse.json();
      const callsData = await callsResponse.json();
      setContacts(contactsData.contacts);
      setRecent(callsData.calls.map((call) => ({ ...call, time: new Date(call.created_at).toLocaleString(), initials: (call.name || '??').slice(0, 2).toUpperCase(), color: 'mint' })));
    }).catch(() => {});
  }, []);
  const shownContacts = contacts.filter((person) => person.name.toLowerCase().includes(query.toLowerCase()));
  const startCall = async (person) => {
    setCalling(person);
    fetch(`${API_BASE}/calls`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: person.name, phone_number: person.handle || person.name }) }).catch(() => {});
  };
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark"><Phone size={19} strokeWidth={2.8} /></span><span>CallMe</span></div>
      <nav>{[['Home', Phone], ['Recents', Clock3], ['Contacts', Users]].map(([label, Icon]) => <button className={activeTab === label ? 'nav-item active' : 'nav-item'} onClick={() => setActiveTab(label)} key={label}><Icon size={18} />{label}</button>)}</nav>
      <div className="sidebar-bottom"><button className="nav-item"><Settings size={18} />Settings</button><div className="profile"><div className="avatar profile-avatar">AR</div><div><strong>Alex Rivera</strong><span>Personal account</span></div><MoreHorizontal size={18} /></div></div>
    </aside>
    <main>
      <header className="topbar"><div className="mobile-brand"><span className="brand-mark"><Phone size={17} /></span>CallMe</div><div className="search"><Search size={17} /><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search people or numbers" /></div><button className="icon-btn notification"><Bell size={19} /><i /></button><div className="avatar profile-avatar">AR</div></header>
      {activeTab === 'Home' && <div className="content"><section className="hero"><div><span className="eyebrow">THURSDAY, AUGUST 20</span><h1>Make room<br /><em>for connection.</em></h1><p>Reach the people who matter, wherever they are.</p><button className="primary-action" onClick={() => setDialOpen(true)}><Plus size={18} />Start a new call</button></div><div className="hero-art"><div className="art-ring ring-one" /><div className="art-ring ring-two" /><div className="art-phone"><Phone size={58} /></div><span className="art-label">your people<br /><b>are close</b></span></div></section>
        <section className="section"><div className="section-heading"><div><span className="eyebrow">QUICK CONNECT</span><h2>People</h2></div><button className="text-btn" onClick={() => setActiveTab('Contacts')}>View all <ArrowUpRight size={15} /></button></div><div className="people-grid">{shownContacts.map((person) => <article className="person-card" key={person.name}><div className="person-top"><Avatar person={person} /><button className="more"><MoreHorizontal size={17} /></button></div><h3>{person.name}</h3><p>{person.handle}</p><div className="person-footer"><span className={`status ${person.status === 'On a call' ? 'busy' : ''}`}><i />{person.status}</span><button className="call-circle" onClick={() => startCall(person)}><Phone size={16} fill="currentColor" /></button></div></article>)}</div></section>
        <section className="section recent-section"><div className="section-heading"><div><span className="eyebrow">YOUR ACTIVITY</span><h2>Recent calls</h2></div><button className="text-btn" onClick={() => setActiveTab('Recents')}>See history <ArrowUpRight size={15} /></button></div><div className="recent-list">{recent.map((item) => <div className="recent-row" key={item.name}><Avatar person={item} /><div className="recent-name"><strong>{item.name}</strong><span>{item.time}</span></div><span className={`call-type ${item.type}`}><span>{item.type === 'outgoing' ? <ArrowUpRight size={14} /> : item.type === 'incoming' ? <ArrowDownLeft size={14} /> : <X size={14} />}</span>{item.type === 'missed' ? 'Missed' : item.type}</span><span className="duration">{item.duration}</span><button className="quick-call" onClick={() => startCall(item)}><Phone size={16} /></button></div>)}</div></section>
      </div>}
      {activeTab !== 'Home' && <div className="content simple-view"><span className="eyebrow">CALLME</span><h1>{activeTab}</h1><p className="view-copy">Your {activeTab.toLowerCase()} will appear here as you connect with your people.</p><button className="primary-action" onClick={() => setDialOpen(true)}><Plus size={18} />Start a new call</button></div>}
    </main>
    <nav className="bottom-nav">{[['Home', Phone], ['Recents', Clock3], ['Contacts', Users]].map(([label, Icon]) => <button className={activeTab === label ? 'active' : ''} onClick={() => setActiveTab(label)} key={label}><Icon size={20} />{label}</button>)}</nav>
    {dialOpen && <div className="modal-backdrop" onClick={() => setDialOpen(false)}><div className="dialer" onClick={(e) => e.stopPropagation()}><div className="dialer-head"><div><span className="eyebrow">NEW CALL</span><h2>Who are you calling?</h2></div><button className="close-btn" onClick={() => setDialOpen(false)}><X size={20} /></button></div><div className="number-display">{number || <span>Enter a number</span>}</div><div className="keypad">{keys.map(([key, letters]) => <button key={key} onClick={() => setNumber((current) => current + key)}><strong>{key}</strong><small>{letters}</small></button>)}</div><div className="dialer-actions"><button className="delete-btn" onClick={() => setNumber((current) => current.slice(0, -1))}><Delete size={19} /></button><button className="dial-btn" onClick={async () => { if (!number) return; await fetch(`${API_BASE}/calls`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ phone_number: number }) }).catch(() => {}); setCalling({ name: number, initials: '??', color: 'mint' }); setDialOpen(false); }}><Phone size={22} fill="currentColor" /></button><span /></div></div></div>}
    {calling && <div className="modal-backdrop"><div className="call-modal"><div className="call-avatar"><Avatar person={calling} size="large" /></div><span className="eyebrow">CALLING</span><h2>{calling.name}</h2><p>Connecting securely...</p><div className="call-controls"><button><Mic size={20} /></button><button><Volume2 size={20} /></button><button className="end-call" onClick={() => setCalling(null)}><Phone size={20} fill="currentColor" /></button></div></div></div>}
  </div>;
}
createRoot(document.getElementById('root')).render(<App />);

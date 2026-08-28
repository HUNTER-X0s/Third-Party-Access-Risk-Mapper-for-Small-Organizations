import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Users, UserPlus, Shield, X, Check, Lock, AlertCircle } from 'lucide-react';

interface UserManagementModalProps {
  onClose: () => void;
}

export const UserManagementModal: React.FC<UserManagementModalProps> = ({ onClose }) => {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // New user form state
  const [newEmail, setNewEmail] = useState('');
  const [newName, setNewName] = useState('');
  const [newRole, setNewRole] = useState('VIEWER');
  const [showAddForm, setShowAddForm] = useState(false);

  const loadUsers = () => {
    setLoading(true);
    api.getUsers()
      .then(data => {
        setUsers(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createUser(newEmail, newName, newRole);
      setNewEmail('');
      setNewName('');
      setShowAddForm(false);
      loadUsers();
    } catch (err: any) {
      alert('Failed to create user: ' + err.message);
    }
  };

  const handleRoleChange = async (userId: string, role: string) => {
    try {
      await api.updateUserRole(userId, role);
      loadUsers();
    } catch (err: any) {
      alert('Failed to update role: ' + err.message);
    }
  };

  const handleStatusToggle = async (userId: string, currentStatus: string) => {
    const nextStatus = currentStatus === 'ACTIVE' ? 'SUSPENDED' : 'ACTIVE';
    try {
      await api.updateUserStatus(userId, nextStatus);
      loadUsers();
    } catch (err: any) {
      alert('Failed to update status: ' + err.message);
    }
  };

  const rolesList = ['SUPER_ADMIN', 'SECURITY_ADMIN', 'IT_ADMIN', 'AUDITOR', 'APP_OWNER', 'DATA_OWNER', 'VIEWER'];

  return (
    <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-50 flex items-center justify-center p-4">
      <div className="bg-white border border-slate-200 rounded-xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden text-slate-800 font-sans shadow-2xl">
        {/* Header */}
        <div className="p-5 border-b border-slate-200 flex items-center justify-between bg-slate-50/70">
          <div className="flex items-center space-x-2">
            <Users className="w-5 h-5 text-blue-600" />
            <h2 className="font-bold text-sm text-slate-900">User & RBAC Access Management</h2>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-md text-xs font-medium flex items-center space-x-1.5 transition-colors shadow-xs cursor-pointer"
            >
              <UserPlus className="w-3.5 h-3.5" />
              <span>{showAddForm ? 'Cancel' : 'Invite User'}</span>
            </button>
            <button onClick={onClose} className="p-1.5 hover:bg-slate-200/60 rounded-md text-slate-400 hover:text-slate-600 cursor-pointer">
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-4 text-xs font-sans">
          {error && (
            <div className="bg-red-50 border border-red-200 p-3 rounded-lg text-red-700 flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-red-600" />
              <span>{error}</span>
            </div>
          )}

          {/* Add User Form */}
          {showAddForm && (
            <form onSubmit={handleCreateUser} className="bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-3">
              <div className="font-bold text-slate-900 text-xs uppercase tracking-wider">Invite New Team Member</div>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="text-slate-600 text-[11px] font-medium block mb-1">Email</label>
                  <input
                    type="email"
                    value={newEmail}
                    onChange={(e) => setNewEmail(e.target.value)}
                    required
                    placeholder="user@anurag.tech"
                    className="w-full bg-white border border-slate-300 rounded-md px-3 py-1.5 text-xs text-slate-900 focus:outline-none focus:border-blue-600"
                  />
                </div>
                <div>
                  <label className="text-slate-600 text-[11px] font-medium block mb-1">Full Name</label>
                  <input
                    type="text"
                    value={newName}
                    onChange={(e) => setNewName(e.target.value)}
                    required
                    placeholder="Jane Doe"
                    className="w-full bg-white border border-slate-300 rounded-md px-3 py-1.5 text-xs text-slate-900 focus:outline-none focus:border-blue-600"
                  />
                </div>
                <div>
                  <label className="text-slate-600 text-[11px] font-medium block mb-1">Role</label>
                  <select
                    value={newRole}
                    onChange={(e) => setNewRole(e.target.value)}
                    className="w-full bg-white border border-slate-300 rounded-md px-3 py-1.5 text-xs text-slate-900 focus:outline-none focus:border-blue-600 cursor-pointer"
                  >
                    {rolesList.map(r => (
                      <option key={r} value={r}>{r}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="flex justify-end pt-2">
                <button
                  type="submit"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-1.5 rounded-md text-xs font-medium transition-colors shadow-xs cursor-pointer"
                >
                  Confirm & Send Invitation
                </button>
              </div>
            </form>
          )}

          {/* User Table */}
          <div className="border border-slate-200 rounded-lg overflow-hidden overflow-x-auto">
            <table className="ag-table">
              <thead>
                <tr>
                  <th>User / Email</th>
                  <th>Role Assignment</th>
                  <th>Status</th>
                  <th>Last Active</th>
                  <th className="text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan={5} className="p-8 text-center text-slate-400 text-xs">Loading users...</td></tr>
                ) : users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-50/80 transition-colors">
                    <td>
                      <div className="font-semibold text-slate-900">{u.display_name}</div>
                      <div className="text-slate-500 text-[11px] font-mono">{u.email}</div>
                    </td>
                    <td>
                      <select
                        value={u.role}
                        onChange={(e) => handleRoleChange(u.id, e.target.value)}
                        className="bg-white border border-slate-200 text-slate-700 rounded-md px-2.5 py-1 text-xs focus:outline-none focus:border-blue-500 shadow-xs cursor-pointer"
                      >
                        {rolesList.map(r => (
                          <option key={r} value={r}>{r}</option>
                        ))}
                      </select>
                    </td>
                    <td>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-medium border ${u.status === 'ACTIVE' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-red-50 text-red-700 border-red-200'}`}>
                        {u.status}
                      </span>
                    </td>
                    <td className="text-slate-500 font-mono text-[11px]">{u.last_login_at ? new Date(u.last_login_at).toLocaleDateString() : 'Never'}</td>
                    <td className="text-right">
                      <button
                        onClick={() => handleStatusToggle(u.id, u.status)}
                        className="text-xs text-slate-600 hover:text-slate-900 underline font-medium cursor-pointer"
                      >
                        {u.status === 'ACTIVE' ? 'Suspend' : 'Activate'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

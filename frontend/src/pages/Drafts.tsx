import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Save, Send, Edit, Trash2, Plus } from 'lucide-react';

interface Draft {
  id: number;
  platform: string;
  content: string;
  status: string;
  created_at: string;
  updated_at?: string;
}

const Drafts: React.FC = () => {
  const { user } = useAuth();
  const token = localStorage.getItem('token');
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingDraft, setEditingDraft] = useState<Draft | null>(null);
  const [formData, setFormData] = useState({
    platform: 'linkedin',
    content: ''
  });

  useEffect(() => {
    fetchDrafts();
  }, []);

  const fetchDrafts = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/content/drafts', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch drafts');
      }

      const data = await response.json();
      setDrafts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDraft = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/content/drafts', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        throw new Error('Failed to create draft');
      }

      await fetchDrafts();
      setFormData({ platform: 'linkedin', content: '' });
      setShowCreateForm(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const handleUpdateDraft = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingDraft) return;

    try {
      const response = await fetch(`http://localhost:8000/content/drafts/${editingDraft.id}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        throw new Error('Failed to update draft');
      }

      await fetchDrafts();
      setEditingDraft(null);
      setFormData({ platform: 'linkedin', content: '' });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const handleDeleteDraft = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this draft?')) return;

    try {
      const response = await fetch(`http://localhost:8000/content/drafts/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to delete draft');
      }

      await fetchDrafts();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const handlePostDraft = async (id: number, platform: string) => {
    if (!window.confirm(`Are you sure you want to post this to ${platform}?`)) return;

    try {
      const response = await fetch(`http://localhost:8000/content/drafts/${id}/post`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to post draft');
      }

      const result = await response.json();
      alert(result.message);
      await fetchDrafts();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const startEditing = (draft: Draft) => {
    setEditingDraft(draft);
    setFormData({
      platform: draft.platform,
      content: draft.content
    });
  };

  const cancelEditing = () => {
    setEditingDraft(null);
    setFormData({ platform: 'linkedin', content: '' });
  };

  const getPlatformColor = (platform: string) => {
    const colors = {
      linkedin: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      twitter: 'bg-sky-100 text-sky-800 dark:bg-sky-900 dark:text-sky-200',
      facebook: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
      instagram: 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200',
      email: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
    };
    return colors[platform as keyof typeof colors] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Drafts</h1>
        <button
          onClick={() => setShowCreateForm(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          New Draft
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4 dark:bg-red-900 dark:border-red-600 dark:text-red-200">
          {error}
        </div>
      )}

      {/* Create/Edit Form */}
      {(showCreateForm || editingDraft) && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
            {editingDraft ? 'Edit Draft' : 'Create New Draft'}
          </h2>
          <form onSubmit={editingDraft ? handleUpdateDraft : handleCreateDraft}>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Platform
              </label>
              <select
                value={formData.platform}
                onChange={(e) => setFormData({ ...formData, platform: e.target.value })}
                className="input-field"
                required
              >
                <option value="linkedin">LinkedIn</option>
                <option value="twitter">Twitter</option>
                <option value="facebook">Facebook</option>
                <option value="instagram">Instagram</option>
                <option value="email">Email</option>
              </select>
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Content
              </label>
              <textarea
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                className="input-field min-h-[120px]"
                placeholder="Write your content here..."
                required
              />
            </div>
            <div className="flex gap-2">
              <button type="submit" className="btn-primary">
                {editingDraft ? 'Update Draft' : 'Save as Draft'}
              </button>
              <button
                type="button"
                onClick={editingDraft ? cancelEditing : () => setShowCreateForm(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Drafts List */}
      {drafts.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-500 dark:text-gray-400 mb-4">
            <Save className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <h3 className="text-lg font-medium">No drafts yet</h3>
            <p>Create your first draft to get started!</p>
          </div>
        </div>
      ) : (
        <div className="grid gap-4">
          {drafts.map((draft) => (
            <div key={draft.id} className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getPlatformColor(draft.platform)}`}>
                    {draft.platform.charAt(0).toUpperCase() + draft.platform.slice(1)}
                  </span>
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    {new Date(draft.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => startEditing(draft)}
                    className="p-2 text-gray-500 hover:text-blue-600 dark:text-gray-400 dark:hover:text-blue-400"
                    title="Edit"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteDraft(draft.id)}
                    className="p-2 text-gray-500 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400"
                    title="Delete"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              
              <div className="mb-4">
                <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                  {draft.content}
                </p>
              </div>
              
              <div className="flex gap-2">
                <button
                  onClick={() => handlePostDraft(draft.id, draft.platform)}
                  className="btn-primary flex items-center gap-2"
                >
                  <Send className="w-4 h-4" />
                  Post to {draft.platform.charAt(0).toUpperCase() + draft.platform.slice(1)}
                </button>
                <button
                  onClick={() => startEditing(draft)}
                  className="btn-secondary flex items-center gap-2"
                >
                  <Edit className="w-4 h-4" />
                  Edit
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Drafts;

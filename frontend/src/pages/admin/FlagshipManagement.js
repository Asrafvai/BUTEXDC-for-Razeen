import React, { useEffect, useState } from 'react';
import { getFlagshipEvents, createFlagshipEvent, updateFlagshipEvent, archiveFlagshipEvent, toggleFlagshipEvent, createFlagshipAnnouncement, getFlagshipAnnouncements, updateFlagshipAnnouncement, archiveFlagshipAnnouncement } from '../../lib/api';
import { Button } from '../../components/ui/button';
import { Card, CardContent } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Textarea } from '../../components/ui/textarea';
import { Label } from '../../components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../../components/ui/dialog';
import { toast } from 'sonner';
import { Plus, Edit, Archive, Star, Bell, ChevronDown, ChevronUp, ExternalLink, FileText, Power } from 'lucide-react';

const FlagshipManagement = () => {
  const [events, setEvents] = useState([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingEvent, setEditingEvent] = useState(null);
  const [formData, setFormData] = useState({ title: '', photo_url: '', details: '', event_link: '', preregister_link: '' });

  // Announcement state
  const [annDialogOpen, setAnnDialogOpen] = useState(false);
  const [annParentId, setAnnParentId] = useState(null);
  const [editingAnn, setEditingAnn] = useState(null);
  const [annForm, setAnnForm] = useState({ title: '', photo_url: '', details: '' });
  const [expandedEvent, setExpandedEvent] = useState(null);
  const [announcements, setAnnouncements] = useState({});

  useEffect(() => { loadEvents(); }, []);

  const loadEvents = async () => {
    try {
      const res = await getFlagshipEvents();
      setEvents(res.data);
    } catch (err) { console.error(err); }
  };

  const loadAnnouncements = async (eventId) => {
    try {
      const res = await getFlagshipAnnouncements(eventId);
      setAnnouncements(prev => ({ ...prev, [eventId]: res.data }));
    } catch (err) { console.error(err); }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingEvent) {
        await updateFlagshipEvent(editingEvent.id, formData);
        toast.success('Flagship event updated');
      } else {
        await createFlagshipEvent(formData);
        toast.success('Flagship event created');
      }
      setDialogOpen(false);
      setEditingEvent(null);
      setFormData({ title: '', photo_url: '', details: '', event_link: '', preregister_link: '' });
      loadEvents();
    } catch (err) { toast.error('Failed to save'); }
  };

  const handleEdit = (evt) => {
    setEditingEvent(evt);
    setFormData({ title: evt.title, photo_url: evt.photo_url || '', details: evt.details, event_link: evt.event_link || '', preregister_link: evt.preregister_link || '' });
    setDialogOpen(true);
  };

  const handleArchive = async (id) => {
    try { await archiveFlagshipEvent(id); toast.success('Archived'); loadEvents(); }
    catch { toast.error('Failed'); }
  };

  const handleToggle = async (id, currentActive) => {
    try {
      await toggleFlagshipEvent(id);
      toast.success(currentActive ? 'Event hidden from homepage' : 'Event visible on homepage');
      loadEvents();
    } catch { toast.error('Failed to toggle'); }
  };

  const toggleExpand = async (eventId) => {
    if (expandedEvent === eventId) { setExpandedEvent(null); return; }
    setExpandedEvent(eventId);
    if (!announcements[eventId]) await loadAnnouncements(eventId);
  };

  const handleAnnSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingAnn) {
        await updateFlagshipAnnouncement(editingAnn.id, annForm);
        toast.success('Announcement updated');
      } else {
        await createFlagshipAnnouncement(annParentId, annForm);
        toast.success('Announcement created');
      }
      setAnnDialogOpen(false);
      setEditingAnn(null);
      setAnnForm({ title: '', photo_url: '', details: '' });
      loadAnnouncements(annParentId);
    } catch { toast.error('Failed to save announcement'); }
  };

  const handleAnnArchive = async (annId, parentId) => {
    try { await archiveFlagshipAnnouncement(annId); toast.success('Archived'); loadAnnouncements(parentId); }
    catch { toast.error('Failed'); }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-bold" data-testid="flagship-management-title">Flagship Events</h1>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-[#FF7F00] text-black hover:bg-[#E67300]" onClick={() => { setEditingEvent(null); setFormData({ title: '', photo_url: '', details: '', event_link: '', preregister_link: '' }); }} data-testid="add-flagship-btn">
              <Plus className="mr-2 h-4 w-4" /> Add Flagship Event
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-[#1A1A1A] border-[#333333] max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="text-[#F0F0F0]">{editingEvent ? 'Edit' : 'Add'} Flagship Event</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label className="text-[#F0F0F0]">Event Title</Label>
                <Input value={formData.title} onChange={e => setFormData({ ...formData, title: e.target.value })} required className="bg-[#252525] border-[#333333] text-white" data-testid="flagship-title-input" />
              </div>
              <div>
                <Label className="text-[#F0F0F0]">Event Photo URL</Label>
                <Input value={formData.photo_url} onChange={e => setFormData({ ...formData, photo_url: e.target.value })} placeholder="https://i.ibb.co/..." className="bg-[#252525] border-[#333333] text-white" data-testid="flagship-photo-input" />
              </div>
              <div>
                <Label className="text-[#F0F0F0]">Details</Label>
                <Textarea value={formData.details} onChange={e => setFormData({ ...formData, details: e.target.value })} required className="bg-[#252525] border-[#333333] text-white" rows={4} data-testid="flagship-details-input" />
              </div>
              <div>
                <Label className="text-[#F0F0F0]">Event Link (optional)</Label>
                <Input value={formData.event_link} onChange={e => setFormData({ ...formData, event_link: e.target.value })} placeholder="https://..." className="bg-[#252525] border-[#333333] text-white" data-testid="flagship-eventlink-input" />
              </div>
              <div>
                <Label className="text-[#F0F0F0]">Pre-register Google Form Link (optional)</Label>
                <Input value={formData.preregister_link} onChange={e => setFormData({ ...formData, preregister_link: e.target.value })} placeholder="https://docs.google.com/forms/..." className="bg-[#252525] border-[#333333] text-white" data-testid="flagship-preregister-input" />
                <p className="text-xs text-gray-500 mt-1">Paste the Google Form embed URL (the src from iframe)</p>
              </div>
              <Button type="submit" className="w-full bg-[#FF7F00] text-black hover:bg-[#E67300]" data-testid="flagship-save-btn">Save</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Announcement dialog */}
      <Dialog open={annDialogOpen} onOpenChange={setAnnDialogOpen}>
        <DialogContent className="bg-[#1A1A1A] border-[#333333] max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-[#F0F0F0]">{editingAnn ? 'Edit' : 'Add'} Event Announcement</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleAnnSubmit} className="space-y-4">
            <div>
              <Label className="text-[#F0F0F0]">Title</Label>
              <Input value={annForm.title} onChange={e => setAnnForm({ ...annForm, title: e.target.value })} required className="bg-[#252525] border-[#333333] text-white" data-testid="ann-title-input" />
            </div>
            <div>
              <Label className="text-[#F0F0F0]">Photo URL (optional)</Label>
              <Input value={annForm.photo_url} onChange={e => setAnnForm({ ...annForm, photo_url: e.target.value })} placeholder="https://i.ibb.co/..." className="bg-[#252525] border-[#333333] text-white" data-testid="ann-photo-input" />
            </div>
            <div>
              <Label className="text-[#F0F0F0]">Details</Label>
              <Textarea value={annForm.details} onChange={e => setAnnForm({ ...annForm, details: e.target.value })} required className="bg-[#252525] border-[#333333] text-white" rows={4} data-testid="ann-details-input" />
            </div>
            <Button type="submit" className="w-full bg-[#FF7F00] text-black hover:bg-[#E67300]" data-testid="ann-save-btn">Save Announcement</Button>
          </form>
        </DialogContent>
      </Dialog>

      <div className="space-y-6">
        {events.map(evt => (
          <Card key={evt.id} className={`bg-[#000000] border-[#333333] ${!evt.active ? 'opacity-60' : ''}`} data-testid={`flagship-${evt.id}`}>
            <CardContent className="p-6">
              <div className="flex items-start gap-4">
                {evt.photo_url && <img src={evt.photo_url} alt={evt.title} className="w-20 h-20 rounded-lg object-cover flex-shrink-0" />}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <Star className="h-4 w-4 text-[#FF7F00]" />
                    <h3 className="text-xl font-semibold text-white">{evt.title}</h3>
                    {!evt.active && <span className="text-xs bg-gray-700 text-gray-300 px-2 py-0.5 rounded">Hidden</span>}
                  </div>
                  <p className="text-gray-400 text-sm line-clamp-2 mb-2">{evt.details}</p>
                  <div className="flex flex-wrap gap-2 text-xs">
                    {evt.event_link && <span className="text-green-400 flex items-center gap-1"><ExternalLink className="h-3 w-3" /> Event link set</span>}
                    {evt.preregister_link && <span className="text-green-400 flex items-center gap-1"><FileText className="h-3 w-3" /> Pre-register set</span>}
                  </div>
                </div>
                <div className="flex gap-2 flex-shrink-0">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleToggle(evt.id, evt.active)}
                    className={evt.active ? 'border-green-500 text-green-500 hover:bg-green-500/10' : 'border-gray-600 text-gray-400 hover:bg-gray-600/10'}
                    data-testid={`toggle-${evt.id}`}
                  >
                    <Power className="h-4 w-4 mr-1" /> {evt.active ? 'On' : 'Off'}
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => { setAnnParentId(evt.id); setEditingAnn(null); setAnnForm({ title: '', photo_url: '', details: '' }); setAnnDialogOpen(true); }} data-testid={`add-ann-${evt.id}`}>
                    <Bell className="h-4 w-4 mr-1" /> Add Update
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => handleEdit(evt)}><Edit className="h-4 w-4" /></Button>
                  <Button size="sm" variant="outline" className="border-red-600 text-red-600" onClick={() => handleArchive(evt.id)}><Archive className="h-4 w-4" /></Button>
                </div>
              </div>

              {/* Expandable announcements */}
              <button onClick={() => toggleExpand(evt.id)} className="mt-4 flex items-center gap-1 text-sm text-gray-400 hover:text-[#FF7F00] transition-colors" data-testid={`toggle-ann-${evt.id}`}>
                {expandedEvent === evt.id ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                Event Announcements ({announcements[evt.id]?.length || 0})
              </button>

              {expandedEvent === evt.id && (
                <div className="mt-3 ml-4 border-l-2 border-[#333] pl-4 space-y-3">
                  {(announcements[evt.id] || []).map(ann => (
                    <div key={ann.id} className="bg-[#111] rounded-lg p-3 flex items-start gap-3" data-testid={`ann-${ann.id}`}>
                      {ann.photo_url && <img src={ann.photo_url} alt="" className="w-12 h-12 rounded object-cover flex-shrink-0" />}
                      <div className="flex-1 min-w-0">
                        <h4 className="text-sm font-medium text-white">{ann.title}</h4>
                        <p className="text-xs text-gray-500 line-clamp-2">{ann.details}</p>
                      </div>
                      <div className="flex gap-1 flex-shrink-0">
                        <Button size="sm" variant="ghost" className="h-7 w-7 p-0" onClick={() => { setAnnParentId(evt.id); setEditingAnn(ann); setAnnForm({ title: ann.title, photo_url: ann.photo_url || '', details: ann.details }); setAnnDialogOpen(true); }}><Edit className="h-3 w-3" /></Button>
                        <Button size="sm" variant="ghost" className="h-7 w-7 p-0 text-red-600" onClick={() => handleAnnArchive(ann.id, evt.id)}><Archive className="h-3 w-3" /></Button>
                      </div>
                    </div>
                  ))}
                  {(announcements[evt.id] || []).length === 0 && <p className="text-xs text-gray-600">No announcements yet</p>}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
        {events.length === 0 && <p className="text-gray-500 text-center py-8">No flagship events yet</p>}
      </div>
    </div>
  );
};

export default FlagshipManagement;

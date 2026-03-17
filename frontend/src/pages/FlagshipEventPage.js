import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getFlagshipEvent } from '../lib/api';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { ArrowLeft, Star, ExternalLink, Bell, Calendar } from 'lucide-react';

const FlagshipEventPage = () => {
  const { eventId } = useParams();
  const [event, setEvent] = useState(null);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => { loadEvent(); }, [eventId]);

  const loadEvent = async () => {
    try {
      const res = await getFlagshipEvent(eventId);
      setEvent(res.data);
    } catch (err) { console.error(err); }
  };

  if (!event) {
    return <div className="min-h-screen bg-[#1A1A1A] flex items-center justify-center"><div className="text-[#FF7F00]">Loading...</div></div>;
  }

  return (
    <div className="min-h-screen bg-[#1A1A1A]">
      <div className="max-w-5xl mx-auto px-6 py-10">
        <Link to="/">
          <Button variant="ghost" className="mb-6 text-gray-400 hover:text-[#FF7F00]" data-testid="back-home-button">
            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Home
          </Button>
        </Link>

        {/* Hero image */}
        {event.photo_url && (
          <div className="w-full aspect-[21/9] rounded-xl overflow-hidden mb-8" data-testid="flagship-hero-image">
            <img src={event.photo_url} alt={event.title} className="w-full h-full object-cover" />
          </div>
        )}

        <div className="mb-8">
          <div className="flex items-center gap-3 mb-3">
            <Star className="h-6 w-6 text-[#FF7F00]" />
            <h1 className="text-4xl md:text-5xl font-bold text-white" data-testid="flagship-title">{event.title}</h1>
          </div>
          <p className="text-gray-300 text-lg leading-relaxed whitespace-pre-line" data-testid="flagship-details">{event.details}</p>
        </div>

        {/* Action buttons */}
        <div className="flex flex-wrap gap-4 mb-12">
          {event.event_link && (
            <a href={event.event_link} target="_blank" rel="noopener noreferrer" data-testid="event-link-btn">
              <Button className="bg-[#FF7F00] text-black hover:bg-[#E67300] px-6 py-5 text-base gap-2">
                <ExternalLink className="h-5 w-5" /> Event Link
              </Button>
            </a>
          )}
          {event.preregister_link && (
            <Button
              onClick={() => setShowForm(!showForm)}
              variant={showForm ? 'outline' : 'default'}
              className={showForm ? 'border-[#FF7F00] text-[#FF7F00] px-6 py-5 text-base gap-2' : 'bg-green-600 text-white hover:bg-green-700 px-6 py-5 text-base gap-2'}
              data-testid="preregister-btn"
            >
              <Calendar className="h-5 w-5" /> {showForm ? 'Hide Form' : 'Pre-register Now'}
            </Button>
          )}
        </div>

        {/* Embedded Google Form */}
        {showForm && event.preregister_link && (
          <div className="mb-12 bg-white rounded-xl overflow-hidden" data-testid="google-form-embed">
            <iframe
              src={event.preregister_link}
              width="100%"
              height="2943"
              frameBorder="0"
              marginHeight="0"
              marginWidth="0"
              title="Pre-registration Form"
              className="w-full"
            >
              Loading...
            </iframe>
          </div>
        )}

        {/* Announcements */}
        {event.announcements && event.announcements.length > 0 && (
          <div data-testid="flagship-announcements">
            <h2 className="text-3xl font-bold text-white mb-6 flex items-center gap-3">
              <Bell className="h-6 w-6 text-[#FF7F00]" /> Event Updates
            </h2>
            <div className="space-y-5">
              {event.announcements.map(ann => (
                <Card key={ann.id} className="bg-[#000] border-[#333] hover:border-[#FF7F00]/30 transition-all" data-testid={`flagship-ann-${ann.id}`}>
                  <CardContent className="p-6">
                    <div className="flex gap-5">
                      {ann.photo_url && (
                        <img src={ann.photo_url} alt={ann.title} className="w-24 h-24 md:w-32 md:h-32 rounded-lg object-cover flex-shrink-0" />
                      )}
                      <div className="flex-1">
                        <h3 className="text-xl font-semibold text-white mb-2">{ann.title}</h3>
                        <p className="text-gray-400 leading-relaxed whitespace-pre-line">{ann.details}</p>
                        <p className="text-xs text-gray-600 mt-3">{new Date(ann.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FlagshipEventPage;

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getCourseModules, getUserProgress, updateProgress } from '../lib/api';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Checkbox } from '../components/ui/checkbox';
import { ArrowLeft, FileText, Video, ExternalLink } from 'lucide-react';
import { toast } from 'sonner';

const getYouTubeEmbedUrl = (url) => {
  if (!url) return null;
  let videoId = null;
  try {
    const parsed = new URL(url);
    if (parsed.hostname.includes('youtube.com')) {
      videoId = parsed.searchParams.get('v');
    } else if (parsed.hostname === 'youtu.be') {
      videoId = parsed.pathname.slice(1);
    }
  } catch { return null; }
  return videoId ? `https://www.youtube.com/embed/${videoId}` : null;
};

const ModulePlayerPage = () => {
  const { courseId, moduleId } = useParams();
  const [modules, setModules] = useState([]);
  const [currentModule, setCurrentModule] = useState(null);
  const [isCompleted, setIsCompleted] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    loadModuleData();
  }, [moduleId]);

  const loadModuleData = async () => {
    try {
      const [modulesRes, progressRes] = await Promise.all([
        getCourseModules(courseId),
        getUserProgress()
      ]);
      setModules(modulesRes.data);
      const module = modulesRes.data.find(m => m.id === moduleId);
      setCurrentModule(module);
      const progressItem = progressRes.data.find(p => p.module_id === moduleId);
      setIsCompleted(progressItem?.completed || false);
    } catch (error) {
      console.error('Failed to load module:', error);
    }
  };

  const handleToggleComplete = async () => {
    try {
      await updateProgress({ module_id: moduleId, completed: !isCompleted });
      setIsCompleted(!isCompleted);
      toast.success(isCompleted ? 'Marked as incomplete' : 'Marked as complete!');
    } catch (error) {
      toast.error('Failed to update progress');
    }
  };

  const goToNextModule = () => {
    const currentIndex = modules.findIndex(m => m.id === moduleId);
    if (currentIndex < modules.length - 1) {
      navigate(`/course/${courseId}/module/${modules[currentIndex + 1].id}`);
    } else {
      navigate(`/course/${courseId}`);
    }
  };

  if (!currentModule) {
    return <div className="min-h-screen bg-[#1A1A1A] flex items-center justify-center"><div className="text-[#FF7F00]">Loading...</div></div>;
  }

  const embedUrl = getYouTubeEmbedUrl(currentModule.video_link);

  return (
    <div className="min-h-screen bg-[#1A1A1A]">
      <div className="max-w-6xl mx-auto px-6 py-12">
        <Link to={`/course/${courseId}`}>
          <Button variant="ghost" className="mb-8 text-gray-400 hover:text-[#FF7F00]" data-testid="back-course-button">
            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Course
          </Button>
        </Link>

        <div className="mb-6">
          <h1 className="text-4xl font-bold mb-2" data-testid="module-title">{currentModule.title}</h1>
          {currentModule.duration && (
            <p className="text-gray-400 text-sm">Duration: {currentModule.duration}</p>
          )}
        </div>

        {/* Video Section */}
        {currentModule.video_link && (
          <div className="mb-6">
            {embedUrl ? (
              <div className="aspect-video rounded-xl overflow-hidden bg-black" data-testid="video-embed">
                <iframe
                  src={embedUrl}
                  title={currentModule.title}
                  className="w-full h-full"
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                  allowFullScreen
                />
              </div>
            ) : (
              <Card className="bg-[#000000] border-[#333333]">
                <CardContent className="p-8 text-center">
                  <Video className="h-12 w-12 text-[#FF7F00] mx-auto mb-3" />
                  <a href={currentModule.video_link} target="_blank" rel="noopener noreferrer" className="text-[#FF7F00] hover:underline text-lg" data-testid="video-link">
                    Open Video
                  </a>
                </CardContent>
              </Card>
            )}
            <div className="mt-2 flex justify-end">
              <a href={currentModule.video_link} target="_blank" rel="noopener noreferrer" className="text-sm text-gray-500 hover:text-[#FF7F00] flex items-center gap-1 transition-colors" data-testid="open-youtube-link">
                <ExternalLink className="h-3.5 w-3.5" /> Open in YouTube
              </a>
            </div>
          </div>
        )}

        {/* PDF Notes */}
        {currentModule.pdf_link && (
          <Card className="bg-[#000000] border-[#333333] mb-6" data-testid="pdf-section">
            <CardContent className="p-5 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <FileText className="h-6 w-6 text-[#FF7F00]" />
                <span className="text-lg font-medium">Module Notes</span>
              </div>
              <a href={currentModule.pdf_link} target="_blank" rel="noopener noreferrer" data-testid="pdf-link">
                <Button className="bg-[#FF7F00] text-black hover:bg-[#E67300] gap-2">
                  <FileText className="h-4 w-4" /> Open PDF
                </Button>
              </a>
            </CardContent>
          </Card>
        )}

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Checkbox 
              checked={isCompleted} 
              onCheckedChange={handleToggleComplete}
              id="complete-checkbox"
              data-testid="complete-checkbox"
            />
            <label htmlFor="complete-checkbox" className="text-lg cursor-pointer">
              {isCompleted ? 'Completed' : 'Mark as complete'}
            </label>
          </div>
          <Button onClick={goToNextModule} className="bg-[#FF7F00] text-black hover:bg-[#E67300]" data-testid="next-module-button">
            Next Module
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ModulePlayerPage;

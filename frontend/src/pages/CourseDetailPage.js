import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getCourse, getCourseModules, getUserProgress } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { ArrowLeft, PlayCircle, CheckCircle, Circle, Clock, Lock, FileText } from 'lucide-react';
import { toast } from 'sonner';

const CourseDetailPage = () => {
  const { courseId } = useParams();
  const { user } = useAuth();
  const [course, setCourse] = useState(null);
  const [modules, setModules] = useState([]);
  const [progress, setProgress] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    loadCourseData();
  }, [courseId]);

  const loadCourseData = async () => {
    try {
      const [courseRes, modulesRes] = await Promise.all([
        getCourse(courseId),
        getCourseModules(courseId)
      ]);
      setCourse(courseRes.data);
      setModules(modulesRes.data);

      // Only fetch progress if logged in
      if (user) {
        try {
          const progressRes = await getUserProgress();
          setProgress(progressRes.data);
        } catch {
          // Ignore progress errors for public viewing
        }
      }
    } catch (error) {
      console.error('Failed to load course:', error);
      if (error.response?.status === 403) {
        toast.error('You need mentorship access to view this course');
        navigate(user ? '/dashboard' : '/signup');
      }
    }
  };

  const isModuleCompleted = (moduleId) => {
    return progress.some(p => p.module_id === moduleId && p.completed);
  };

  const handleModuleClick = (moduleId) => {
    if (!user) {
      toast.info('Sign up to access course modules');
      navigate('/signup');
    } else {
      navigate(`/course/${courseId}/module/${moduleId}`);
    }
  };

  if (!course) {
    return <div className="min-h-screen bg-[#1A1A1A] flex items-center justify-center"><div className="text-[#FF7F00]">Loading...</div></div>;
  }

  return (
    <div className="min-h-screen bg-[#1A1A1A]">
      <div className="max-w-5xl mx-auto px-6 py-12">
        <Link to={user ? '/dashboard' : '/courses'}>
          <Button variant="ghost" className="mb-8 text-gray-400 hover:text-[#FF7F00]" data-testid="back-button">
            <ArrowLeft className="mr-2 h-4 w-4" /> {user ? 'Back to Dashboard' : 'Back to Courses'}
          </Button>
        </Link>

        <div className="mb-12">
          <h1 className="text-5xl font-bold mb-4" data-testid="course-title">{course.title}</h1>
          <p className="text-gray-300 text-lg mb-6">{course.description}</p>
          <div className="bg-[#252525] border border-[#333333] rounded-lg p-6">
            <h3 className="text-xl font-semibold mb-3 text-[#FF7F00]">Course Outline</h3>
            <p className="text-gray-300">{course.outline}</p>
          </div>
        </div>

        {course.course_type === 'mentorship' && (
          <div className="mb-8">
            <Link to="/coach">
              <Button className="bg-[#FF7F00] text-black hover:bg-[#E67300]" data-testid="meet-coach-button">
                Meet Your Coach
              </Button>
            </Link>
          </div>
        )}

        <div>
          <h2 className="text-3xl font-semibold mb-6">Modules</h2>
          <div className="space-y-4">
            {modules.map((module, index) => (
              <Card 
                key={module.id} 
                className="bg-[#000000] border-[#333333] hover:border-[#FF7F00]/50 transition-all cursor-pointer"
                onClick={() => handleModuleClick(module.id)}
                data-testid={`module-card-${module.id}`}
              >
                <CardContent className="p-6 flex items-center gap-4">
                  <div className="flex-shrink-0">
                    {user ? (
                      isModuleCompleted(module.id) ? (
                        <CheckCircle className="h-6 w-6 text-green-500" />
                      ) : (
                        <Circle className="h-6 w-6 text-gray-600" />
                      )
                    ) : (
                      <Lock className="h-5 w-5 text-gray-600" />
                    )}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold mb-1">{index + 1}. {module.title}</h3>
                    {module.duration && (
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <Clock className="h-4 w-4" />
                        {module.duration}
                      </div>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    {user && module.pdf_link && (
                      <a
                        href={module.pdf_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        data-testid={`notes-btn-${module.id}`}
                      >
                        <Button size="sm" variant="outline" className="border-[#FF7F00] text-[#FF7F00] hover:bg-[#FF7F00]/10 gap-1.5">
                          <FileText className="h-4 w-4" /> Notes
                        </Button>
                      </a>
                    )}
                    {user ? (
                      <PlayCircle className="h-8 w-8 text-[#FF7F00]" />
                    ) : (
                      <span className="text-xs text-gray-500">Sign up to access</span>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {!user && (
          <div className="mt-10 text-center">
            <p className="text-gray-400 mb-4">Sign up to access all course modules and track your progress</p>
            <Link to="/signup">
              <Button className="bg-[#FF7F00] text-black hover:bg-[#E67300] px-8 py-5 text-lg" data-testid="signup-cta-button">
                Sign Up Now
              </Button>
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default CourseDetailPage;

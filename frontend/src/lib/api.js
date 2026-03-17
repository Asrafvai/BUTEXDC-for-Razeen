import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL + '/api';

export const api = axios.create({
  baseURL: API_URL,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const signup = (data) => api.post('/auth/signup', data);
export const login = (data) => api.post('/auth/login', data);
export const getMe = () => api.get('/auth/me');

// System setup
export const checkSetupStatus = () => api.get('/setup/status');
export const initializeSystem = (data) => api.post('/setup/initialize', data);

// Users
export const getAllUsers = (params) => api.get('/admin/users', { params });
export const approveUser = (userId) => api.patch(`/admin/users/${userId}/approve`);
export const toggleMentorship = (userId, grant) => api.patch(`/admin/users/${userId}/mentorship`, null, { params: { grant } });
export const archiveUser = (userId) => api.patch(`/admin/users/${userId}/archive`);

// Leadership
export const getLeadership = () => api.get('/leadership');
export const createLeadershipMember = (data) => api.post('/admin/leadership', data);
export const updateLeadershipMember = (memberId, data) => api.put(`/admin/leadership/${memberId}`, data);
export const archiveLeadershipMember = (memberId) => api.patch(`/admin/leadership/${memberId}/archive`);
export const reorderLeadership = (order) => api.post('/admin/leadership/reorder', order);

// Courses
export const getCourses = () => api.get('/courses');
export const getCourse = (courseId) => api.get(`/courses/${courseId}`);
export const createCourse = (data) => api.post('/admin/courses', data);
export const updateCourse = (courseId, data) => api.put(`/admin/courses/${courseId}`, data);
export const archiveCourse = (courseId) => api.patch(`/admin/courses/${courseId}/archive`);

// Modules
export const getCourseModules = (courseId) => api.get(`/courses/${courseId}/modules`);
export const createModule = (data) => api.post('/admin/modules', data);
export const updateModule = (moduleId, data) => api.put(`/admin/modules/${moduleId}`, data);
export const archiveModule = (moduleId) => api.patch(`/admin/modules/${moduleId}/archive`);
export const reorderModules = (order) => api.post('/admin/modules/reorder', order);

// Progress
export const getUserProgress = () => api.get('/progress');
export const updateProgress = (data) => api.post('/progress', data);

// Announcements
export const getAnnouncements = () => api.get('/announcements');
export const createAnnouncement = (data) => api.post('/admin/announcements', data);
export const updateAnnouncement = (announcementId, data) => api.put(`/admin/announcements/${announcementId}`, data);
export const archiveAnnouncement = (announcementId) => api.patch(`/admin/announcements/${announcementId}/archive`);

// Success Events
export const getSuccessEvents = () => api.get('/success-events');
export const createSuccessEvent = (data) => api.post('/admin/success-events', data);
export const updateSuccessEvent = (eventId, data) => api.put(`/admin/success-events/${eventId}`, data);
export const archiveSuccessEvent = (eventId) => api.patch(`/admin/success-events/${eventId}/archive`);

// Homepage Content
export const getHomepageContent = () => api.get('/homepage-content');
export const updateHomepageContent = (data) => api.put('/admin/homepage-content', data);

// Coach Info
export const getCoachInfo = () => api.get('/coach-info');
export const updateCoachInfo = (data) => api.put('/admin/coach-info', data);

// Analytics
export const getAnalytics = () => api.get('/admin/analytics');

// Image Upload
export const uploadImage = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/admin/upload-image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// Alumni
export const getAlumni = () => api.get('/alumni');
export const createAlumni = (data) => api.post('/admin/alumni', data);
export const updateAlumni = (alumniId, data) => api.put(`/admin/alumni/${alumniId}`, data);
export const archiveAlumni = (alumniId) => api.patch(`/admin/alumni/${alumniId}/archive`);

// Events
export const getEvents = () => api.get('/events');
export const createEvent = (data) => api.post('/admin/events', data);
export const updateEvent = (eventId, data) => api.put(`/admin/events/${eventId}`, data);
export const archiveEvent = (eventId) => api.patch(`/admin/events/${eventId}/archive`);

// Membership
export const getMembershipContent = () => api.get('/membership-content');
export const updateMembershipContent = (data) => api.put('/admin/membership-content', data);

// Advanced Course Access
export const toggleAdvancedAccess = (userId, grant) => api.patch(`/admin/users/${userId}/advanced`, null, { params: { grant } });


// Flagship Events
export const getFlagshipEvents = () => api.get('/flagship-events');
export const getActiveFlagshipEvents = () => api.get('/flagship-events/active');
export const getFlagshipEvent = (eventId) => api.get(`/flagship-events/${eventId}`);
export const createFlagshipEvent = (data) => api.post('/admin/flagship-events', data);
export const updateFlagshipEvent = (eventId, data) => api.put(`/admin/flagship-events/${eventId}`, data);
export const archiveFlagshipEvent = (eventId) => api.patch(`/admin/flagship-events/${eventId}/archive`);
export const toggleFlagshipEvent = (eventId) => api.patch(`/admin/flagship-events/${eventId}/toggle`);
export const getFlagshipAnnouncements = (eventId) => api.get(`/flagship-events/${eventId}/announcements`);
export const createFlagshipAnnouncement = (eventId, data) => api.post(`/admin/flagship-events/${eventId}/announcements`, data);
export const updateFlagshipAnnouncement = (annId, data) => api.put(`/admin/flagship-announcements/${annId}`, data);
export const archiveFlagshipAnnouncement = (annId) => api.patch(`/admin/flagship-announcements/${annId}/archive`);
